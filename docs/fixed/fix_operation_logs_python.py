#!/usr/bin/env python3
"""
修复operation_logs表的Python脚本
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def fix_operation_logs_table():
    """修复operation_logs表"""
    
    print("🔧 修复operation_logs表")
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
            # 1. 检查表是否存在
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'operation_logs'
                )
            """)
            
            exists = cur.fetchone()[0]
            print(f"📊 operation_logs表是否存在: {exists}")
            
            if not exists:
                # 创建表
                print("🔨 创建operation_logs表...")
                cur.execute("""
                    CREATE TABLE operation_logs (
                        id SERIAL PRIMARY KEY,
                        operation_type VARCHAR(100) NOT NULL,
                        operation_desc TEXT,
                        affected_rows INTEGER DEFAULT 0,
                        status VARCHAR(20) NOT NULL DEFAULT 'success',
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建索引
                cur.execute("CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at)")
                cur.execute("CREATE INDEX idx_operation_logs_status ON operation_logs(status)")
                cur.execute("CREATE INDEX idx_operation_logs_operation_type ON operation_logs(operation_type)")
                
                print("✅ 表创建完成")
            else:
                # 检查并添加缺失的字段
                print("🔍 检查表字段...")
                
                # 获取现有字段
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'operation_logs'
                """)
                
                existing_columns = [row['column_name'] for row in cur.fetchall()]
                print(f"📊 现有字段: {existing_columns}")
                
                # 需要的字段
                required_columns = {
                    'operation_type': 'VARCHAR(100) NOT NULL DEFAULT \'unknown\'',
                    'operation_desc': 'TEXT',
                    'affected_rows': 'INTEGER DEFAULT 0',
                    'status': 'VARCHAR(20) NOT NULL DEFAULT \'success\'',
                    'error_message': 'TEXT',
                    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                }
                
                # 添加缺失的字段
                for col_name, col_def in required_columns.items():
                    if col_name not in existing_columns:
                        print(f"🔨 添加字段: {col_name}")
                        cur.execute(f"ALTER TABLE operation_logs ADD COLUMN {col_name} {col_def}")
                
                # 检查索引
                cur.execute("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename = 'operation_logs'
                """)
                
                existing_indexes = [row['indexname'] for row in cur.fetchall()]
                print(f"📊 现有索引: {existing_indexes}")
                
                # 创建缺失的索引
                indexes = [
                    ('idx_operation_logs_created_at', 'created_at'),
                    ('idx_operation_logs_status', 'status'),
                    ('idx_operation_logs_operation_type', 'operation_type')
                ]
                
                for index_name, column in indexes:
                    if index_name not in existing_indexes:
                        print(f"🔨 创建索引: {index_name}")
                        cur.execute(f"CREATE INDEX {index_name} ON operation_logs({column})")
            
            # 2. 检查数据
            cur.execute("SELECT COUNT(*) FROM operation_logs")
            count = cur.fetchone()[0]
            print(f"📊 当前记录数: {count}")
            
            if count == 0:
                # 插入测试数据
                print("🔨 插入测试数据...")
                test_data = [
                    ('user_login', '用户登录操作', 1, 'success', None),
                    ('data_export', '数据导出操作', 100, 'success', None),
                    ('system_backup', '系统备份操作', 0, 'success', None),
                    ('data_import', '数据导入操作', 50, 'partial_success', '部分数据导入失败'),
                    ('user_logout', '用户登出操作', 1, 'success', None),
                    ('config_update', '配置更新操作', 1, 'success', None),
                    ('data_cleanup', '数据清理操作', 200, 'success', None),
                    ('report_generation', '报告生成操作', 0, 'error', '报告模板不存在'),
                    ('user_creation', '用户创建操作', 1, 'success', None),
                    ('data_validation', '数据验证操作', 75, 'partial_success', '部分数据验证失败')
                ]
                
                for data in test_data:
                    cur.execute("""
                        INSERT INTO operation_logs (operation_type, operation_desc, affected_rows, status, error_message)
                        VALUES (%s, %s, %s, %s, %s)
                    """, data)
                
                print("✅ 测试数据插入完成")
            
            # 3. 显示最终结构
            print("\n📊 最终表结构:")
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'operation_logs'
                ORDER BY ordinal_position
            """)
            
            columns = cur.fetchall()
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"   - {col['column_name']}: {col['data_type']} {nullable}{default}")
            
            # 4. 显示数据统计
            cur.execute("SELECT COUNT(*) as total FROM operation_logs")
            total = cur.fetchone()[0]
            
            cur.execute("SELECT status, COUNT(*) as count FROM operation_logs GROUP BY status")
            status_stats = cur.fetchall()
            
            print(f"\n📊 数据统计:")
            print(f"   - 总记录数: {total}")
            for stat in status_stats:
                print(f"   - {stat['status']}: {stat['count']} 条")
            
            # 提交更改
            conn.commit()
            print("\n✅ 修复完成")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fix_operation_logs_table() 