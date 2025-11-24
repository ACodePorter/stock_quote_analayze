"""
港股行情管理API
提供港股实时行情数据查询服务
"""

from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from database import get_db
from sqlalchemy.orm import Session
import traceback
import numpy as np
import pandas as pd
import akshare as ak
from sqlalchemy import text, create_engine, func
from models import StockRealtimeQuoteHK, StockBasicInfoHK, HistoricalQuotesHK
import datetime

# 创建两个路由器：一个用于旧的接口（保持原路径），一个用于新的港股详情页接口
router_old = APIRouter(prefix="/api/stock", tags=["stock_hk"])
router = APIRouter(prefix="/api/stock/hk", tags=["stock_hk"])

def safe_float(value):
    """安全地将值转换为浮点数"""
    try:
        if value in [None, '', '-'] or pd.isna(value):
            return None
        return float(value)
    except (ValueError, TypeError):
        return None

def clean_nan(data_list):
    """清理数据中的NaN值"""
    if not isinstance(data_list, list):
        return data_list
    cleaned = []
    for item in data_list:
        if isinstance(item, dict):
            cleaned_item = {}
            for k, v in item.items():
                if pd.isna(v) or (isinstance(v, float) and np.isnan(v)):
                    cleaned_item[k] = None
                else:
                    cleaned_item[k] = v
            cleaned.append(cleaned_item)
        else:
            cleaned.append(item)
    return cleaned

