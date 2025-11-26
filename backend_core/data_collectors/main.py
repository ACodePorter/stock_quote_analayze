import sys
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
from backend_core.data_collectors.akshare.realtime import AkshareRealtimeQuoteCollector
from backend_core.data_collectors.akshare.historical_turnover_rate import HistoricalTurnoverRateCollector
from backend_core.data_collectors.tushare.historical import HistoricalQuoteCollector
from backend_core.data_collectors.tushare.realtime import RealtimeQuoteCollector
from backend_core.config.config import DATA_COLLECTORS
from backend_core.data_collectors.akshare.realtime_index_spot_ak import RealtimeIndexSpotAkCollector
from backend_core.data_collectors.akshare.realtime_stock_industry_board_ak import RealtimeStockIndustryBoardCollector
from backend_core.data_collectors.akshare.realtime_stock_notice_report_ak import AkshareStockNoticeReportCollector
from backend_core.data_collectors.akshare.hk_realtime import HKRealtimeQuoteCollector
from backend_core.data_collectors.akshare.hk_historical import HKHistoricalQuoteCollector
from apscheduler.schedulers.background import BackgroundScheduler
from backend_core.data_collectors.akshare.watchlist_history_collector import collect_watchlist_history
from backend_core.data_collectors.news_collector import NewsCollector
import time


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# 初始化采集器
ak_collector = AkshareRealtimeQuoteCollector(DATA_COLLECTORS.get('akshare', {}))
ak_turnover_collector = HistoricalTurnoverRateCollector(DATA_COLLECTORS.get('akshare', {}))
tushare_hist_collector = HistoricalQuoteCollector(DATA_COLLECTORS.get('tushare', {}))
tushare_realtime_collector = RealtimeQuoteCollector(DATA_COLLECTORS.get('tushare', {}))
index_collector = RealtimeIndexSpotAkCollector()
industry_board_collector = RealtimeStockIndustryBoardCollector()
notice_collector = AkshareStockNoticeReportCollector(DATA_COLLECTORS.get('akshare', {}))
news_collector = NewsCollector()
# 港股采集器
hk_realtime_collector = HKRealtimeQuoteCollector(DATA_COLLECTORS.get('akshare', {}))
hk_historical_collector = HKHistoricalQuoteCollector(DATA_COLLECTORS.get('akshare', {}))

scheduler = BlockingScheduler()

def collect_akshare_realtime():
    try:
        logging.info("[定时任务] AKShare 实时行情采集开始...")
        df = ak_collector.collect_quotes()
        # 可在此处保存数据到数据库或文件
        #logging.info(f"[定时任务] AKShare 实时行情采集完成，采集到 {len(df)} 条数据")
    except Exception as e:
        logging.error(f"[定时任务] AKShare 实时行情采集异常: {e}")

def collect_akshare_index_realtime(): 
    try:
        logging.info("[定时任务] AKShare 指数实时行情采集开始...")
        df = index_collector.collect_quotes()
        logging.info(f"[定时任务] AKShare 指数实时行情采集完成，采集到 {len(df)} 条数据")
    except Exception as e:
        logging.error(f"[定时任务] 实时行情采集异常: {e}")

def collect_tushare_historical():
    try:
        today = datetime.now()
        # 如果是周六、周日则不采集，工作日采集当天
        if today.weekday() in (5, 6):  # 5=周六，6=周日
            logging.info("[定时任务] 今天是周末，不执行 Tushare 历史行情采集。")
            return
        today = today.strftime('%Y%m%d')
        logging.info(f"[定时任务] Tushare 历史行情采集开始，日期: {today}")
        tushare_hist_collector.collect_historical_quotes(today)
        logging.info("[定时任务] Tushare 历史行情采集完成")
    except Exception as e:
        logging.error(f"[定时任务] Tushare 历史行情采集异常: {e}")

