#!/usr/bin/env python3
"""
检查operation_logs表的实际结构
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def check_operation_logs_structure():
    """检查operation_logs表结构"""
    
    print("🔍 检查operation_logs表结构")
    print("=" * 50)
    
    try:
        # 连接数据库
        conn = psycopg2.connect(
            host="localhost",
            database="stock_analysis",
            user="postgres",
            password="123456"
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 检查表是否存在
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'operation_logs'
                )
            """)
            
            exists = cur.fetchone()[0]
            print(f"📊 operation_logs表是否存在: {exists}")
            
            if exists:
                # 检查表结构
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = 'operation_logs'
                    ORDER BY ordinal_position
                """)
                
                columns = cur.fetchall()
                print(f"\n📊 operation_logs表实际结构:")
                for col in columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                    print(f"   - {col['column_name']}: {col['data_type']} {nullable}{default}")
                
                # 检查记录数
                cur.execute("SELECT COUNT(*) FROM operation_logs")
                count = cur.fetchone()[0]
                print(f"\n📊 operation_logs表记录数: {count}")
                
                if count > 0:
                    # 查看前几条记录
                    cur.execute("SELECT * FROM operation_logs LIMIT 3")
                    records = cur.fetchall()
                    print(f"\n📊 前3条记录:")
                    for i, record in enumerate(records, 1):
                        print(f"   记录{i}: {dict(record)}")
            else:
                print("❌ operation_logs表不存在")
                
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
    
    print("\n" + "=" * 50)
    print("📝 分析:")
    print("1. 如果表存在但缺少operation_type字段，需要添加该字段")
    print("2. 如果表结构完全不对，可能需要重新创建表")
    print("3. 根据实际结构调整API配置或修改表结构")

if __name__ == "__main__":
    check_operation_logs_structure() 