#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资讯采集定时任务
"""

import schedule
import time
import logging
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_core.data_collectors.news_collector import NewsCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_collector.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def collect_market_news_job():
    """采集市场新闻任务"""
    logger.info("🔄 开始执行市场新闻采集任务...")
    
    collector = NewsCollector()
    try:
        result = collector.collect_and_save_market_news()
        if result["success"]:
            logger.info(f"✅ 市场新闻采集完成: {result['message']}")
        else:
            logger.error(f"❌ 市场新闻采集失败: {result['message']}")
    except Exception as e:
        logger.error(f"❌ 市场新闻采集异常: {e}")
    finally:
        collector.close()

def update_hot_news_job():
    """更新热门资讯任务"""
    logger.info("🔄 开始执行热门资讯更新任务...")
    
    collector = NewsCollector()
    try:
        success = collector.update_hot_news()
        if success:
            logger.info("✅ 热门资讯更新完成")
        else:
            logger.error("❌ 热门资讯更新失败")
    except Exception as e:
        logger.error(f"❌ 热门资讯更新异常: {e}")
    finally:
        collector.close()

def cleanup_old_news_job():
    """清理旧新闻任务"""
    logger.info("🔄 开始执行旧新闻清理任务...")
    
    collector = NewsCollector()
    try:
        deleted_count = collector.cleanup_old_news(days=30)
        logger.info(f"✅ 旧新闻清理完成，删除了 {deleted_count} 条记录")
    except Exception as e:
        logger.error(f"❌ 旧新闻清理异常: {e}")
    finally:
        collector.close()

def main():
    """主函数"""
    logger.info("🚀 资讯采集定时任务启动...")
    
    # 设置定时任务
    # 每30分钟采集一次市场新闻
    schedule.every(30).minutes.do(collect_market_news_job)
    
    # 每小时更新一次热门资讯
    schedule.every().hour.do(update_hot_news_job)
    
    # 每天凌晨2点清理旧新闻
    schedule.every().day.at("02:00").do(cleanup_old_news_job)
    
    # 启动时立即执行一次
    logger.info("🔄 启动时立即执行一次采集...")
    collect_market_news_job()
    
    logger.info("⏰ 定时任务已设置:")
    logger.info("  - 每30分钟采集市场新闻")
    logger.info("  - 每小时更新热门资讯")
    logger.info("  - 每天凌晨2点清理旧新闻")
    logger.info("🔄 开始运行定时任务...")
    
    # 运行定时任务
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("⏹️ 收到停止信号，正在退出...")
            break
        except Exception as e:
            logger.error(f"❌ 定时任务运行异常: {e}")
            time.sleep(60)  # 异常后等待1分钟再继续

if __name__ == "__main__":
    main()
