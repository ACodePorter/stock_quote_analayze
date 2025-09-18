#!/usr/bin/env python3
"""
测试PostgreSQL数据库连接
"""

import psycopg2
import pandas as pd
from sqlalchemy import create_engine

def test_postgres_connection():
    """测试PostgreSQL连接"""
    try:
        # 数据库连接信息
        db_url = "postgresql+psycopg2://postgres:qidianspacetime@localhost:5446/stock_analysis"
        
        print("🔌 测试PostgreSQL数据库连接...")
        print(f"连接URL: {db_url}")
        
        # 创建SQLAlchemy引擎
        engine = create_engine(db_url)
        
        # 测试连接
        with engine.connect() as conn:
            print("✅ 数据库连接成功！")
            
            # 检查表是否存在
            print("\n📋 检查表结构...")
            tables_result = pd.read_sql_query("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """, conn)
            
            print("数据库中的表:")
            for _, row in tables_result.iterrows():
                print(f"  - {row['table_name']}")
            
            # 检查stock_realtime_quote表结构
            if 'stock_realtime_quote' in tables_result['table_name'].values:
                print("\n📊 检查stock_realtime_quote表结构...")
                columns_result = pd.read_sql_query("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'stock_realtime_quote'
                    ORDER BY ordinal_position
                """, conn)
                
                print("表结构:")
                for _, row in columns_result.iterrows():
                    print(f"  - {row['column_name']}: {row['data_type']} {'(nullable)' if row['is_nullable'] == 'YES' else '(not null)'}")
                
                # 检查是否有trade_date字段
                has_trade_date = 'trade_date' in columns_result['column_name'].values
                print(f"\n✅ 包含trade_date字段: {has_trade_date}")
                
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
            else:
                print("❌ stock_realtime_quote表不存在")
                return False
                
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("🔧 PostgreSQL数据库连接测试")
    print("=" * 60)
    
    success = test_postgres_connection()
    
    if success:
        print("\n🎉 数据库测试成功！")
        print("自选股API修复应该能正常工作。")
    else:
        print("\n⚠️ 数据库测试失败，需要检查数据库连接和表结构。")

if __name__ == "__main__":
    main()
