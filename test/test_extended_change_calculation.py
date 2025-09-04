#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试扩展涨跌幅计算功能
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend_core.database.db import SessionLocal
from backend_core.data_collectors.tushare.extended_change_calculator import ExtendedChangeCalculator
from backend_core.data_collectors.tushare.migrate_extended_change_fields import migrate_historical_quotes_table
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def test_extended_change_calculation():
    """
    测试扩展涨跌幅计算功能
    """
    try:
        logger.info("开始测试扩展涨跌幅计算功能...")
        
        # 1. 首先运行数据库迁移
        logger.info("步骤1: 运行数据库迁移...")
        if not migrate_historical_quotes_table():
            logger.error("数据库迁移失败，测试终止")
            return False
        
        # 2. 测试扩展涨跌幅计算器
        logger.info("步骤2: 测试扩展涨跌幅计算器...")
        session = SessionLocal()
        
        try:
            calculator = ExtendedChangeCalculator(session)
            
            # 获取最近的交易日期
            result = session.execute(text("""
                SELECT DISTINCT date 
                FROM historical_quotes 
                ORDER BY date DESC 
                LIMIT 1
            """))
            
            latest_date = result.fetchone()
            if not latest_date:
                logger.warning("没有找到历史行情数据，无法进行测试")
                return False
            
            test_date = latest_date[0]
            logger.info(f"使用测试日期: {test_date}")
            
            # 测试计算状态查询
            logger.info("测试计算状态查询...")
            status = calculator.get_calculation_status(test_date)
            logger.info(f"计算状态: {status}")
            
            # 测试扩展涨跌幅计算
            logger.info("测试扩展涨跌幅计算...")
            calc_result = calculator.calculate_for_date(test_date)
            logger.info(f"计算结果: {calc_result}")
            
            # 验证计算结果
            if calc_result['total'] > 0:
                logger.info(f"测试成功！总计 {calc_result['total']} 只股票，成功计算 {calc_result['success']} 只")
                
                # 查询一些示例数据
                sample_result = session.execute(text("""
                    SELECT code, name, five_day_change_percent, ten_day_change_percent, sixty_day_change_percent
                    FROM historical_quotes 
                    WHERE date = :date 
                    AND five_day_change_percent IS NOT NULL
                    LIMIT 5
                """), {"date": test_date})
                
                samples = sample_result.fetchall()
                logger.info("示例计算结果:")
                for sample in samples:
                    logger.info(f"  股票 {sample[0]} ({sample[1]}): 5日={sample[2]}%, 10日={sample[3]}%, 60日={sample[4]}%")
                
                return True
            else:
                logger.warning("没有需要计算的股票数据")
                return True
                
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"测试扩展涨跌幅计算功能失败: {e}")
        return False

def test_batch_calculation():
    """
    测试批量计算功能
    """
    try:
        logger.info("开始测试批量计算功能...")
        
        session = SessionLocal()
        
        try:
            calculator = ExtendedChangeCalculator(session)
            
            # 获取最近7天的日期范围
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            logger.info(f"测试批量计算日期范围: {start_date} 到 {end_date}")
            
            batch_result = calculator.calculate_batch_for_date_range(start_date, end_date)
            logger.info(f"批量计算结果: {batch_result}")
            
            return True
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"测试批量计算功能失败: {e}")
        return False

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("开始测试扩展涨跌幅计算功能")
    logger.info("=" * 50)
    
    # 测试基本功能
    success1 = test_extended_change_calculation()
    
    # 测试批量计算功能
    success2 = test_batch_calculation()
    
    logger.info("=" * 50)
    if success1 and success2:
        logger.info("所有测试通过！扩展涨跌幅计算功能正常工作")
    else:
        logger.error("部分测试失败，请检查日志")
    logger.info("=" * 50)
