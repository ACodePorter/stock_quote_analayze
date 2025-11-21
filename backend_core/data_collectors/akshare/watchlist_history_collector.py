import time
import logging
from datetime import datetime, timedelta
import akshare as ak
from sqlalchemy.orm import Session
from sqlalchemy import exists, text
from backend_core.database.db import get_db

# 假设有自选股表 watchlist，字段 code
from backend_core.models.watchlist import Watchlist  # 需根据实际路径调整
from backend_core.models.historical_quotes import HistoricalQuotes  # 需根据实际路径调整
from backend_core.models.watchlist_history_collection_logs import WatchlistHistoryCollectionLogs  # 需根据实际路径调整

# 配置日志
logger = logging.getLogger(__name__)

def get_watchlist_codes(db: Session):
    """获取自选股股票代码列表，去重。"""
    codes = db.query(Watchlist.stock_code).distinct().all()
    return [c[0] for c in codes]

def has_collected(db: Session, stock_code: str) -> bool:
    """判断该股票是否已采集过历史数据。"""
    return db.query(
        exists().where(
            (WatchlistHistoryCollectionLogs.stock_code == stock_code) &
            (WatchlistHistoryCollectionLogs.status == 'success')
        )
    ).scalar()

def is_hk_stock(db: Session, stock_code: str) -> bool:
    """
    判断股票代码是否为港股。
    优先通过查询 stock_basic_info_hk 表判断，如果表中没有记录，则通过代码格式判断。
    港股代码特征：5位数字，以0开头（如 00700, 00111）
    """
    if not stock_code:
        return False
    
    code_str = str(stock_code).strip()
    logger.info(f"[is_hk_stock] 检查股票代码: {code_str}, 长度: {len(code_str)}")
    
    # 方法1：查询 stock_basic_info_hk 表
    try:
        result = db.execute(
            text("SELECT 1 FROM stock_basic_info_hk WHERE code = :code LIMIT 1"),
            {"code": code_str}
        ).fetchone()
        if result is not None:
            logger.info(f"[is_hk_stock] 通过 stock_basic_info_hk 表判断 {code_str} 为港股")
            return True
    except Exception as e:
        logger.warning(f"[is_hk_stock] 查询 stock_basic_info_hk 表时出错: {e}")
    
    
    logger.debug(f"[is_hk_stock] {code_str} 不是港股")
    return False

def log_collection(db: Session, stock_code: str, affected_rows: int, status: str, error_message: str = None):
    """写入采集日志。"""
    log = WatchlistHistoryCollectionLogs(
        stock_code=stock_code,
        affected_rows=affected_rows,
        status=status,
        error_message=error_message,
        created_at=datetime.now()
    )
    db.add(log)
    db.commit()

