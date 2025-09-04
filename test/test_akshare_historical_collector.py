#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试akshare历史数据采集程序
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend_core.data_collectors.akshare.historical_collector import AkshareHistoricalCollector
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_akshare_collector():
    """测试akshare历史数据采集器"""
    logger.info("🧪 开始测试akshare历史数据采集器...")
    
    # 创建采集器
    collector = AkshareHistoricalCollector()
    
    try:
        # 测试获取股票列表
        logger.info("📋 测试获取股票列表...")
        stocks = collector.get_stock_list()
        logger.info(f"获取到 {len(stocks)} 只股票")
        
        if len(stocks) > 0:
            logger.info(f"前5只股票: {[stock['code'] for stock in stocks[:5]]}")
        
        # 测试检查已存在数据
        if len(stocks) > 0:
            test_stock = stocks[0]['code']
            logger.info(f"🔍 测试检查股票 {test_stock} 的已存在数据...")
            existing_dates = collector.check_existing_data(test_stock, "2025-08-01", "2025-09-03")
            logger.info(f"股票 {test_stock} 在指定日期范围内已有 {len(existing_dates)} 天数据")
            if existing_dates:
                logger.info(f"已存在日期示例: {existing_dates[:5]}")
        
        # 测试单只股票采集（测试模式）
        if len(stocks) > 0:
            test_stock = stocks[0]['code']
            logger.info(f"📊 测试采集股票 {test_stock} 的历史数据...")
            
            # 使用较短的日期范围进行测试
            result = collector.collect_single_stock_data(test_stock, "2025-09-01", "2025-09-03")
            
            if result:
                logger.info(f"✅ 股票 {test_stock} 采集成功")
            else:
                logger.warning(f"⚠️ 股票 {test_stock} 采集失败")
        
        # 测试批量采集（测试模式）
        logger.info("🚀 测试批量采集（测试模式）...")
        test_stocks = [stock['code'] for stock in stocks[:3]]  # 只测试前3只股票
        logger.info(f"测试股票: {test_stocks}")
        
        result = collector.collect_historical_data("2025-09-01", "2025-09-03", test_stocks)
        
        logger.info(f"📈 批量采集结果:")
        logger.info(f"  - 总计股票: {result['total']}")
        logger.info(f"  - 成功采集: {result['success']}")
        logger.info(f"  - 采集失败: {result['failed']}")
        logger.info(f"  - 新增数据: {result['collected']} 条")
        logger.info(f"  - 跳过数据: {result['skipped']} 条")
        
        if result['failed_details']:
            logger.warning("失败详情:")
            for detail in result['failed_details']:
                logger.warning(f"  - {detail}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {e}")
        return False
    finally:
        collector.session.close()

def check_database_connection():
    """检查数据库连接"""
    logger.info("🔌 检查数据库连接...")
    
    from backend_core.database.db import SessionLocal
    from sqlalchemy import text
    
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT 1"))
        logger.info("✅ 数据库连接正常")
        return True
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        return False
    finally:
        session.close()

def check_akshare_availability():
    """检查akshare是否可用"""
    logger.info("🔍 检查akshare可用性...")
    
    try:
        import akshare as ak
        
        # 测试获取股票列表
        stock_info = ak.stock_info_a_code_name()
        logger.info(f"✅ akshare可用，获取到 {len(stock_info)} 只股票信息")
        return True
        
    except Exception as e:
        logger.error(f"❌ akshare不可用: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 开始测试akshare历史数据采集器...")
    
    # 检查依赖
    if not check_database_connection():
        logger.error("❌ 数据库连接失败，无法进行测试")
        sys.exit(1)
    
    if not check_akshare_availability():
        logger.error("❌ akshare不可用，无法进行测试")
        sys.exit(1)
    
    # 执行测试
    success = test_akshare_collector()
    if success:
        logger.info("✅ 测试完成")
    else:
        logger.error("❌ 测试失败")
        sys.exit(1)
