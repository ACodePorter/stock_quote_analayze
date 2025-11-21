from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
import akshare as ak
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from fastapi import Depends
import traceback
import numpy as np
import time
from threading import Lock
import datetime
import pandas as pd
import math
from models import StockRealtimeQuote, StockBasicInfo, StockRealtimeQuoteHK, StockBasicInfoHK

# 简单内存缓存实现,缓存600秒。
class DataFrameCache:
    def __init__(self, expire_seconds=600):
        self.data = None
        self.timestamp = 0
        self.expire = expire_seconds
        self.lock = Lock()
    def get(self):
        with self.lock:
            if self.data is not None and (time.time() - self.timestamp) < self.expire:
                return self.data
            return None
    def set(self, df):
        with self.lock:
            self.data = df
            self.timestamp = time.time()

# 创建一个全局缓存实例
stock_spot_cache = DataFrameCache(expire_seconds=600)

router = APIRouter(prefix="/api/stock", tags=["stock"])

def is_hk_stock(code: str, db: Session) -> bool:
    """
    判断股票代码是否为港股
    先查询 stock_basic_info_hk 表，如果不存在，再查询 stock_basic_info 表
    
    Args:
        code: 股票代码
        db: 数据库会话
        
    Returns:
        bool: True表示港股，False表示A股
    """
    if not code:
        return False
    
    code_str = str(code).strip()
    
    # 先查询港股表
    hk_stock = db.query(StockBasicInfoHK).filter(StockBasicInfoHK.code == code_str).first()
    if hk_stock:
        return True
    
    # 再查询A股表
    a_stock = db.query(StockBasicInfo).filter(StockBasicInfo.code == code_str).first()
    if a_stock:
        return False
    
    # 如果两个表都没有，默认返回False（A股）
    return False

def safe_float(value):
    try:
        if value in [None, '', '-']:
            return None
        return float(value)
    except (ValueError, TypeError):
        return None

def normalize_code(raw_code: str):
    if raw_code is None:
        return None
    code = str(raw_code).strip()
    if '.' in code:
        code = code.split('.')[0]
    return code

def get_cached_spot_df():
    try:
        df = stock_spot_cache.get()
        if df is None:
            df = ak.stock_zh_a_spot_em()
            if df is not None:
                stock_spot_cache.set(df)
        if df is not None and hasattr(df, 'copy'):
            return df.copy()
    except Exception as e:
        print(f"⚠️ 获取AkShare行情失败: {e}")
    return None

def prepare_spot_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    rename_map = {
        '代码': 'code',
        '名称': 'name',
        '最新价': 'current',
        '涨跌额': 'change',
        '涨跌幅': 'change_percent',
        '成交量': 'volume',
        '成交额': 'turnover',
        '换手率': 'rate',
    }
    available_cols = [col for col in rename_map.keys() if col in df.columns]
    if not available_cols:
        return pd.DataFrame()
    df_prepared = df[available_cols].rename(columns=rename_map)
    df_prepared['code'] = df_prepared['code'].apply(normalize_code)
    
    def to_float(series):
        return pd.to_numeric(series, errors='coerce')
    
    df_prepared['current'] = to_float(df_prepared.get('current'))
    df_prepared['change'] = to_float(df_prepared.get('change'))
    df_prepared['change_percent'] = pd.to_numeric(
        df_prepared.get('change_percent', '').astype(str).str.replace('%', ''), errors='coerce'
    )
    df_prepared['volume'] = to_float(df_prepared.get('volume'))
    df_prepared['turnover'] = to_float(df_prepared.get('turnover'))
    df_prepared['rate'] = pd.to_numeric(
        df_prepared.get('rate', '').astype(str).str.replace('%', ''), errors='coerce'
    )
    
    for col in ['open', 'pre_close', 'high', 'low', 'pe_dynamic', 'pb', 'market_cap', 'circulating_market_cap']:
        if col not in df_prepared.columns:
            df_prepared[col] = None
    return df_prepared