def insert_historical_quotes(db: Session, stock_code: str, df):
    """批量插入历史行情数据，避免重复插入。"""
    rows = []
    # 根据code从watchlist表获取股票名称
    stock_name = None
    try:
        # 使用 scalar() 方法直接获取单个值，避免返回 Row 对象
        result = db.query(Watchlist.stock_name).filter(Watchlist.stock_code == stock_code).scalar()
        if result is not None:
            stock_name = str(result)
    except Exception as e:
        logger.warning(f"获取股票 {stock_code} 名称失败: {e}")
    logger.debug(f"股票代码 {stock_code} 的名称: {stock_name}")

    for _, row in df.iterrows():
        hq = HistoricalQuotes(
            code=stock_code,
            name=stock_name,
            date=row.get('日期'),
            open=row.get('开盘'),
            close=row.get('收盘'),
            high=row.get('最高'),
            low=row.get('最低'),
            volume=row.get('成交量'),
            amount=row.get('成交额'),
            amplitude=row.get('振幅'),
            change_percent=row.get('涨跌幅'),
            change=row.get('涨跌额'),
            turnover_rate=row.get('换手率')
            #adjust='qfq'
        )
        rows.append(hq)
    if rows:
        # 执行upsert操作，避免重复插入
        # 这里只能用原生SQL或SQLAlchemy的merge/on_conflict等方式，以下为通用实现（以PostgreSQL为例，其他数据库需调整语法）
        from sqlalchemy.dialects.postgresql import insert

        for hq in rows:
            stmt = insert(HistoricalQuotes).values(
                code=hq.code,
                name=hq.name,    # 新增股票名称字段      
                date=hq.date,
                open=hq.open,
                close=hq.close,
                high=hq.high,
                low=hq.low,
                volume=hq.volume,
                amount=hq.amount,
                amplitude=hq.amplitude,
                change_percent=hq.change_percent,
                change=hq.change,
                turnover_rate=hq.turnover_rate
                #adjust=hq.adjust
            ).on_conflict_do_update(
                index_elements=['code', 'date'],
                set_={
                    'name': hq.name,
                    'open': hq.open,
                    'close': hq.close,
                    'high': hq.high,
                    'low': hq.low,
                    'volume': hq.volume,
                    'amount': hq.amount,
                    'amplitude': hq.amplitude,
                    'change_percent': hq.change_percent,
                    'change': hq.change,
                    'turnover_rate': hq.turnover_rate
                    #'adjust': hq.adjust
                }
            )
            db.execute(stmt)
        db.commit()
    return len(rows)

def insert_historical_quotes_hk(db: Session, stock_code: str, df):
    """批量插入港股历史行情数据，避免重复插入。"""
    rows = []
    # 根据code从watchlist表获取股票名称
    stock_name = None
    try:
        # 使用 scalar() 方法直接获取单个值，避免返回 Row 对象
        result = db.query(Watchlist.stock_name).filter(Watchlist.stock_code == stock_code).scalar()
        if result is not None:
            stock_name = str(result)
    except Exception as e:
        logger.warning(f"获取港股 {stock_code} 名称失败: {e}")
    logger.debug(f"港股代码 {stock_code} 的名称: {stock_name}")

    for _, row in df.iterrows():
        # 处理日期格式：从 YYYYMMDD 转换为 YYYY-MM-DD
        date_str = str(row.get('日期', ''))
        if len(date_str) == 8 and date_str.isdigit():
            date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        else:
            date_formatted = date_str
        
        # 港股数据字段映射
        row_data = {
            'code': stock_code,
            'name': stock_name,
            'date': date_formatted,
            'open': row.get('开盘') if '开盘' in row.index else None,
            'close': row.get('收盘') if '收盘' in row.index else None,
            'high': row.get('最高') if '最高' in row.index else None,
            'low': row.get('最低') if '最低' in row.index else None,
            'pre_close': row.get('昨收') if '昨收' in row.index else None,
            'volume': row.get('成交量') if '成交量' in row.index else None,
            'amount': row.get('成交额') if '成交额' in row.index else None,
            'amplitude': row.get('振幅') if '振幅' in row.index else None,
            'change_percent': row.get('涨跌幅') if '涨跌幅' in row.index else None,
            'change_amount': row.get('涨跌额') if '涨跌额' in row.index else None,
            'turnover_rate': row.get('换手率') if '换手率' in row.index else None,
        }
        rows.append(row_data)
    
    if rows:
        # 使用 PostgreSQL 的 ON CONFLICT DO UPDATE 进行 upsert
        for row_data in rows:
            stmt = text("""
                INSERT INTO historical_quotes_hk (
                    code, name, date, open, close, high, low, pre_close,
                    volume, amount, amplitude, change_percent, change_amount, turnover_rate
                ) VALUES (
                    :code, :name, :date, :open, :close, :high, :low, :pre_close,
                    :volume, :amount, :amplitude, :change_percent, :change_amount, :turnover_rate
                )
                ON CONFLICT (code, date) DO UPDATE SET
                    name = EXCLUDED.name,
                    open = EXCLUDED.open,
                    close = EXCLUDED.close,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    pre_close = EXCLUDED.pre_close,
                    volume = EXCLUDED.volume,
                    amount = EXCLUDED.amount,
                    amplitude = EXCLUDED.amplitude,
                    change_percent = EXCLUDED.change_percent,
                    change_amount = EXCLUDED.change_amount,
                    turnover_rate = EXCLUDED.turnover_rate
            """)
            db.execute(stmt, row_data)
        db.commit()
    return len(rows)

