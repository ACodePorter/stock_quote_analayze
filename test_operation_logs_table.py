#!/usr/bin/env python3
"""
测试operation_logs表问题诊断
检查表是否存在以及字段结构
"""

import requests
import json
import psycopg2
from psycopg2.extras import RealDictCursor

def test_operation_logs_table():
    """测试operation_logs表"""
    
    print("🔍 诊断operation_logs表问题")
    print("=" * 60)
    
    # 1. 测试API端点
    print("\n1. 测试API端点")
    print("-" * 30)
    
    base_url = "http://localhost:5000"
    endpoints = [
        "/api/admin/logs/tables",
        "/api/admin/logs/query/operation?page=1&page_size=5",
        "/api/admin/logs/stats/operation"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 测试URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ 状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 请求成功")
                if endpoint.endswith("/tables"):
                    print(f"📊 可用表: {[table['table_name'] for table in data.get('tables', [])]}")
                elif endpoint.endswith("/stats/operation"):
                    print(f"📊 统计信息: {data}")
                else:
                    print(f"📊 查询结果: 共 {data.get('pagination', {}).get('total_count', 0)} 条记录")
            elif response.status_code == 500:
                print("❌ 500 内部服务器错误")
                try:
                    error_data = response.json()
                    print(f"❌ 错误详情: {error_data}")
                except:
                    print(f"❌ 错误响应: {response.text}")
            else:
                print(f"⚠️  其他状态码: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败 - 请确保后端服务正在运行")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    # 2. 直接检查数据库表
    print("\n\n2. 直接检查数据库表")
    print("-" * 30)
    
    try:
        # 连接数据库（需要根据实际配置调整）
        conn = psycopg2.connect(
            host="localhost",
            database="stock_analysis",
            user="postgres",
            password="123456"
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 检查表是否存在
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%log%'
                ORDER BY table_name
            """)
            
            tables = cur.fetchall()
            print("📊 数据库中的日志表:")
            for table in tables:
                print(f"   - {table['table_name']}")
            
            # 检查operation_logs表是否存在
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'operation_logs'
                )
            """)
            
            exists = cur.fetchone()[0]
            print(f"\n🔍 operation_logs表是否存在: {exists}")
            
            if exists:
                # 检查表结构
                cur.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'operation_logs'
                    ORDER BY ordinal_position
                """)
                
                columns = cur.fetchall()
                print(f"\n📊 operation_logs表结构:")
                for col in columns:
                    print(f"   - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
                
                # 检查记录数
                cur.execute("SELECT COUNT(*) FROM operation_logs")
                count = cur.fetchone()[0]
                print(f"\n📊 operation_logs表记录数: {count}")
                
                if count > 0:
                    # 查看前几条记录
                    cur.execute("""
                        SELECT * FROM operation_logs 
                        ORDER BY created_at DESC 
                        LIMIT 3
                    """)
                    
                    records = cur.fetchall()
                    print(f"\n📊 前3条记录:")
                    for i, record in enumerate(records, 1):
                        print(f"   记录{i}: {dict(record)}")
            else:
                print("❌ operation_logs表不存在，需要创建")
                
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("请检查数据库连接配置")
    
    print("\n" + "=" * 60)
    print("📝 诊断建议:")
    print("1. 如果operation_logs表不存在，需要创建该表")
    print("2. 如果表存在但字段不匹配，需要修改表结构或更新API配置")
    print("3. 检查数据库连接和权限")
    print("✅ 诊断完成")

if __name__ == "__main__":
    test_operation_logs_table() 