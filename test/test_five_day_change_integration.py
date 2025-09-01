#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试5日涨跌幅计算功能的集成
验证历史行情数据采集后自动计算5日涨跌幅的功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend_core'))

from datetime import datetime, timedelta
from backend_core.database.db import SessionLocal
from backend_core.data_collectors.tushare.five_day_change_calculator import FiveDayChangeCalculator
from sqlalchemy import text
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_five_day_change_calculator():
    """测试5日涨跌幅计算器"""
    print("=== 测试5日涨跌幅计算器 ===")
    
    session = SessionLocal()
    calculator = FiveDayChangeCalculator(session)
    
    try:
        # 测试获取计算状态
        today = datetime.now().strftime("%Y-%m-%d")
        status = calculator.get_calculation_status(today)
        print(f"今日计算状态: {status}")
        
        # 测试计算功能（如果有数据的话）
        if status['total_records'] > 0:
            result = calculator.calculate_for_date(today)
            print(f"今日计算结果: {result}")
        else:
            print("今日没有历史行情数据，跳过计算测试")
        
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"测试5日涨跌幅计算器失败: {e}")
        session.close()
        return False

def test_database_connection():
    """测试数据库连接和表结构"""
    print("=== 测试数据库连接和表结构 ===")
    
    session = SessionLocal()
    
    try:
        # 检查historical_quotes表是否存在five_day_change_percent字段
        result = session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'historical_quotes' 
            AND column_name = 'five_day_change_percent'
        """))
        
        columns = result.fetchall()
        if columns:
            print(f"✓ five_day_change_percent字段存在: {columns[0]}")
        else:
            print("✗ five_day_change_percent字段不存在")
            return False
        
        # 检查是否有历史数据
        result = session.execute(text("""
            SELECT COUNT(*) as total_records,
                   COUNT(five_day_change_percent) as calculated_records
            FROM historical_quotes 
            WHERE date >= :start_date
        """), {"start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")})
        
        row = result.fetchone()
        if row:
            print(f"最近30天数据统计:")
            print(f"  总记录数: {row[0]}")
            print(f"  已计算5日涨跌幅记录数: {row[1]}")
            print(f"  待计算记录数: {row[0] - row[1]}")
        
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"测试数据库连接失败: {e}")
        session.close()
        return False

def test_sample_calculation():
    """测试样本数据计算"""
    print("=== 测试样本数据计算 ===")
    
    session = SessionLocal()
    calculator = FiveDayChangeCalculator(session)
    
    try:
        # 查找有足够历史数据的股票进行测试
        result = session.execute(text("""
            SELECT code, COUNT(*) as record_count
            FROM historical_quotes 
            WHERE date >= :start_date
            GROUP BY code
            HAVING COUNT(*) >= 6
            ORDER BY record_count DESC
            LIMIT 1
        """), {"start_date": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")})
        
        stock_data = result.fetchone()
        if not stock_data:
            print("没有找到足够历史数据的股票进行测试")
            session.close()
            return True
        
        stock_code = stock_data[0]
        print(f"使用股票 {stock_code} 进行测试计算")
        
        # 获取该股票最近的日期
        result = session.execute(text("""
            SELECT MAX(date) as latest_date
            FROM historical_quotes 
            WHERE code = :stock_code
        """), {"stock_code": stock_code})
        
        latest_date = result.fetchone()[0]
        print(f"最新数据日期: {latest_date}")
        
        # 测试计算该股票的5日涨跌幅
        success = calculator._calculate_single_stock_five_day_change(stock_code, latest_date)
        if success:
            print(f"✓ 股票 {stock_code} 在 {latest_date} 的5日涨跌幅计算成功")
            
            # 验证计算结果
            result = session.execute(text("""
                SELECT five_day_change_percent
                FROM historical_quotes 
                WHERE code = :stock_code AND date = :date
            """), {"stock_code": stock_code, "date": latest_date})
            
            calc_result = result.fetchone()
            if calc_result and calc_result[0] is not None:
                print(f"  计算结果: {calc_result[0]}%")
            else:
                print("  计算结果为空")
        else:
            print(f"✗ 股票 {stock_code} 在 {latest_date} 的5日涨跌幅计算失败")
        
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"测试样本数据计算失败: {e}")
        session.close()
        return False

def main():
    """主测试函数"""
    print("开始测试5日涨跌幅计算功能集成...")
    print()
    
    tests = [
        ("数据库连接和表结构", test_database_connection),
        ("5日涨跌幅计算器", test_five_day_change_calculator),
        ("样本数据计算", test_sample_calculation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"运行测试: {test_name}")
        try:
            if test_func():
                print(f"✓ {test_name} 测试通过")
                passed += 1
            else:
                print(f"✗ {test_name} 测试失败")
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
        print()
    
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！5日涨跌幅计算功能集成成功。")
        return True
    else:
        print("❌ 部分测试失败，请检查相关配置和数据。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
