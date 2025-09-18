#!/usr/bin/env python3
"""
简单的数据库测试
"""

import sqlite3
import pandas as pd
import os

def test_database():
    """测试数据库"""
    db_path = "database/stock_analysis.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        
        # 检查表结构
        print("📋 检查stock_realtime_quote表结构...")
        result = pd.read_sql_query("PRAGMA table_info(stock_realtime_quote)", conn)
        print("表结构:")
        for _, row in result.iterrows():
            print(f"  - {row['name']}: {row['type']} {'(PK)' if row['pk'] else ''}")
        
        # 检查是否有trade_date字段
        has_trade_date = 'trade_date' in result['name'].values
        print(f"✅ 包含trade_date字段: {has_trade_date}")
        
        if has_trade_date:
            # 查询最新交易日期
            print("\n📅 查询最新交易日期...")
            latest_date_result = pd.read_sql_query("""
                SELECT MAX(trade_date) as latest_date 
                FROM stock_realtime_quote 
                WHERE change_percent IS NOT NULL AND change_percent != 0
            """, conn)
            
            if not latest_date_result.empty and latest_date_result.iloc[0]['latest_date'] is not None:
                latest_trade_date = latest_date_result.iloc[0]['latest_date']
                print(f"✅ 最新交易日期: {latest_trade_date}")
                
                # 查询该日期的数据
                print(f"\n📊 查询 {latest_trade_date} 的数据...")
                data_result = pd.read_sql_query(f"""
                    SELECT code, name, current_price, change_percent, trade_date
                    FROM stock_realtime_quote 
                    WHERE trade_date = '{latest_trade_date}'
                    LIMIT 5
                """, conn)
                
                print(f"查询到 {len(data_result)} 条数据:")
                for _, row in data_result.iterrows():
                    print(f"  - {row['name']} ({row['code']}): {row['current_price']} ({row['change_percent']}%)")
                
                return True
            else:
                print("❌ 未找到有效的交易日期数据")
                return False
        else:
            print("❌ 表结构缺少trade_date字段")
            return False
            
    except Exception as e:
        print(f"❌ 数据库测试失败: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    print("=" * 60)
    print("🔧 简单数据库测试")
    print("=" * 60)
    
    success = test_database()
    
    if success:
        print("\n🎉 数据库测试成功！")
        print("自选股API修复应该能正常工作。")
    else:
        print("\n⚠️ 数据库测试失败，需要检查数据库结构。")

if __name__ == "__main__":
    main()
