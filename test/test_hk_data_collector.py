"""
港股数据采集器测试
测试港股实时行情和历史行情数据采集功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend_core.data_collectors.akshare.hk_realtime import HKRealtimeQuoteCollector
from backend_core.data_collectors.akshare.hk_historical import HKHistoricalQuoteCollector
from backend_core.config.config import DATA_COLLECTORS
from backend_core.database.db import SessionLocal
from sqlalchemy import text
from datetime import datetime, timedelta

def test_hk_realtime_collector():
    """测试港股实时行情采集器"""
    print("=" * 60)
    print("测试港股实时行情采集器")
    print("=" * 60)
    
    try:
        collector = HKRealtimeQuoteCollector(DATA_COLLECTORS.get('akshare', {}))
        
        # 测试初始化数据库
        print("\n1. 测试数据库表初始化...")
        result = collector._init_db()
        if result:
            print("✓ 数据库表初始化成功")
        else:
            print("✗ 数据库表初始化失败")
            return False
        
        # 测试采集实时行情
        print("\n2. 测试采集港股实时行情数据...")
        success = collector.collect_quotes()
        if success:
            print("✓ 港股实时行情数据采集成功")
            
            # 验证数据是否入库
            session = SessionLocal()
            try:
                result = session.execute(text('''
                    SELECT COUNT(*) as count FROM stock_realtime_quote_hk
                ''')).fetchone()
                count = result[0] if result else 0
                print(f"✓ 数据库中共有 {count} 条港股实时行情记录")
                
                # 显示前5条记录
                result = session.execute(text('''
                    SELECT code, name, current_price, change_percent, update_time 
                    FROM stock_realtime_quote_hk 
                    ORDER BY update_time DESC 
                    LIMIT 5
                ''')).fetchall()
                
                if result:
                    print("\n前5条记录:")
                    for row in result:
                        print(f"  代码: {row[0]}, 名称: {row[1]}, 最新价: {row[2]}, 涨跌幅: {row[3]}, 更新时间: {row[4]}")
            finally:
                session.close()
        else:
            print("✗ 港股实时行情数据采集失败")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hk_historical_collector():
    """测试港股历史行情采集器"""
    print("\n" + "=" * 60)
    print("测试港股历史行情采集器")
    print("=" * 60)
    
    try:
        collector = HKHistoricalQuoteCollector(DATA_COLLECTORS.get('akshare', {}))
        
        # 测试初始化数据库
        print("\n1. 测试数据库表初始化...")
        result = collector._init_db()
        if result:
            print("✓ 数据库表初始化成功")
        else:
            print("✗ 数据库表初始化失败")
            return False
        
        # 测试采集历史行情（采集昨天的数据，避免今天可能没有数据）
        print("\n2. 测试采集港股历史行情数据...")
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        print(f"   采集日期: {yesterday}")
        
        success = collector.collect_historical_quotes(yesterday)
        if success:
            print("✓ 港股历史行情数据采集成功")
            
            # 验证数据是否入库
            session = SessionLocal()
            try:
                result = session.execute(text('''
                    SELECT COUNT(*) as count FROM historical_quotes_hk
                    WHERE date = :date
                '''), {'date': datetime.strptime(yesterday, '%Y%m%d').strftime('%Y-%m-%d')}).fetchone()
                count = result[0] if result else 0
                print(f"✓ 数据库中日期 {yesterday} 共有 {count} 条港股历史行情记录")
                
                # 显示前5条记录
                result = session.execute(text('''
                    SELECT code, name, date, open, close, volume, change_percent 
                    FROM historical_quotes_hk 
                    WHERE date = :date
                    ORDER BY code 
                    LIMIT 5
                '''), {'date': datetime.strptime(yesterday, '%Y%m%d').strftime('%Y-%m-%d')}).fetchall()
                
                if result:
                    print("\n前5条记录:")
                    for row in result:
                        print(f"  代码: {row[0]}, 名称: {row[1]}, 日期: {row[2]}, 开盘: {row[3]}, 收盘: {row[4]}, 成交量: {row[5]}, 涨跌幅: {row[6]}")
            finally:
                session.close()
        else:
            print("✗ 港股历史行情数据采集失败")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_tables():
    """测试数据库表结构"""
    print("\n" + "=" * 60)
    print("测试数据库表结构")
    print("=" * 60)
    
    session = SessionLocal()
    try:
        tables = [
            'stock_basic_info_hk',
            'stock_realtime_quote_hk',
            'historical_quotes_hk',
            'hk_realtime_collect_operation_logs',
            'hk_historical_collect_operation_logs'
        ]
        
        for table in tables:
            try:
                result = session.execute(text(f'''
                    SELECT COUNT(*) as count FROM {table}
                ''')).fetchone()
                count = result[0] if result else 0
                print(f"✓ 表 {table} 存在，共有 {count} 条记录")
            except Exception as e:
                print(f"✗ 表 {table} 不存在或查询失败: {e}")
    finally:
        session.close()

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("港股数据采集器测试开始")
    print("=" * 60)
    
    # 测试数据库表结构
    test_database_tables()
    
    # 测试实时行情采集器
    realtime_result = test_hk_realtime_collector()
    
    # 测试历史行情采集器（需要先有实时行情数据，因为历史采集器会从基本信息表获取股票列表）
    if realtime_result:
        historical_result = test_hk_historical_collector()
    else:
        print("\n跳过历史行情采集测试（因为实时行情采集失败）")
        historical_result = False
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"实时行情采集测试: {'✓ 通过' if realtime_result else '✗ 失败'}")
    print(f"历史行情采集测试: {'✓ 通过' if historical_result else '✗ 失败'}")
    
    if realtime_result and historical_result:
        print("\n✓ 所有测试通过！")
        return True
    else:
        print("\n✗ 部分测试失败，请检查日志")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