def collect_watchlist_history():
    """
    自选股历史行情采集主函数。
    返回采集成功的股票数量和失败的股票数量。
    支持A股和港股。
    """
    db = next(get_db())
    codes = get_watchlist_codes(db)
    success_count = 0
    fail_count = 0
    for stock_code in set(codes):
        if has_collected(db, stock_code):
            logger.info(f"[collect_watchlist_history] 股票 {stock_code} 已采集过，跳过")
            continue
        try:
            end_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
            
            # 判断是否为港股
            logger.info(f"[collect_watchlist_history] 开始判断股票 {stock_code} 是否为港股")
            is_hk = is_hk_stock(db, stock_code)
            logger.info(f"[collect_watchlist_history] 股票 {stock_code} 判断结果: {'港股' if is_hk else 'A股'}")
            
            if is_hk:
                # 港股处理逻辑
                logger.info(f"[collect_watchlist_history] 检测到港股代码: {stock_code}")
                df = ak.stock_hk_hist(symbol=stock_code, period='daily', start_date='19950101', end_date=end_date, adjust='')
                
                # 检查返回的DataFrame是否为空
                if df.empty:
                    logger.warning(f"港股 {stock_code} 返回空数据，可能该股票已退市或代码无效")
                    log_collection(db, stock_code, 0, 'fail', '返回空数据，可能该股票已退市或代码无效')
                    fail_count += 1
                    continue
                
                # 批量插入前，先删除该stock_code在港股历史行情表中的旧数据
                db.execute(
                    text("DELETE FROM historical_quotes_hk WHERE code = :code"),
                    {"code": stock_code}
                )
                db.commit()
                
                affected_rows = insert_historical_quotes_hk(db, stock_code, df)
                log_collection(db, stock_code, affected_rows, 'success')
                success_count += 1
            else:
                # A股处理逻辑（保持原有逻辑）
                logger.info(f"[collect_watchlist_history] 开始采集A股 {stock_code} 的历史数据")
                df = ak.stock_zh_a_hist(symbol=stock_code, period='daily', start_date='19950101', end_date=end_date, adjust='')
                
                # 检查返回的DataFrame是否为空
                if df.empty:
                    logger.warning(f"A股 {stock_code} 返回空数据，可能该股票已退市或代码无效")
                    log_collection(db, stock_code, 0, 'fail', '返回空数据，可能该股票已退市或代码无效')
                    fail_count += 1
                    continue
                
                # 批量插入前，先删除该stock_code的历史数据
                db.query(HistoricalQuotes).filter(HistoricalQuotes.code == stock_code).delete()
                db.commit()
                affected_rows = insert_historical_quotes(db, stock_code, df)
                log_collection(db, stock_code, affected_rows, 'success')
                success_count += 1
        except Exception as e:
            db.rollback()
            error_msg = str(e)
            logger.error(f"[collect_watchlist_history] 采集股票 {stock_code} 失败: {error_msg}", exc_info=True)
            try:
                log_collection(db, stock_code, 0, 'fail', error_msg)
            except Exception as log_error:
                logger.error(f"记录采集失败日志时出错: {log_error}")
            fail_count += 1
            print(f"[collect_watchlist_history] 采集 {stock_code} 失败: {error_msg}")
        time.sleep(10)
    return {"success": success_count, "fail": fail_count}