@router.post("/quote")
async def get_stock_quote(request: Request):
    """
    批量获取股票实时行情
    前端应POST {"codes": ["000001", "600519", ...]}
    """
    try:
        data = await request.json()
        print(f"[stock_quote] 收到请求数据: {data}")
        codes = data.get("codes", [])
        if not codes:
            print("[stock_quote] 缺少股票代码")
            return JSONResponse({"success": False, "message": "缺少股票代码"}, status_code=400)
        result = []
        today = datetime.date.today()
        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        today_pattern = f"{today_str}%"

        db_session_gen = get_db()
        db = next(db_session_gen)
        try:
            # 1. 先查询A股表
            quotes_today_a = db.query(StockRealtimeQuote).filter(
                StockRealtimeQuote.code.in_(codes),
                StockRealtimeQuote.trade_date.like(today_pattern)
            ).all()
            quote_map_a = {q.code: q for q in quotes_today_a}

            # 2. 查询港股表
            quotes_today_hk = db.query(StockRealtimeQuoteHK).filter(
                StockRealtimeQuoteHK.code.in_(codes),
                StockRealtimeQuoteHK.trade_date.like(today_pattern)
            ).all()
            quote_map_hk = {q.code: q for q in quotes_today_hk}

            remaining_codes = []
            for code in codes:
                # 优先使用A股数据
                stock_quote = quote_map_a.get(code)
                if stock_quote:
                    result.append({
                        "code": stock_quote.code,
                        "current_price": safe_float(stock_quote.current_price),
                        "change_percent": safe_float(stock_quote.change_percent),
                        "volume": safe_float(stock_quote.volume),
                        "turnover": safe_float(stock_quote.amount),
                        "high": safe_float(stock_quote.high),
                        "low": safe_float(stock_quote.low),
                        "open": safe_float(stock_quote.open),
                        "pre_close": safe_float(stock_quote.pre_close),
                    })
                else:
                    # A股没有，尝试港股
                    stock_quote_hk = quote_map_hk.get(code)
                    if stock_quote_hk:
                        result.append({
                            "code": stock_quote_hk.code,
                            "current_price": safe_float(stock_quote_hk.current_price),
                            "change_percent": safe_float(stock_quote_hk.change_percent),
                            "volume": safe_float(stock_quote_hk.volume),
                            "turnover": safe_float(stock_quote_hk.amount),
                            "high": safe_float(stock_quote_hk.high),
                            "low": safe_float(stock_quote_hk.low),
                            "open": safe_float(stock_quote_hk.open),
                            "pre_close": safe_float(stock_quote_hk.pre_close),
                        })
                    else:
                        remaining_codes.append(code)

            api_failed_codes = []
            if remaining_codes and today.weekday() not in (5, 6):
                for code in remaining_codes:
                    try:
                        df = ak.stock_bid_ask_em(symbol=code)
                        if df is None or df.empty:
                            api_failed_codes.append(code)
                            continue
                        data_dict = dict(zip(df['item'], df['value']))
                        api_result = {
                            "code": code,
                            "current_price": safe_float(data_dict.get("最新")),
                            "change_amount": safe_float(data_dict.get("涨跌")),
                            "change_percent": safe_float(data_dict.get("涨幅")),
                            "open": safe_float(data_dict.get("今开")),
                            "pre_close": safe_float(data_dict.get("昨收")),
                            "high": safe_float(data_dict.get("最高")),
                            "low": safe_float(data_dict.get("最低")),
                            "volume": safe_float(data_dict.get("总手")),
                            "turnover": safe_float(data_dict.get("金额")),
                        }
                        result.append(api_result)

                        # 更新数据库，确保下次直接命中
                        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        # 先查询是否已存在
                        existing_quote = db.query(StockRealtimeQuote).filter(
                            StockRealtimeQuote.code == code,
                            StockRealtimeQuote.trade_date == now_str
                        ).first()
                        
                        if existing_quote:
                            # 更新现有记录
                            existing_quote.name = None
                            existing_quote.current_price = api_result["current_price"]
                            existing_quote.change_percent = api_result["change_percent"]
                            existing_quote.volume = api_result["volume"]
                            existing_quote.amount = api_result["turnover"]
                            existing_quote.high = api_result["high"]
                            existing_quote.low = api_result["low"]
                            existing_quote.open = api_result["open"]
                            existing_quote.pre_close = api_result["pre_close"]
                            existing_quote.turnover_rate = None
                            existing_quote.pe_dynamic = None
                            existing_quote.total_market_value = None
                            existing_quote.pb_ratio = None
                            existing_quote.circulating_market_value = None
                            existing_quote.update_time = datetime.datetime.now()
                        else:
                            # 插入新记录
                            db.add(StockRealtimeQuote(
                                code=code,
                                trade_date=now_str,
                                name=None,
                                current_price=api_result["current_price"],
                                change_percent=api_result["change_percent"],
                                volume=api_result["volume"],
                                amount=api_result["turnover"],
                                high=api_result["high"],
                                low=api_result["low"],
                                open=api_result["open"],
                                pre_close=api_result["pre_close"],
                                turnover_rate=None,
                                pe_dynamic=None,
                                total_market_value=None,
                                pb_ratio=None,
                                circulating_market_value=None,
                                update_time=datetime.datetime.now()
                            ))
                    except Exception as e:
                        print(f"[stock_quote] 获取 {code} 行情异常: {e}")
                        api_failed_codes.append(code)
                try:
                    db.commit()
                except Exception as commit_err:
                    db.rollback()
                    print(f"[stock_quote] 更新数据库失败: {commit_err}")
            else:
                api_failed_codes = remaining_codes.copy()

            # 对于仍未获取成功的代码，从数据库取最近一次记录
            if api_failed_codes:
                for code in api_failed_codes:
                    # 先查A股表
                    stock_quote = db.query(StockRealtimeQuote).filter(
                        StockRealtimeQuote.code == code
                    ).order_by(StockRealtimeQuote.trade_date.desc()).first()
                    if stock_quote:
                        result.append({
                            "code": stock_quote.code,
                            "current_price": safe_float(stock_quote.current_price),
                            "change_percent": safe_float(stock_quote.change_percent),
                            "volume": safe_float(stock_quote.volume),
                            "turnover": safe_float(stock_quote.amount),
                            "high": safe_float(stock_quote.high),
                            "low": safe_float(stock_quote.low),
                            "open": safe_float(stock_quote.open),
                            "pre_close": safe_float(stock_quote.pre_close),
                        })
                    else:
                        # A股没有，查港股表
                        stock_quote_hk = db.query(StockRealtimeQuoteHK).filter(
                            StockRealtimeQuoteHK.code == code
                        ).order_by(StockRealtimeQuoteHK.trade_date.desc()).first()
                        if stock_quote_hk:
                            result.append({
                                "code": stock_quote_hk.code,
                                "current_price": safe_float(stock_quote_hk.current_price),
                                "change_percent": safe_float(stock_quote_hk.change_percent),
                                "volume": safe_float(stock_quote_hk.volume),
                                "turnover": safe_float(stock_quote_hk.amount),
                                "high": safe_float(stock_quote_hk.high),
                                "low": safe_float(stock_quote_hk.low),
                                "open": safe_float(stock_quote_hk.open),
                                "pre_close": safe_float(stock_quote_hk.pre_close),
                            })
        finally:
            db.close()
        print(f"[stock_quote] 返回数据: {result}")
        return JSONResponse({"success": True, "data": result})
    except Exception as e:
        print(f"[stock_quote] 异常: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

# 获取所有股票基本信息（用于前端全局缓存）
@router.get("/basic-info/all")
async def get_all_stocks_basic_info(db: Session = Depends(get_db)):
    """获取所有股票的基本信息（代码和名称），用于前端登录后全局缓存"""
    print(f"[stock_basic_info_all] 收到请求: 获取所有股票信息")
    try:
        from models import StockBasicInfo
        stocks = db.query(StockBasicInfo).all()
        result = [{'code': str(s.code), 'name': s.name} for s in stocks]
        print(f"[stock_basic_info_all] 返回数据: 共{len(result)}条股票信息")
        return JSONResponse({'success': True, 'data': result, 'total': len(result)})
    except Exception as e:
        print(f"[stock_basic_info_all] 查询异常: {e}\n{traceback.format_exc()}")
        return JSONResponse({'success': False, 'message': str(e)}, status_code=500)

# 获取股票列表（支持A股和港股）
@router.get("/list")
async def get_stocks_list(request: Request, db: Session = Depends(get_db)):
    query = request.query_params.get('query', '').strip()
    limit = int(request.query_params.get('limit', 15))
    print(f"[stock_list] 收到请求: query={query}, limit={limit}")
    try:
        from models import StockBasicInfo, StockBasicInfoHK, StockRealtimeQuoteHK
        result = []
        seen_codes = set()  # 用于去重
        
        # 1. 先查询A股基础信息表
        q_a = db.query(StockBasicInfo)
        if query:
            q_a = q_a.filter(
                (StockBasicInfo.code.like(f"%{query}%")) |
                (StockBasicInfo.name.like(f"%{query}%"))
            )
        stocks_a = q_a.limit(limit).all()
        for s in stocks_a:
            code_str = str(s.code)
            if code_str not in seen_codes:
                result.append({'code': code_str, 'name': s.name})
                seen_codes.add(code_str)
        
        # 2. 如果A股结果不足，查询港股基础信息表
        if len(result) < limit:
            remaining_limit = limit - len(result)
            try:
                q_hk = db.query(StockBasicInfoHK)
                if query:
                    q_hk = q_hk.filter(
                        (StockBasicInfoHK.code.like(f"%{query}%")) |
                        (StockBasicInfoHK.name.like(f"%{query}%"))
                    )
                stocks_hk = q_hk.limit(remaining_limit).all()
                for s in stocks_hk:
                    code_str = str(s.code)
                    if code_str not in seen_codes:
                        result.append({'code': code_str, 'name': s.name})
                        seen_codes.add(code_str)
            except Exception as e_hk:
                print(f"[stock_list] 查询港股基础信息表失败: {e_hk}")
        
        # 3. 如果结果仍不足，从港股实时行情表查询（作为后备）
        if len(result) < limit:
            remaining_limit = limit - len(result)
            try:
                # 获取最新交易日期
                latest_date = db.query(func.max(StockRealtimeQuoteHK.trade_date)).scalar()
                if latest_date:
                    q_hk_quote = db.query(StockRealtimeQuoteHK.code, StockRealtimeQuoteHK.name).filter(
                        StockRealtimeQuoteHK.trade_date == latest_date
                    )
                    if query:
                        q_hk_quote = q_hk_quote.filter(
                            (StockRealtimeQuoteHK.code.like(f"%{query}%")) |
                            (StockRealtimeQuoteHK.name.like(f"%{query}%")) |
                            (StockRealtimeQuoteHK.english_name.like(f"%{query}%"))
                        )
                    stocks_hk_quote = q_hk_quote.distinct().limit(remaining_limit).all()
                    for row in stocks_hk_quote:
                        code_str = str(row.code)
                        if code_str not in seen_codes:
                            result.append({'code': code_str, 'name': row.name or code_str})
                            seen_codes.add(code_str)
            except Exception as e_hk_quote:
                print(f"[stock_list] 查询港股实时行情表失败: {e_hk_quote}")
        
        print(f"[stock_list] 返回数据: {result}, 总数: {len(result)}")
        return JSONResponse({'success': True, 'data': result, 'total': len(result)})
    except Exception as e:
        print(f"[stock_list] 查询异常: {e}\n{traceback.format_exc()}")
        return JSONResponse({'success': False, 'message': str(e)}, status_code=500)


@router.get("/quote_board")
async def get_quote_board(limit: int = Query(10, description="返回前N个涨幅最高的股票")):
    """获取沪深京A股最新行情，返回涨幅最高的前limit个股票（始终从stock_realtime_quote表读取，不联表）"""
    try:
        # 获取最新交易日期的实时行情数据
        db = next(get_db())
        
        # 首先获取最新的交易日期
        latest_date_result = pd.read_sql_query("""
            SELECT MAX(trade_date) as latest_date 
            FROM stock_realtime_quote 
            WHERE change_percent IS NOT NULL AND change_percent != 0
        """, db.bind)
        
        if latest_date_result.empty or latest_date_result.iloc[0]['latest_date'] is None:
            db.close()
            return JSONResponse({'success': False, 'message': '暂无行情数据'}, status_code=404)
        
        latest_trade_date = latest_date_result.iloc[0]['latest_date']
        print(f"📅 首页涨幅榜使用最新交易日期: {latest_trade_date}")
        
        # 获取最新交易日期的数据
        df = pd.read_sql_query(f"""
            SELECT * FROM stock_realtime_quote 
            WHERE change_percent IS NOT NULL AND change_percent != 0 AND trade_date = '{latest_trade_date}'
            ORDER BY code
        """, db.bind)
        
        # 按涨幅降序排列
        df = df.sort_values(by='change_percent', ascending=False)
        
        # 取前limit个
        df_limit = df.head(limit)
        
        # 准备名称映射，避免名称字段为空
        name_map = {}
        if not df_limit.empty:
            code_list = [str(code) for code in df_limit['code'].tolist() if code]
            if code_list:
                name_rows = db.query(StockBasicInfo.code, StockBasicInfo.name).filter(
                    StockBasicInfo.code.in_(code_list)
                ).all()
                name_map = {str(row.code): row.name for row in name_rows if row.name}
        
        data = []
        for _, row in df_limit.iterrows():
            code = str(row['code'])
            display_name = row['name']
            if not display_name or str(display_name).lower() == 'null':
                display_name = name_map.get(code) or ''
            data.append({
                'code': code,
                'name': display_name,
                'current': row['current_price'],
                'change_percent': row['change_percent'],
                'open': row['open'],
                'pre_close': row['pre_close'],
                'high': row['high'],
                'low': row['low'],
                'volume': row['volume'],
                'turnover': row['amount'],
            })
        print(f"✅(DB) 成功获取 {len(data)} 条A股涨幅榜数据（已去重）")
        db.close()
        return JSONResponse({'success': True, 'data': data})
    except Exception as e:
        print(f"❌ 获取A股涨幅榜数据失败: {str(e)}")
        tb = traceback.format_exc()
        print(tb)
        return JSONResponse({'success': False, 'message': '获取A股涨幅榜数据失败', 'error': str(e), 'traceback': tb}, status_code=500)
    
# 获取A股最新行情排行
@router.get("/quote_board_list")
def get_quote_board_list(
    ranking_type: str = Query('rise', description="排行类型: rise(涨幅榜), fall(跌幅榜), volume(成交量榜), turnover_rate(换手率榜)"),
    market: str = Query('all', description="市场类型: all(全部市场), sh(上交所), sz(深交所), bj(北交所), cy(创业板)"),
    page: int = Query(1, description="页码，从1开始"),
    page_size: int = Query(20, description="每页条数，默认20"),
    keyword: str = Query(None, description="搜索关键词（股票代码或名称）")
):
    """
    获取A股最新行情，支持多种排行类型、市场过滤和分页 (数据源: stock_realtime_quote)
    """
    try:
        print(f"📊 获取A股行情排行 (from DB): type={ranking_type}, market={market}, page={page}, page_size={page_size}, keyword={keyword}")
        
        # 1. 获取最新交易日期的实时行情数据
        db = next(get_db())
        
        try:
            latest_date_result = pd.read_sql_query("""
                SELECT MAX(trade_date) as latest_date 
                FROM stock_realtime_quote 
                WHERE change_percent IS NOT NULL
            """, db.bind)
            
            if latest_date_result.empty or latest_date_result.iloc[0]['latest_date'] is None:
                latest_trade_date = None
                df = pd.DataFrame()
            else:
                latest_trade_date = latest_date_result.iloc[0]['latest_date']
                if latest_trade_date is not None and len(str(latest_trade_date)) > 10:
                    latest_trade_date = str(latest_trade_date)[:10]
                print(f"📅 使用最新交易日期: {latest_trade_date}")
              
                # 构建查询SQL - 使用text()包装SQL语句
                if keyword and keyword.strip():
                    keyword_clean = keyword.strip().replace("'", "''")  # 防止SQL注入
                    sql_query = text(f"""
                        SELECT * FROM stock_realtime_quote 
                        WHERE change_percent IS NOT NULL AND trade_date = '{latest_trade_date}'
                        AND (code LIKE '%{keyword_clean}%' OR name LIKE '%{keyword_clean}%')
                        ORDER BY code
                    """)
                else:
                    sql_query = text(f"""
                        SELECT * FROM stock_realtime_quote 
                        WHERE change_percent IS NOT NULL AND trade_date = '{latest_trade_date}'
                        ORDER BY code
                    """)
                
                df = pd.read_sql_query(sql_query, db.bind)
        finally:
            db.close()

        # 3. 市场类型过滤
        if market != 'all':
            if market == 'sh':
                df = df[df['code'].str.startswith('6')]
            elif market == 'sz':
                df = df[df['code'].str.startswith('0') | df['code'].str.startswith('3')] # 深市包含主板和创业板
            elif market == 'cy':
                df = df[df['code'].str.startswith('3')]
            elif market == 'bj':
                df = df[df['code'].str.startswith('8') | df['code'].str.startswith('4')] # 北交所
        
        # 4. 排行类型排序
        sort_column_map = {
            'rise': ('change_percent', False),
            'fall': ('change_percent', True),
            'volume': ('volume', False),
            'turnover_rate': ('turnover_rate', False)
        }
        
        if ranking_type in sort_column_map:
            col, ascending = sort_column_map[ranking_type]
            df = df.sort_values(by=col, ascending=ascending)
        else:
            return JSONResponse({'success': False, 'message': '无效的排行类型'}, status_code=400)

        # 5. 字段重命名和格式化
        df = df.replace({np.nan: None})
        
        # 确保数值字段的数据类型正确
        numeric_columns = ['current_price', 'change_percent', 'open', 'pre_close', 'high', 'low', 
                          'volume', 'amount', 'turnover_rate', 'pe_dynamic', 'pb_ratio', 
                          'total_market_value', 'circulating_market_value']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        field_rename_map = {
            'code': 'code',
            'name': 'name',
            'current_price': 'current',
            # 'change' is not in db, can be calculated if needed
            'change_percent': 'change_percent',
            'open': 'open',
            'pre_close': 'pre_close',
            'high': 'high',
            'low': 'low',
            'volume': 'volume',
            'amount': 'turnover',
            'turnover_rate': 'rate',
            'pe_dynamic': 'pe_dynamic',
            'pb_ratio': 'pb',
            'total_market_value': 'market_cap',
            'circulating_market_value': 'circulating_market_cap'
        }
        
        if df.empty:
            df_selected = pd.DataFrame(columns=field_rename_map.values())
        else:
            df_selected = df[list(field_rename_map.keys())].rename(columns=field_rename_map)

        # Calculate 'change' if possible
        if not df_selected.empty and 'current' in df_selected.columns and 'pre_close' in df_selected.columns:
            # 确保数据类型为数值型，处理可能的字符串或None值
            current_numeric = pd.to_numeric(df_selected['current'], errors='coerce')
            pre_close_numeric = pd.to_numeric(df_selected['pre_close'], errors='coerce')
            df_selected['change'] = (current_numeric - pre_close_numeric).round(2)
        else:
            df_selected['change'] = None

        total = len(df_selected)
        fallback_used = False
        if total < page_size:
            spot_df = get_cached_spot_df()
            df_from_spot = prepare_spot_dataframe(spot_df)
            if not df_from_spot.empty:
                df_selected = df_from_spot
                total = len(df_selected)
                fallback_used = True
                print(f"⚠️ 本地行情数据不足，使用AkShare行情填充，共 {total} 条")
                
                if market != 'all':
                    if market == 'sh':
                        df_selected = df_selected[df_selected['code'].str.startswith('6')]
                    elif market == 'sz':
                        df_selected = df_selected[df_selected['code'].str.startswith('0') | df_selected['code'].str.startswith('3')]
                    elif market == 'cy':
                        df_selected = df_selected[df_selected['code'].str.startswith('3')]
                    elif market == 'bj':
                        df_selected = df_selected[df_selected['code'].str.startswith('8') | df_selected['code'].str.startswith('4')]
                
                fallback_sort_map = {
                    'rise': ('change_percent', False),
                    'fall': ('change_percent', True),
                    'volume': ('volume', False),
                    'turnover_rate': ('rate', False)
                }
                sort_col, ascending = fallback_sort_map.get(ranking_type, ('change_percent', False))
                if sort_col in df_selected.columns:
                    df_selected = df_selected.sort_values(by=sort_col, ascending=ascending)
                total = len(df_selected)

        start = (page - 1) * page_size
        end = start + page_size
        df_page = df_selected.iloc[start:end].copy()
        
        # 名称兜底（仅对本地数据）
        if not fallback_used and not df_page.empty and 'code' in df_page.columns:
            code_list = [str(code) for code in df_page['code'].tolist() if code]
            if code_list:
                db_lookup = next(get_db())
                try:
                    name_rows = db_lookup.query(StockBasicInfo.code, StockBasicInfo.name).filter(
                        StockBasicInfo.code.in_(code_list)
                    ).all()
                finally:
                    db_lookup.close()
                name_map = {str(row.code): row.name for row in name_rows if row.name}
                def resolve_name(row):
                    current_name = row.get('name')
                    if current_name and str(current_name).strip().lower() != 'null':
                        return current_name
                    return name_map.get(str(row.get('code'))) or current_name or ''
                df_page['name'] = df_page.apply(resolve_name, axis=1)
        
        data = df_page.to_dict(orient='records')
        data = clean_nan(data)
        
        print(f"✅ 成功获取 {len(data)} 条A股排行数据 (总数: {total})")
        db.close()
        return JSONResponse({'success': True, 'data': data, 'total': total, 'page': page, 'page_size': page_size})
        
    except Exception as e:
        print(f"❌ 获取A股排行数据失败: {str(e)}")
        tb = traceback.format_exc()
        print(tb)
        return JSONResponse({'success': False, 'message': '获取A股排行数据失败', 'error': str(e), 'traceback': tb}, status_code=500)

# 根据股票代码获取实时行情
@router.get("/realtime_quote_by_code")
async def get_realtime_quote_by_code(code: str = Query(None, description="股票代码"), db: Session = Depends(get_db)):
    print(f"[realtime_quote_by_code] 输入参数: code={code}")
    if not code:
        print("[realtime_quote_by_code] 缺少参数")
        return JSONResponse({"success": False, "message": "缺少股票代码参数code"}, status_code=400)
    try:
        # 先判断股票类型
        if is_hk_stock(code, db):
            print(f"[realtime_quote_by_code] 检测到港股代码: {code}，调用港股接口")
            # 导入港股接口函数
            from stock.hk_stock_manage import get_hk_realtime_quote_by_code
            # 调用港股接口
            return await get_hk_realtime_quote_by_code(code, db)
        
        # A股逻辑继续
        # 优先从数据库获取市盈率等财务指标数据
        # 获取最新交易日期
        latest_date_result = pd.read_sql_query("""
            SELECT MAX(trade_date) as latest_date 
            FROM stock_realtime_quote 
            WHERE change_percent IS NOT NULL AND change_percent != 0
        """, db.bind)
        
        db_stock_data = None
        if not latest_date_result.empty and latest_date_result.iloc[0]['latest_date'] is not None:
            latest_trade_date = latest_date_result.iloc[0]['latest_date']
            db_stock_data = db.query(StockRealtimeQuote).filter(
                StockRealtimeQuote.code == code,
                StockRealtimeQuote.trade_date == latest_trade_date
            ).first()
        
        # 获取买卖盘数据
        try:
            df_bid_ask = ak.stock_bid_ask_em(symbol=code)
            if df_bid_ask.empty:
                print(f"[realtime_quote_by_code] 未找到股票代码: {code}")
                return JSONResponse({"success": False, "message": f"未找到股票代码: {code}"}, status_code=404)
        except Exception as e:
            print(f"[realtime_quote_by_code] 获取买卖盘数据失败: {e}")
            return JSONResponse({"success": False, "message": f"获取股票数据失败: {str(e)}"}, status_code=500)
        
        # 合并数据
        bid_ask_dict = dict(zip(df_bid_ask['item'], df_bid_ask['value']))
        
        def fmt(val):
            try:
                if val is None:
                    return None
                return f"{float(val):.2f}"
            except Exception:
                return None
        
        # 增加均价字段
        avg_price = None
        try:
            # 优先用akshare返回的均价字段
            avg_price = bid_ask_dict.get("均价") or bid_ask_dict.get("成交均价")
            if avg_price is None and bid_ask_dict.get("金额") and bid_ask_dict.get("总手") and float(bid_ask_dict.get("总手")) != 0:
                avg_price = float(bid_ask_dict.get("金额")) / float(bid_ask_dict.get("总手"))
        except Exception:
            avg_price = None
        
        # 优先从数据库获取市盈率数据，如果数据库没有则从akshare获取
        pe_dynamic = None
        if db_stock_data and db_stock_data.pe_dynamic is not None:
            # 从数据库获取市盈率
            pe_dynamic = fmt(db_stock_data.pe_dynamic)
            print(f"[realtime_quote_by_code] 从数据库获取市盈率: {pe_dynamic}")
        else:
            # 数据库没有市盈率数据，从akshare获取作为备选
            try:
                df_spot = ak.stock_zh_a_spot_em()
                stock_spot_data = df_spot[df_spot['代码'] == code]
                if not stock_spot_data.empty:
                    pe_dynamic = stock_spot_data.iloc[0]['市盈率-动态']
                    if pd.isna(pe_dynamic):
                        pe_dynamic = None
                    else:
                        pe_dynamic = fmt(pe_dynamic)
                    print(f"[realtime_quote_by_code] 从akshare获取市盈率: {pe_dynamic}")
            except Exception as e:
                print(f"[realtime_quote_by_code] 从akshare获取市盈率失败: {e}")
                pe_dynamic = None
        
        result = {
            "code": code,
            "current_price": fmt(bid_ask_dict.get("最新")),
            "change_amount": fmt(bid_ask_dict.get("涨跌")),
            "change_percent": fmt(bid_ask_dict.get("涨幅")),
            "open": fmt(bid_ask_dict.get("今开")),
            "pre_close": fmt(bid_ask_dict.get("昨收")),
            "high": fmt(bid_ask_dict.get("最高")),
            "low": fmt(bid_ask_dict.get("最低")),
            "volume": fmt(bid_ask_dict.get("总手")),
            "turnover": fmt(bid_ask_dict.get("金额")),
            "turnover_rate": fmt(bid_ask_dict.get("换手")),
            "pe_dynamic": pe_dynamic,
            "average_price": fmt(avg_price),
        }
        print(f"[realtime_quote_by_code] 输出数据: {result}")
        return JSONResponse({"success": True, "data": result})
    except Exception as e:
        print(f"[realtime_quote_by_code] 异常: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

# 股票类型判断接口
@router.get("/check_type")
async def check_stock_type(code: str = Query(None, description="股票代码"), db: Session = Depends(get_db)):
    """
    判断股票类型（A股或港股）
    
    Args:
        code: 股票代码
        
    Returns:
        {"success": True, "is_hk": True/False, "code": "股票代码"}
    """
    if not code:
        return JSONResponse({"success": False, "message": "缺少股票代码参数code"}, status_code=400)
    
    try:
        is_hk = is_hk_stock(code, db)
        return JSONResponse({
            "success": True,
            "is_hk": is_hk,
            "code": code
        })
    except Exception as e:
        print(f"[check_type] 异常: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

# 获取指定股票代码的当日分时数据（分时线），非交易日返回最近一个交易日的分钟数据
@router.get("/minute_data_by_code")
async def get_minute_data_by_code(code: str = Query(None, description="股票代码")):
    """
    获取指定股票代码的当日分时数据（分时线），非交易日返回最近一个交易日的分钟数据
    """
    print(f"[minute_data_by_code] 输入参数: code={code}")
    if not code:
        print(f"[minute_data_by_code] 缺少参数code")
        return JSONResponse({"success": False, "message": "缺少股票代码参数code"}, status_code=400)
    try:
        trade_dates = ak.tool_trade_date_hist_sina()['trade_date'].tolist()
        trade_dates_str = [d.strftime('%Y-%m-%d') for d in trade_dates]
        print(f"[minute_data_by_code] 交易日历: {trade_dates_str[:10]} ... 共{len(trade_dates_str)}天")
        today = datetime.date.today()
        today_str = today.strftime('%Y-%m-%d')
        # 如果今天不是交易日，则取最近一个交易日的分钟数据
        if today_str not in trade_dates_str:
            today = today - datetime.timedelta(days=1)
            today_str = today.strftime('%Y-%m-%d')
        is_trading_day = today_str in trade_dates_str
        print(f"[minute_data_by_code] 今日是否交易日: {is_trading_day}")
        result = []
        if is_trading_day:
            df = ak.stock_intraday_em(symbol=code)
            if df is None or df.empty:
                print(f"[minute_data_by_code] 未找到股票代码: {code}")
                return JSONResponse({"success": False, "message": f"未找到股票代码: {code}"}, status_code=404)
            for _, row in df.iterrows():
                def fmt(val):
                    try:
                        if val is None:
                            return None
                        return round(float(val), 2)
                    except Exception:
                        return None
                result.append({
                    "time": row.get("时间"),
                    "price": fmt(row.get("成交价")),
                    "volume": row.get("手数"),
                    "amount": fmt(fmt(row.get("手数")) * fmt(row.get("成交价")) if fmt(row.get("手数")) is not None and fmt(row.get("成交价")) is not None else None),
                    "trade_type": row.get("买卖盘性质") if "买卖盘性质" in row else None,
                })
            print(f"[minute_data_by_code] 交易日，返回{len(result)}条分时数据")
        else:
            # 非交易日，取最近一个交易日的分钟数据
            df = ak.stock_zh_a_hist_pre_min_em(symbol=code, start_time="09:00:00", end_time="15:40:00")
            if df is None or df.empty:
                print(f"[minute_data_by_code] 非交易日未找到股票代码: {code}")
                return JSONResponse({"success": False, "message": f"未找到股票代码: {code}"}, status_code=404)
            # 取最近一个交易日
            for _, row in df.iterrows():
                def fmt(val):
                    try:
                        if val is None:
                            return None
                        return round(float(val), 2)
                    except Exception:
                        return None
                result.append({
                    "time": row.get("时间"),
                    "price": fmt(row.get("最新价")),
                    "open": fmt(row.get("开盘")),
                    "close": fmt(row.get("收盘")),
                    "high": fmt(row.get("最高")),
                    "low": fmt(row.get("最低")),
                    "avg_price": fmt((row.get("成交额") / (row.get("成交量") * 100)) if row.get("成交量") else None),
                    "volume": row.get("成交量"),
                    "amount": fmt(row.get("成交额")),
                })
            print(f"[minute_data_by_code] 非交易日，返回{len(result)}条分时数据")
        if result:
            print(f"[minute_data_by_code] 前3条数据: {result[:3]}")
        return JSONResponse({"success": True, "data": result})
    except Exception as e:
        print(f"[minute_data_by_code] 异常: {e}")
        import traceback
        print(traceback.format_exc())
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

@router.get("/kline_hist")
async def get_kline_hist(
    code: str = Query(None, description="股票代码"),
    period: str = Query("daily", description="周期，如daily"),
    start_date: str = Query(None, description="开始日期，YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期，YYYY-MM-DD"),
    adjust: str = Query("qfq", description="复权类型，如qfq")
):
    """
    获取A股K线历史（日线）数据
    """
    print(f"[kline_hist] 输入参数: code={code}, period={period}, start_date={start_date}, end_date={end_date}, adjust={adjust}")
    if not code or not start_date or not end_date:
        print(f"[kline_hist] 缺少参数")
        return JSONResponse({"success": False, "message": "缺少参数"}, status_code=400)
    try:
        # 日期格式化为YYYYMMDD
        start_date_fmt = start_date.replace('-', '') if start_date else None
        end_date_fmt = end_date.replace('-', '') if end_date else None
        df = ak.stock_zh_a_hist(symbol=code, period=period, start_date=start_date_fmt, end_date=end_date_fmt, adjust=adjust)
        if df is None or df.empty:
            print(f"[kline_hist] 未找到股票代码: {code}")
            return JSONResponse({"success": False, "message": f"未找到股票代码: {code}"}, status_code=404)
        result = []
        def fmt(val):
            try:
                if val is None:
                    return None
                return round(float(val), 2)
            except Exception:
                return None
        for _, row in df.iterrows():
            date_val = row.get("日期")
            if hasattr(date_val, 'strftime'):
                date_val = date_val.strftime('%Y-%m-%d')
            
            # 获取原始数据
            open_price = fmt(row.get("开盘"))
            close_price = fmt(row.get("收盘"))
            high_price = fmt(row.get("最高"))
            low_price = fmt(row.get("最低"))
            
            # 调试：输出原始Akshare数据
            if len(result) < 3:  # 只输出前3条
                print(f"[kline_hist] 原始Akshare数据 {date_val}:", {
                    "开盘": row.get("开盘"),
                    "收盘": row.get("收盘"), 
                    "最高": row.get("最高"),
                    "最低": row.get("最低")
                })
                print(f"[kline_hist] 格式化后数据 {date_val}:", {
                    "open": open_price,
                    "close": close_price,
                    "high": high_price,
                    "low": low_price
                })
            
            result.append({
                "date": date_val,
                "code": code,
                "open": open_price,
                "close": close_price,
                "high": high_price,
                "low": low_price,
                "volume": int(row.get("成交量")) if row.get("成交量") is not None else None,
                "amount": fmt(row.get("成交额")),
                "amplitude": fmt(row.get("振幅")),
                "pct_chg": fmt(row.get("涨跌幅")),
                "change": fmt(row.get("涨跌额")),
                "turnover": fmt(row.get("换手率")),
            })
        print(f"[kline_hist] 返回{len(result)}条K线数据，前3条: {result[:3]}")
        return JSONResponse({"success": True, "data": result})
    except Exception as e:
        print(f"[kline_hist] 异常: {e}")
        import traceback
        print(traceback.format_exc())
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

# 获取A股分钟K线历史数据
@router.get("/kline_min_hist")
async def get_kline_min_hist(
    code: str = Query(None, description="股票代码"),
    period: str = Query("60", description="周期，分钟K，如1、5、15、30、60"),
    start_datetime: str = Query(None, description="开始时间，YYYY-MM-DD HH:MM:SS"),
    end_datetime: str = Query(None, description="结束时间，YYYY-MM-DD HH:MM:SS"),
    adjust: str = Query("qfq", description="复权类型，如qfq")
):
    """
    获取A股分钟K线（如1小时线）历史数据
    """
    print(f"[kline_min_hist] 输入参数: code={code}, period={period}, start_datetime={start_datetime}, end_datetime={end_datetime}, adjust={adjust}")
    if not code or not start_datetime or not end_datetime:
        print(f"[kline_min_hist] 缺少参数")
        return JSONResponse({"success": False, "message": "缺少参数"}, status_code=400)
    try:
        # 日期格式化
        start_dt_fmt = start_datetime.replace('-', '').replace(':', '').replace(' ', '') if start_datetime else None
        end_dt_fmt = end_datetime.replace('-', '').replace(':', '').replace(' ', '') if end_datetime else None
        # 1分钟线不支持复权，adjust传空
        ak_adjust = '' if period == '1' else adjust
        print(f"[kline_min_hist] 调用ak，symbol={code}, period={period}, start={start_dt_fmt}, end={end_dt_fmt}, adjust={ak_adjust}")
        df = ak.stock_zh_a_hist_min_em(symbol=code, period=period, start_date=start_dt_fmt, end_date=end_dt_fmt, adjust=ak_adjust)
        if df is None or df.empty:
            print(f"[kline_min_hist] 未找到股票代码: {code}")
            return JSONResponse({"success": False, "message": f"未找到股票代码: {code}"}, status_code=404)
        result = []
        def fmt(val):
            try:
                if val is None:
                    return None
                return round(float(val), 2)
            except Exception:
                return None
        for _, row in df.iterrows():
            date_val = row.get("时间")
            if hasattr(date_val, 'strftime'):
                date_val = date_val.strftime('%Y-%m-%d %H:%M:%S')
            result.append({
                "date": date_val,
                "code": code,
                "open": fmt(row.get("开盘")),
                "close": fmt(row.get("收盘")),
                "high": fmt(row.get("最高")),
                "low": fmt(row.get("最低")),
                "volume": int(row.get("成交量")) if row.get("成交量") is not None else None,
                "amount": fmt(row.get("成交额")),
                "amplitude": fmt(row.get("振幅")),
                "pct_chg": fmt(row.get("涨跌幅")),
                "change": fmt(row.get("涨跌额")),
                "turnover": fmt(row.get("换手率")),
            })
        print(f"[kline_min_hist] 返回{len(result)}条分钟K线数据，前3条: {result[:3]}")
        return JSONResponse({"success": True, "data": result})
    except Exception as e:
        print(f"[kline_min_hist] 异常: {e}")
        import traceback
        print(traceback.format_exc())
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)
    
@router.get("/latest_financial")
async def get_latest_financial(code: str = Query(..., description="股票代码")):
    """
    获取指定股票代码的最新报告期主要财务指标
    """
    try:
        print(f"[latest_financial] 请求参数: code={code}")
        import pandas as pd
        df = ak.stock_financial_abstract(symbol=code)
        print(f"[latest_financial] 获取到原始数据: {df.shape if df is not None else None}")
        if df is None or df.empty:
            print(f"[latest_financial] 未获取到财务数据")
            return JSONResponse({"success": False, "message": "未获取到财务数据"}, status_code=404)
        print(f"[latest_financial] DataFrame columns: {df.columns.tolist()}")

        # 自动查找行名列
        row_name_col = None
        for possible in ['指标', '选项', '名称']:
            if possible in df.columns:
                row_name_col = possible
                break
        if row_name_col is None:
            print(f"[latest_financial] 未找到指标行名列，所有列为: {df.columns.tolist()}")
            return JSONResponse({"success": False, "message": "未找到指标行名列"}, status_code=500)

        # 找到所有报告期列（一般为数字开头的列）
        period_cols = [col for col in df.columns if str(col).isdigit()]
        if not period_cols:
            # 也可能是 '2024-03-31' 这种格式
            period_cols = [col for col in df.columns if str(col).startswith('20')]
        if not period_cols:
            print(f"[latest_financial] 未找到报告期列，所有列为: {df.columns.tolist()}")
            return JSONResponse({"success": False, "message": "未找到报告期列"}, status_code=500)
        # 取最新报告期
        period_cols_sorted = sorted(period_cols, reverse=True)
        latest_date = period_cols_sorted[0]
        print(f"[latest_financial] 最新报告期: {latest_date}")
 
        # 指标映射
        indicator_map = {
            "pe": ["市盈率", "市盈率-TTM", "市盈率(动)"],
            "pb": ["市净率"],
            "roe": ["净资产收益率", "净资产收益率(加权)", "净资产收益率(ROE)"],
            "roa": ["资产收益率", "资产收益率(ROA)", "总资产报酬率(ROA)"],
            "revenue": ["营业总收入", "营业收入"],
            "profit": ["归母净利润", "净利润"],
            "eps": ["每股收益", "基本每股收益", "每股收益(EPS)"],
            "bps": ["每股净资产", "每股净资产(BPS)"]
        }

        result = {
            "report_date": latest_date
        }
        for key, possible_names in indicator_map.items():
            value = None
            for name in possible_names:
                row = df[df[row_name_col] == name]
                if not row.empty:
                    value = row[latest_date].values[0] if latest_date in row else row.iloc[0, -1]
                    print(f"[latest_financial] 指标 {key} 匹配到: {name}，值: {value}")
                    break
            if value is None:
                print(f"[latest_financial] 指标 {key} 未匹配到任何行")
            result[key] = value

        print(f"[latest_financial] 返回结果: {result}")
        result = clean_nan(result)
        return JSONResponse({"success": True, "data": result})
    except Exception as e:
        import traceback
        print(f"[latest_financial] 异常: {e}")
        print(traceback.format_exc())
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

@router.get("/financial_indicator_list")
async def get_financial_indicator_list(
    symbol: str = Query(..., description="股票代码"),
    indicator: str = Query("按报告期", description="指标报告类型")
):
    """
    获取指定股票代码和指标类型的主要财务指标列表（返回所有报告期）
    """
    try:
        print(f"[financial_indicator_list] symbol={symbol}, indicator={indicator}")
        if indicator == "1":
            indicator = "按报告期"
        elif indicator == "2":
            indicator = "按年度"
        elif indicator == "3":
            indicator = "按单季度"
        else:
            indicator = "按报告期"
        df = ak.stock_financial_abstract_ths(symbol=symbol, indicator=indicator)
        print(f"[financial_indicator_list] 原始数据列: {df.columns.tolist()}")
        if df is None or df.empty:
            return JSONResponse({"success": False, "message": "未获取到财务数据"}, status_code=404)

        # 你需要的指标
        wanted_indicators = [
            "报告期", "净资产收益率", "资产收益率", "营业总收入", "净利润",
            "基本每股收益", "每股净资产"
        ]
        # 只保留需要的列，且存在于df中的
        cols = [col for col in wanted_indicators if col in df.columns]
        if not cols:
            return JSONResponse({"success": False, "message": "未找到所需指标"}, status_code=404)

        # 按报告期升序排列（从旧到新，便于图表从左到右显示）
        df = df.sort_values("报告期", ascending=True)
        # 转为dict
        data = df[cols].to_dict(orient="records")
        data = clean_nan(data)
        return JSONResponse({"success": True, "data": data})
    except Exception as e:
        print(f"[financial_indicator_list] 异常: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


def clean_nan(obj):
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nan(v) for v in obj]
    return obj