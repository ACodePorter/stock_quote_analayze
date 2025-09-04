#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的扩展涨跌幅计算器
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend_core.database.db import SessionLocal
from backend_core.data_collectors.tushare.extended_change_calculator import ExtendedChangeCalculator
import logging
from sqlalchemy import text

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_extended_change_calculator():
    """测试修改后的扩展涨跌幅计算器"""
    logger.info("🧪 开始测试修改后的扩展涨跌幅计算器...")
    
    session = SessionLocal()
    try:
        target_date = "2025-09-03"
        calculator = ExtendedChangeCalculator(session)
        
        # 测试计算
        logger.info(f"📊 开始计算日期 {target_date} 的扩展涨跌幅...")
        result = calculator.calculate_for_date(target_date)
        
        logger.info(f"✅ 计算完成:")
        logger.info(f"  - 总计股票: {result['total']}")
        logger.info(f"  - 成功计算: {result['success']}")
        logger.info(f"  - 失败计算: {result['failed']}")
        
        if result['details']:
            logger.info(f"  - 失败详情（前5个）:")
            for detail in result['details'][:5]:
                logger.info(f"    * {detail}")
        
        # 检查计算状态
        logger.info("📈 检查计算状态...")
        status = calculator.get_calculation_status(target_date)
        
        logger.info(f"📊 计算状态:")
        logger.info(f"  - 总记录数: {status['total_records']}")
        logger.info(f"  - 5日涨跌幅: {status['five_day']['calculated']}/{status['total_records']} ({status['five_day']['completion_rate']}%)")
        logger.info(f"  - 10日涨跌幅: {status['ten_day']['calculated']}/{status['total_records']} ({status['ten_day']['completion_rate']}%)")
        logger.info(f"  - 60日涨跌幅: {status['sixty_day']['calculated']}/{status['total_records']} ({status['sixty_day']['completion_rate']}%)")
        
        # 验证一些具体的计算结果
        logger.info("🔍 验证具体计算结果...")
        result = session.execute(text("""
            SELECT 
                code,
                five_day_change_percent,
                ten_day_change_percent,
                sixty_day_change_percent
            FROM historical_quotes 
            WHERE date = :target_date
            AND (five_day_change_percent IS NOT NULL 
                 OR ten_day_change_percent IS NOT NULL 
                 OR sixty_day_change_percent IS NOT NULL)
            ORDER BY code
            LIMIT 10
        """), {"target_date": target_date})
        
        calculated_stocks = result.fetchall()
        logger.info(f"📋 已计算涨跌幅的股票示例（前10个）:")
        for stock in calculated_stocks:
            periods = []
            if stock[1] is not None:
                periods.append(f"5日:{stock[1]:.2f}%")
            if stock[2] is not None:
                periods.append(f"10日:{stock[2]:.2f}%")
            if stock[3] is not None:
                periods.append(f"60日:{stock[3]:.2f}%")
            
            logger.info(f"  - {stock[0]}: {', '.join(periods)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {e}")
        return False
    finally:
        session.close()

def check_database_connection():
    """检查数据库连接"""
    logger.info("🔌 检查数据库连接...")
    
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

if __name__ == "__main__":
    logger.info("🚀 开始测试修改后的扩展涨跌幅计算器...")
    
    if check_database_connection():
        success = test_extended_change_calculator()
        if success:
            logger.info("✅ 测试完成")
        else:
            logger.error("❌ 测试失败")
            sys.exit(1)
    else:
        logger.error("❌ 数据库连接失败，无法进行测试")
        sys.exit(1)