@router_old.get("/hk_quote_board_list")
def get_hk_quote_board_list(
    ranking_type: str = Query('rise', description="排行类型: rise(涨幅榜), fall(跌幅榜), volume(成交量榜), turnover_rate(换手率榜)"),
    page: int = Query(1, description="页码，从1开始"),
    page_size: int = Query(20, description="每页条数，默认20"),
    keyword: str = Query(None, description="搜索关键词（股票代码或名称）")
):
    """
    获取港股实时行情排行数据，支持多种排行类型、搜索和分页 (数据源: stock_realtime_quote_hk)
    """
    try:
        print(f"📊 获取港股行情排行 (from DB): type={ranking_type}, page={page}, page_size={page_size}, keyword={keyword}")
        
        # 1. 获取最新交易日期的实时行情数据
        db = next(get_db())
        
        try:
            latest_date_result = pd.read_sql_query("""
                SELECT MAX(trade_date) as latest_date 
                FROM stock_realtime_quote_hk 
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
              
                # 构建查询SQL - 使用与stock_manage.py相同的方式
                if keyword and keyword.strip():
                    keyword_clean = keyword.strip().replace("'", "''")  # 防止SQL注入
                    sql_query = text(f"""
                        SELECT * FROM stock_realtime_quote_hk 
                        WHERE change_percent IS NOT NULL AND trade_date = '{latest_trade_date}'
                        AND (code LIKE '%{keyword_clean}%' OR name LIKE '%{keyword_clean}%' OR english_name LIKE '%{keyword_clean}%')
                        ORDER BY code
                    """)
                else:
                    sql_query = text(f"""
                        SELECT * FROM stock_realtime_quote_hk 
                        WHERE change_percent IS NOT NULL AND trade_date = '{latest_trade_date}'
                        ORDER BY code
                    """)
                
                df = pd.read_sql_query(sql_query, db.bind)
        finally:
            db.close()

        # 2. 排行类型排序
        sort_column_map = {
            'rise': ('change_percent', False),
            'fall': ('change_percent', True),
            'volume': ('volume', False),
            'turnover_rate': ('turnover_rate', False)
        }
        
        if ranking_type in sort_column_map:
            col, ascending = sort_column_map[ranking_type]
            if not df.empty and col in df.columns:
                df = df.sort_values(by=col, ascending=ascending, na_position='last')
        else:
            return JSONResponse({'success': False, 'message': '无效的排行类型'}, status_code=400)

        # 3. 字段重命名和格式化
        df = df.replace({np.nan: None})
        
        # 确保数值字段的数据类型正确
        numeric_columns = ['current_price', 'change_percent', 'change_amount', 'open', 'pre_close', 
                          'high', 'low', 'volume', 'amount']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 字段映射，与A股接口保持一致
        field_rename_map = {
            'code': 'code',
            'name': 'name',
            'english_name': 'english_name',
            'current_price': 'current',
            'change_percent': 'change_percent',
            'change_amount': 'change',
            'open': 'open',
            'pre_close': 'pre_close',
            'high': 'high',
            'low': 'low',
            'volume': 'volume',
            'amount': 'turnover'
        }
        
        if df.empty:
            df_selected = pd.DataFrame(columns=field_rename_map.values())
        else:
            # 只选择存在的字段
            available_fields = [f for f in field_rename_map.keys() if f in df.columns]
            df_selected = df[available_fields].rename(columns=field_rename_map)
            
            # 如果change字段不存在，尝试计算
            if 'change' not in df_selected.columns and 'current' in df_selected.columns and 'pre_close' in df_selected.columns:
                current_numeric = pd.to_numeric(df_selected['current'], errors='coerce')
                pre_close_numeric = pd.to_numeric(df_selected['pre_close'], errors='coerce')
                df_selected['change'] = (current_numeric - pre_close_numeric).round(2)
            
            # 添加rate字段（换手率），港股可能没有，设为None
            if 'rate' not in df_selected.columns:
                df_selected['rate'] = None

        total = len(df_selected)

        # 4. 分页处理
        start = (page - 1) * page_size
        end = start + page_size
        df_page = df_selected.iloc[start:end].copy()
        
        # 5. 格式化数据
        data = df_page.to_dict(orient='records')
        data = clean_nan(data)
        
        # 格式化数值字段
        for item in data:
            for key in ['current', 'change', 'change_percent', 'open', 'pre_close', 'high', 'low', 'volume', 'turnover', 'rate']:
                if key in item and item[key] is not None:
                    if key in ['change_percent', 'rate']:
                        # 百分比字段保留2位小数
                        item[key] = round(float(item[key]), 2) if item[key] is not None else None
                    elif key in ['current', 'open', 'pre_close', 'high', 'low', 'change']:
                        # 价格字段保留2位小数
                        item[key] = round(float(item[key]), 2) if item[key] is not None else None
                    else:
                        # 其他数值字段
                        item[key] = float(item[key]) if item[key] is not None else None
        
        print(f"✅ 成功获取 {len(data)} 条港股排行数据 (总数: {total})")
        return JSONResponse({
            'success': True, 
            'data': data, 
            'total': total, 
            'page': page, 
            'page_size': page_size
        })
        
    except Exception as e:
        print(f"❌ 获取港股排行数据失败: {str(e)}")
        tb = traceback.format_exc()
        print(tb)
        return JSONResponse({
            'success': False, 
            'message': '获取港股排行数据失败', 
            'error': str(e), 
            'traceback': tb
        }, status_code=500)

@router_old.get("/hk_indices")
def get_hk_indices():
    """
    获取港股指数模拟数据
    返回恒生指数、恒生科技指数等模拟数据
    """
    try:
        import random
        from datetime import datetime
        
        # 模拟港股指数数据
        indices_data = [
            {
                'code': 'HSI',
                'name': '恒生指数',
                'value': round(18000 + random.uniform(-500, 500), 2),
                'change': round(random.uniform(-200, 200), 2),
                'change_percent': round(random.uniform(-1.5, 1.5), 2)
            },
            {
                'code': 'HSTECH',
                'name': '恒生科技指数',
                'value': round(4500 + random.uniform(-200, 200), 2),
                'change': round(random.uniform(-80, 80), 2),
                'change_percent': round(random.uniform(-2.0, 2.0), 2)
            },
            {
                'code': 'HSCEI',
                'name': '恒生中国企业指数',
                'value': round(6500 + random.uniform(-300, 300), 2),
                'change': round(random.uniform(-150, 150), 2),
                'change_percent': round(random.uniform(-2.5, 2.5), 2)
            },
            {
                'code': 'HSCI',
                'name': '恒生综合指数',
                'value': round(2800 + random.uniform(-100, 100), 2),
                'change': round(random.uniform(-50, 50), 2),
                'change_percent': round(random.uniform(-2.0, 2.0), 2)
            }
        ]
        
        return JSONResponse({
            'success': True,
            'data': indices_data,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        print(f"❌ 获取港股指数数据失败: {str(e)}")
        tb = traceback.format_exc()
        print(tb)
        return JSONResponse({
            'success': False,
            'message': '获取港股指数数据失败',
            'error': str(e)
        }, status_code=500)

# 港股实时行情接口
@router.get("/realtime_quote_by_code")
async def get_hk_realtime_quote_by_code(code: str = Query(None, description="股票代码"), db: Session = Depends(get_db)):
    """
    获取港股实时行情数据
    优先从数据库查询，如果数据库没有则调用akshare实时获取
    
    Args:
        code: 股票代码
        
    Returns:
        {"success": True, "data": {...}}
    """
    print(f"[hk_realtime_quote_by_code] 输入参数: code={code}")
    if not code:
        print("[hk_realtime_quote_by_code] 缺少参数")
        return JSONResponse({"success": False, "message": "缺少股票代码参数code"}, status_code=400)
    
    try:
        # 获取最新交易日期
        latest_date_result = pd.read_sql_query("""
            SELECT MAX(trade_date) as latest_date 
            FROM stock_realtime_quote_hk 
            WHERE change_percent IS NOT NULL
        """, db.bind)
        
        db_stock_data = None
        if not latest_date_result.empty and latest_date_result.iloc[0]['latest_date'] is not None:
            latest_trade_date = latest_date_result.iloc[0]['latest_date']
            if isinstance(latest_trade_date, str):
                latest_trade_date = latest_trade_date[:10]  # 只取日期部分
            else:
                latest_trade_date = str(latest_trade_date)[:10]
            
            db_stock_data = db.query(StockRealtimeQuoteHK).filter(
                StockRealtimeQuoteHK.code == code,
                StockRealtimeQuoteHK.trade_date == latest_trade_date
            ).first()
        
        # 如果数据库有数据，直接返回
        if db_stock_data:
            def fmt(val):
                try:
                    if val is None:
                        return None
                    return f"{float(val):.2f}"
                except Exception:
                    return None
            
            result = {
                "code": db_stock_data.code,
                "name": db_stock_data.name,
                "current_price": fmt(db_stock_data.current_price),
                "change_amount": fmt(db_stock_data.change_amount),
                "change_percent": fmt(db_stock_data.change_percent),
                "open": fmt(db_stock_data.open),
                "pre_close": fmt(db_stock_data.pre_close),
                "high": fmt(db_stock_data.high),
                "low": fmt(db_stock_data.low),
                "volume": fmt(db_stock_data.volume),
                "turnover": fmt(db_stock_data.amount),
                "turnover_rate": None,  # 从历史行情表获取
                "pe_dynamic": None,  # 从财务指标接口获取
                "average_price": None,  # 需要计算
            }
            
            # 计算均价
            if db_stock_data.volume and db_stock_data.volume > 0 and db_stock_data.amount:
                try:
                    avg_price = float(db_stock_data.amount) / float(db_stock_data.volume)
                    result["average_price"] = fmt(avg_price)
                except Exception:
                    pass
            
            # 从历史行情表获取最新的换手率
            try:
                latest_history = db.query(HistoricalQuotesHK).filter(
                    HistoricalQuotesHK.code == code,
                    HistoricalQuotesHK.turnover_rate.isnot(None)
                ).order_by(HistoricalQuotesHK.date.desc()).first()
                if latest_history and latest_history.turnover_rate is not None:
                    result["turnover_rate"] = fmt(latest_history.turnover_rate)
                    print(f"[hk_realtime_quote_by_code] 从历史行情表获取换手率: {result['turnover_rate']}")
            except Exception as e:
                print(f"[hk_realtime_quote_by_code] 获取换手率失败: {e}")
            
            # 从财务指标接口获取市盈率
            try:
                import akshare as ak
                financial_df = ak.stock_hk_financial_indicator_em(symbol=code)
                if financial_df is not None and not financial_df.empty and '市盈率' in financial_df.columns:
                    pe_value = financial_df.iloc[0]['市盈率']
                    if pd.notna(pe_value):
                        result["pe_dynamic"] = fmt(pe_value)
                        print(f"[hk_realtime_quote_by_code] 从财务指标获取市盈率: {result['pe_dynamic']}")
            except Exception as e:
                print(f"[hk_realtime_quote_by_code] 获取市盈率失败: {e}")
            
            print(f"[hk_realtime_quote_by_code] 从数据库返回数据: {result}")
            return JSONResponse({"success": True, "data": result})
        
        # 数据库没有数据，尝试从akshare实时获取
        try:
            df_hk_spot = ak.stock_hk_spot_em()
            stock_data = df_hk_spot[df_hk_spot['代码'] == code]
            
            if stock_data.empty:
                print(f"[hk_realtime_quote_by_code] 未找到股票代码: {code}")
                return JSONResponse({"success": False, "message": f"未找到股票代码: {code}"}, status_code=404)
            
            row = stock_data.iloc[0]
            
            def fmt(val):
                try:
                    if val is None or pd.isna(val):
                        return None
                    return f"{float(val):.2f}"
                except Exception:
                    return None
            
            result = {
                "code": code,
                "name": row.get('名称', ''),
                "current_price": fmt(row.get('最新价')),
                "change_amount": fmt(row.get('涨跌额')),
                "change_percent": fmt(row.get('涨跌幅')),
                "open": fmt(row.get('今开')),
                "pre_close": fmt(row.get('昨收')),
                "high": fmt(row.get('最高')),
                "low": fmt(row.get('最低')),
                "volume": fmt(row.get('成交量')),
                "turnover": fmt(row.get('成交额')),
                "turnover_rate": None,  # 从历史行情表获取
                "pe_dynamic": None,  # 从财务指标接口获取
                "average_price": None,
            }
            
            # 计算均价
            if row.get('成交量') and float(row.get('成交量', 0)) > 0 and row.get('成交额'):
                try:
                    avg_price = float(row.get('成交额')) / float(row.get('成交量'))
                    result["average_price"] = fmt(avg_price)
                except Exception:
                    pass
            
            # 从历史行情表获取最新的换手率
            try:
                latest_history = db.query(HistoricalQuotesHK).filter(
                    HistoricalQuotesHK.code == code,
                    HistoricalQuotesHK.turnover_rate.isnot(None)
                ).order_by(HistoricalQuotesHK.date.desc()).first()
                if latest_history and latest_history.turnover_rate is not None:
                    result["turnover_rate"] = fmt(latest_history.turnover_rate)
                    print(f"[hk_realtime_quote_by_code] 从历史行情表获取换手率: {result['turnover_rate']}")
            except Exception as e:
                print(f"[hk_realtime_quote_by_code] 获取换手率失败: {e}")
            
            # 从财务指标接口获取市盈率
            try:
                financial_df = ak.stock_hk_financial_indicator_em(symbol=code)
                if financial_df is not None and not financial_df.empty and '市盈率' in financial_df.columns:
                    pe_value = financial_df.iloc[0]['市盈率']
                    if pd.notna(pe_value):
                        result["pe_dynamic"] = fmt(pe_value)
                        print(f"[hk_realtime_quote_by_code] 从财务指标获取市盈率: {result['pe_dynamic']}")
            except Exception as e:
                print(f"[hk_realtime_quote_by_code] 获取市盈率失败: {e}")
            
            print(f"[hk_realtime_quote_by_code] 从akshare返回数据: {result}")
            return JSONResponse({"success": True, "data": result})
            
        except Exception as e:
            print(f"[hk_realtime_quote_by_code] 从akshare获取数据失败: {e}")
            return JSONResponse({"success": False, "message": f"获取港股实时行情失败: {str(e)}"}, status_code=500)
            
    except Exception as e:
        print(f"[hk_realtime_quote_by_code] 异常: {e}")
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

# 港股分时数据接口
@router.get("/minute_data_by_code")
async def get_hk_minute_data_by_code(code: str = Query(None, description="股票代码")):
    """
    获取港股分时数据（使用ak.stock_hk_hist_min_em获取1分钟数据）
    
    Args:
        code: 股票代码
        
    Returns:
        {"success": True, "data": [{time, price, volume, amount, ...}]}
    """
    print(f"[hk_minute_data_by_code] 输入参数: code={code}")
    if not code:
        print("[hk_minute_data_by_code] 缺少参数")
        return JSONResponse({"success": False, "message": "缺少股票代码参数code"}, status_code=400)
    
    try:
        # 获取当日日期
        today = datetime.date.today()
        today_str = today.strftime('%Y%m%d')
        
        # 获取最近几天的分钟数据（确保能获取到当日数据）
        # 使用1分钟周期
        try:
            df = ak.stock_hk_hist_min_em(symbol=code, period="1", start_date=today_str, end_date=today_str, adjust="")
            
            if df is None or df.empty:
                # 如果当日没有数据，尝试获取最近一个交易日的数据
                # 往前推几天
                for i in range(1, 6):
                    prev_date = (today - datetime.timedelta(days=i)).strftime('%Y%m%d')
                    try:
                        df = ak.stock_hk_hist_min_em(symbol=code, period="1", start_date=prev_date, end_date=prev_date, adjust="")
                        if df is not None and not df.empty:
                            print(f"[hk_minute_data_by_code] 使用日期 {prev_date} 的数据")
                            break
                    except Exception:
                        continue
                
                if df is None or df.empty:
                    print(f"[hk_minute_data_by_code] 未找到股票代码: {code}")
                    return JSONResponse({"success": False, "message": f"未找到股票代码: {code}"}, status_code=404)
        except Exception as e:
            print(f"[hk_minute_data_by_code] 调用akshare失败: {e}")
            return JSONResponse({"success": False, "message": f"获取港股分时数据失败: {str(e)}"}, status_code=500)
        
        result = []
        for _, row in df.iterrows():
            def fmt(val):
                try:
                    if val is None or pd.isna(val):
                        return None
                    return round(float(val), 2)
                except Exception:
                    return None
            
            # 获取时间字段（可能是"时间"或"日期时间"等）
            time_val = None
            for time_col in ['时间', '日期时间', 'datetime', 'time']:
                if time_col in row:
                    time_val = row[time_col]
                    break
            
            # 格式化时间
            if time_val is not None:
                if hasattr(time_val, 'strftime'):
                    time_val = time_val.strftime('%H:%M:%S')
                else:
                    time_val = str(time_val)
            
            # 获取价格字段
            price = None
            for price_col in ['收盘', '最新价', 'close', 'price']:
                if price_col in row:
                    price = fmt(row[price_col])
                    break
            
            # 获取成交量字段
            volume = None
            for vol_col in ['成交量', 'volume']:
                if vol_col in row:
                    vol_val = row[vol_col]
                    if vol_val is not None and not pd.isna(vol_val):
                        volume = int(float(vol_val))
                    break
            
            # 获取成交额字段
            amount = None
            for amt_col in ['成交额', 'amount']:
                if amt_col in row:
                    amount = fmt(row[amt_col])
                    break
            
            # 如果没有成交额，尝试计算
            if amount is None and price is not None and volume is not None:
                try:
                    amount = fmt(float(price) * float(volume))
                except Exception:
                    pass
            
            result.append({
                "time": time_val or "",
                "price": price,
                "volume": volume,
                "amount": amount,
                "trade_type": None,  # 港股分时数据可能没有买卖盘性质
            })
        
        print(f"[hk_minute_data_by_code] 返回{len(result)}条分时数据")
        return JSONResponse({"success": True, "data": result})
        
    except Exception as e:
        print(f"[hk_minute_data_by_code] 异常: {e}")
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

# 港股K线历史数据接口（日线/周线/月线）
@router.get("/kline_hist")
async def get_hk_kline_hist(
    code: str = Query(None, description="股票代码"),
    period: str = Query("daily", description="周期，如daily/weekly/monthly"),
    start_date: str = Query(None, description="开始日期，YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期，YYYY-MM-DD"),
    adjust: str = Query("", description="复权类型，港股暂不支持复权"),
    db: Session = Depends(get_db)
):
    """
    获取港股K线历史数据（日线/周线/月线）
    从historical_quotes_hk表查询
    """
    print(f"[hk_kline_hist] 输入参数: code={code}, period={period}, start_date={start_date}, end_date={end_date}")
    if not code or not start_date or not end_date:
        return JSONResponse({"success": False, "message": "缺少参数"}, status_code=400)
    
    try:
        # 从数据库查询历史数据
        query = db.query(HistoricalQuotesHK).filter(
            HistoricalQuotesHK.code == code
        )
        
        # 日期过滤
        if start_date:
            query = query.filter(HistoricalQuotesHK.date >= start_date)
        if end_date:
            query = query.filter(HistoricalQuotesHK.date <= end_date)
        
        # 按日期降序
        query = query.order_by(HistoricalQuotesHK.date.desc())
        
        quotes = query.all()
        
        # 如果数据库没有数据，尝试从akshare获取
        if not quotes:
            print(f"[hk_kline_hist] 数据库没有数据，尝试从akshare获取")
            try:
                import akshare as ak
                from datetime import datetime
                
                # 转换日期格式：YYYY-MM-DD -> YYYYMMDD
                start_date_str = start_date.replace("-", "")
                end_date_str = end_date.replace("-", "")
                
                # 根据周期选择接口
                if period == "daily":
                    df = ak.stock_hk_hist(symbol=code, period='daily', start_date=start_date_str, end_date=end_date_str, adjust='')
                elif period == "weekly":
                    df = ak.stock_hk_hist(symbol=code, period='weekly', start_date=start_date_str, end_date=end_date_str, adjust='')
                elif period == "monthly":
                    df = ak.stock_hk_hist(symbol=code, period='monthly', start_date=start_date_str, end_date=end_date_str, adjust='')
                else:
                    df = ak.stock_hk_hist(symbol=code, period='daily', start_date=start_date_str, end_date=end_date_str, adjust='')
                
                if df is None or df.empty:
                    return JSONResponse({"success": False, "message": f"未找到股票代码: {code} 的历史数据"}, status_code=404)
                
                # 转换DataFrame为返回格式
                result = []
                for _, row in df.iterrows():
                    try:
                        date_val = row.get('日期', '')
                        date_str = str(date_val) if date_val is not None else ''
                        # 处理日期格式：YYYYMMDD -> YYYY-MM-DD
                        if len(date_str) == 8 and date_str.isdigit():
                            date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                        elif len(date_str) == 10 and '-' in date_str:
                            # 已经是 YYYY-MM-DD 格式
                            pass
                        elif isinstance(date_val, pd.Timestamp):
                            date_str = date_val.strftime("%Y-%m-%d")
                        
                        result.append({
                            "date": date_str,
                            "open": float(row.get('开盘', 0)) if pd.notna(row.get('开盘')) else 0,
                            "close": float(row.get('收盘', 0)) if pd.notna(row.get('收盘')) else 0,
                            "high": float(row.get('最高', 0)) if pd.notna(row.get('最高')) else 0,
                            "low": float(row.get('最低', 0)) if pd.notna(row.get('最低')) else 0,
                            "volume": float(row.get('成交量', 0)) if pd.notna(row.get('成交量')) else 0,
                            "amount": float(row.get('成交额', 0)) if pd.notna(row.get('成交额')) else 0,
                        })
                    except Exception as e:
                        print(f"[hk_kline_hist] 处理行数据时出错: {e}, row: {row}")
                        continue
                
                # 按日期降序排列
                result.sort(key=lambda x: x['date'], reverse=True)
                
                print(f"[hk_kline_hist] 从akshare获取到{len(result)}条K线数据")
                return JSONResponse({"success": True, "data": result})
            except Exception as e:
                print(f"[hk_kline_hist] 从akshare获取数据失败: {e}")
                import traceback
                traceback.print_exc()
                return JSONResponse({"success": False, "message": f"未找到股票代码: {code} 的历史数据"}, status_code=404)
        
        result = []
        def fmt(val):
            try:
                if val is None:
                    return None
                return round(float(val), 2)
            except Exception:
                return None
        
        for quote in quotes:
            result.append({
                "date": quote.date,
                "code": quote.code,
                "open": fmt(quote.open),
                "close": fmt(quote.close),
                "high": fmt(quote.high),
                "low": fmt(quote.low),
                "volume": int(quote.volume) if quote.volume is not None else None,
                "amount": fmt(quote.amount),
                "amplitude": fmt(quote.amplitude),
                "pct_chg": fmt(quote.change_percent),
                "change": fmt(quote.change_amount),
                "turnover": fmt(quote.turnover_rate),
            })
        
        # 如果是周线或月线，需要聚合数据
        if period == "weekly" or period == "monthly":
            # 简单的聚合逻辑：按周/月分组，取第一天的开盘、最后一天的收盘、最高价、最低价、成交量总和
            # 这里简化处理，直接返回日线数据，前端可以自行聚合
            pass
        
        print(f"[hk_kline_hist] 返回{len(result)}条K线数据")
        return JSONResponse({"success": True, "data": result})
        
    except Exception as e:
        print(f"[hk_kline_hist] 异常: {e}")
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

# 港股分钟K线历史数据接口
@router.get("/kline_min_hist")
async def get_hk_kline_min_hist(
    code: str = Query(None, description="股票代码"),
    period: str = Query("60", description="周期，分钟K，如1、5、15、30、60"),
    start_datetime: str = Query(None, description="开始时间，YYYY-MM-DD HH:MM:SS"),
    end_datetime: str = Query(None, description="结束时间，YYYY-MM-DD HH:MM:SS"),
    adjust: str = Query("", description="复权类型，港股暂不支持复权")
):
    """
    获取港股分钟K线历史数据
    使用ak.stock_hk_hist_min_em接口
    """
    print(f"[hk_kline_min_hist] 输入参数: code={code}, period={period}, start_datetime={start_datetime}, end_datetime={end_datetime}")
    if not code or not start_datetime or not end_datetime:
        return JSONResponse({"success": False, "message": "缺少参数"}, status_code=400)
    
    try:
        # 日期格式化：YYYY-MM-DD HH:MM:SS -> YYYYMMDD
        start_date = start_datetime.split(' ')[0].replace('-', '')
        end_date = end_datetime.split(' ')[0].replace('-', '')
        
        print(f"[hk_kline_min_hist] 调用akshare: symbol={code}, period={period}, start_date={start_date}, end_date={end_date}")
        
        # 调用akshare接口
        df = ak.stock_hk_hist_min_em(symbol=code, period=period, start_date=start_date, end_date=end_date, adjust=adjust)
        
        if df is None or df.empty:
            print(f"[hk_kline_min_hist] 未找到股票代码: {code}")
            return JSONResponse({"success": False, "message": f"未找到股票代码: {code}"}, status_code=404)
        
        result = []
        def fmt(val):
            try:
                if val is None or pd.isna(val):
                    return None
                return round(float(val), 2)
            except Exception:
                return None
        
        for _, row in df.iterrows():
            # 获取时间字段
            date_val = None
            for time_col in ['时间', '日期时间', 'datetime', 'time']:
                if time_col in row:
                    date_val = row[time_col]
                    break
            
            if date_val is not None:
                if hasattr(date_val, 'strftime'):
                    date_val = date_val.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    date_val = str(date_val)
            
            # 获取价格字段
            open_price = None
            close_price = None
            high_price = None
            low_price = None
            
            for col in ['开盘', 'open']:
                if col in row:
                    open_price = fmt(row[col])
                    break
            for col in ['收盘', 'close']:
                if col in row:
                    close_price = fmt(row[col])
                    break
            for col in ['最高', 'high']:
                if col in row:
                    high_price = fmt(row[col])
                    break
            for col in ['最低', 'low']:
                if col in row:
                    low_price = fmt(row[col])
                    break
            
            # 获取成交量
            volume = None
            for vol_col in ['成交量', 'volume']:
                if vol_col in row:
                    vol_val = row[vol_col]
                    if vol_val is not None and not pd.isna(vol_val):
                        volume = int(float(vol_val))
                    break
            
            # 获取成交额
            amount = None
            for amt_col in ['成交额', 'amount']:
                if amt_col in row:
                    amount = fmt(row[amt_col])
                    break
            
            result.append({
                "date": date_val,
                "code": code,
                "open": open_price,
                "close": close_price,
                "high": high_price,
                "low": low_price,
                "volume": volume,
                "amount": amount,
                "amplitude": None,  # 港股分钟数据可能没有振幅
                "pct_chg": None,  # 港股分钟数据可能没有涨跌幅
                "change": None,  # 港股分钟数据可能没有涨跌额
                "turnover": None,  # 港股分钟数据可能没有换手率
            })
        
        print(f"[hk_kline_min_hist] 返回{len(result)}条分钟K线数据")
        return JSONResponse({"success": True, "data": result})
        
    except Exception as e:
        print(f"[hk_kline_min_hist] 异常: {e}")
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