def collect_tushare_realtime():
    try:
        logging.info("[定时任务] Tushare 实时行情采集开始...")
        tushare_realtime_collector.collect_quotes()
        logging.info("[定时任务] Tushare 实时行情采集完成")
    except Exception as e:
        logging.error(f"[定时任务] Tushare 实时行情采集异常: {e}")

def collect_akshare_industry_board_realtime():
    try:
        logging.info("[定时任务] 行业板块实时行情采集开始...")
        industry_board_collector.run()
        logging.info("[定时任务] 行业板块实时行情采集完成")
    except Exception as e:
        logging.error(f"[定时任务] 行业板块实时行情采集异常: {e}")

def collect_akshare_stock_notices():
    try:
        logging.info("[定时任务] A股公告数据采集开始...")
        # 采集当日公告数据
        result = notice_collector.collect_stock_notices(symbol="全部")
        if result:
            logging.info("[定时任务] A股公告数据采集完成")
        else:
            logging.warning("[定时任务] A股公告数据采集失败")
    except Exception as e:
        logging.error(f"[定时任务] A股公告数据采集异常: {e}")

def collect_akshare_turnover_rate():
    try:
        logging.info("[定时任务] AKShare 历史换手率数据采集开始...")
        # 采集最近30天缺失的换手率数据
        success = ak_turnover_collector.collect_missing_turnover_rate(30)
        if success:
            logging.info("[定时任务] AKShare 历史换手率数据采集完成")
        else:
            logging.warning("[定时任务] AKShare 历史换手率数据采集部分失败")
    except Exception as e:
        logging.error(f"[定时任务] AKShare 历史换手率数据采集异常: {e}")

def run_watchlist_history_collection():
    try:
        logging.info("[定时任务] 自选股历史行情采集开始...")
        result = collect_watchlist_history()
        if result:
            logging.info("[定时任务] 自选股历史行情采集完成")
            print(f"自选股历史行情采集成功个股数量: {result.get('success', 0)}，失败个股数量: {result.get('fail', 0)}")
    except Exception as e:
        logging.error(f"[定时任务] 自选股历史行情采集异常: {e}")

def collect_market_news():
    """采集市场新闻任务"""
    try:
        logging.info("[定时任务] 市场新闻采集开始...")
        result = news_collector.collect_and_save_market_news()
        if result["success"]:
            logging.info(f"[定时任务] 市场新闻采集完成: {result['message']}")
        else:
            logging.error(f"[定时任务] 市场新闻采集失败: {result['message']}")
    except Exception as e:
        logging.error(f"[定时任务] 市场新闻采集异常: {e}")

def update_hot_news():
    """更新热门资讯任务"""
    try:
        logging.info("[定时任务] 热门资讯更新开始...")
        success = news_collector.update_hot_news()
        if success:
            logging.info("[定时任务] 热门资讯更新完成")
        else:
            logging.error("[定时任务] 热门资讯更新失败")
    except Exception as e:
        logging.error(f"[定时任务] 热门资讯更新异常: {e}")

def cleanup_old_news():
    """清理旧新闻任务"""
    try:
        logging.info("[定时任务] 旧新闻清理开始...")
        deleted_count = news_collector.cleanup_old_news(days=30)
        logging.info(f"[定时任务] 旧新闻清理完成，删除了 {deleted_count} 条记录")
    except Exception as e:
        logging.error(f"[定时任务] 旧新闻清理异常: {e}")

def collect_hk_realtime():
    """港股实时行情采集任务"""
    try:
        logging.info("[定时任务] 港股实时行情采集开始...")
        success = hk_realtime_collector.collect_quotes()
        if success:
            logging.info("[定时任务] 港股实时行情采集完成")
        else:
            logging.warning("[定时任务] 港股实时行情采集失败")
    except Exception as e:
        logging.error(f"[定时任务] 港股实时行情采集异常: {e}")

