#!/usr/bin/env python3
"""
检查operation_logs表的实际结构
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def check_operation_logs_actual_structure():
    """检查operation_logs表的实际结构"""
    
    print("🔍 检查operation_logs表实际结构")
    print("=" * 60)
    
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
                        
                    # 检查字段值的分布
                    print(f"\n📊 字段值分布:")
                    
                    # 检查每个字段的非空值数量
                    for col in columns:
                        col_name = col['column_name']
                        cur.execute(f"SELECT COUNT(*) FROM operation_logs WHERE {col_name} IS NOT NULL")
                        non_null_count = cur.fetchone()[0]
                        print(f"   - {col_name}: {non_null_count}/{count} 非空值")
                        
                        # 对于字符串字段，显示一些示例值
                        if col['data_type'] in ['character varying', 'text'] and non_null_count > 0:
                            cur.execute(f"SELECT DISTINCT {col_name} FROM operation_logs WHERE {col_name} IS NOT NULL LIMIT 5")
                            sample_values = cur.fetchall()
                            sample_str = ", ".join([str(row[0]) for row in sample_values])
                            print(f"     示例值: {sample_str}")
            else:
                print("❌ operation_logs表不存在")
                
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
    
    print("\n" + "=" * 60)
    print("📝 分析:")
    print("1. 根据实际结构调整API配置")
    print("2. 修改前端显示逻辑")
    print("3. 确保字段名与实际表结构匹配")

if __name__ == "__main__":
    check_operation_logs_actual_structure() 