def collect_hk_historical():
    """港股历史行情采集任务"""
    try:
        today = datetime.now()
        # 如果是周六、周日则不采集，工作日采集当天
        if today.weekday() in (5, 6):  # 5=周六，6=周日
            logging.info("[定时任务] 今天是周末，不执行港股历史行情采集。")
            return
        today = today.strftime('%Y%m%d')
        logging.info(f"[定时任务] 港股历史行情采集开始，日期: {today}")
        success = hk_historical_collector.collect_historical_quotes(today)
        if success:
            logging.info("[定时任务] 港股历史行情采集完成")
        else:
            logging.warning("[定时任务] 港股历史行情采集失败")
    except Exception as e:
        logging.error(f"[定时任务] 港股历史行情采集异常: {e}")

# 定时任务配置
# 每个交易日上午9:00-11:30、下午13:30-15:30每30分钟采集一次A股实时行情
scheduler.add_job(
    collect_akshare_realtime,
    'cron',
    day_of_week='mon-fri',
    hour='9-11,13-16',
    minute='3,33',
    id='akshare_realtime',
    
)
# 每天收盘后，采集当天历史行情
scheduler.add_job(collect_tushare_historical, 'cron', hour='16', minute='7', id='tushare_historical')

# 每隔5分钟采集一次Tushare实时行情----由于tushare对普通会员，一小时只能调用1次，所以暂时不启用
#scheduler.add_job(collect_tushare_realtime, 'interval', minutes=5, id='tushare_realtime')


# 指数实时行情采集任务，每30分钟采集一次
# 工作日的交易时段内，每半小时采集一次指数实时行情
scheduler.add_job(
    collect_akshare_index_realtime,
    'cron',
    day_of_week='mon-fri',
    hour='9-11,13-16',
    minute='58',
    id='akshare_index_realtime',
)

# 行业板块实时行情采集任务，每小时采集一次
scheduler.add_job(
    collect_akshare_industry_board_realtime,
    'cron',
    day_of_week='mon-fri',
    hour='9-11,13-16',
    minute=2,
    id='akshare_industry_board_realtime',
)


# A股公告数据采集任务，每240分钟采集一次
scheduler.add_job(
    collect_akshare_stock_notices,
    'interval',
    minutes=180,
    id='akshare_stock_notices',
)

# 历史换手率数据采集任务，每30天采集一次
scheduler.add_job(
    collect_akshare_turnover_rate,
    'cron',
    day_of_week='mon-fri',
    hour='11',
    minute='12',
    id='akshare_turnover_rate',
)

# 自选股历史行情采集任务，每5分钟执行一次
scheduler.add_job(
    run_watchlist_history_collection,
    'cron',
    minute='*/5',
    id='watchlist_history_every_5_minutes',
)

# 市场新闻采集任务，每30分钟采集一次
scheduler.add_job(
    collect_market_news,
    'interval',
    minutes=50,
    id='market_news_collection',
)

# 热门资讯更新任务，每小时更新一次
scheduler.add_job(
    update_hot_news,
    'interval',
    hours=1,
    id='hot_news_update',
)

# 旧新闻清理任务，每天凌晨2点执行
scheduler.add_job(
    cleanup_old_news,
    'cron',
    hour=2,
    minute=0,
    id='old_news_cleanup',
)

# 港股实时行情采集任务，工作日交易时段内每30分钟采集一次
# 港股交易时间：工作日 9:30-12:00, 13:00-16:00
scheduler.add_job(
    collect_hk_realtime,
    'cron',
    day_of_week='mon-fri',
    hour='9-12,13-16',
    minute='11,57',
    id='hk_realtime',
)

# 港股历史行情采集任务，每天收盘后执行
scheduler.add_job(
    collect_hk_historical,
    'cron',
    day_of_week='mon-fri',
    hour=16,
    minute=12,
    id='hk_historical',
)

if __name__ == "__main__":
    logging.info("启动定时采集任务...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("定时任务已停止。") 