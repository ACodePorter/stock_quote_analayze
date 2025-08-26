#!/usr/bin/env python3
"""
测试指数API的脚本，诊断获取指数数据失败的问题
"""

import requests
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# 添加后端API路径
sys.path.append('backend_api')
from config import DATABASE_CONFIG

def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    try:
        engine = create_engine(DATABASE_CONFIG["url"])
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ 数据库连接成功")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def check_table_exists():
    """检查指数表是否存在"""
    print("\n🔍 检查指数表是否存在...")
    try:
        engine = create_engine(DATABASE_CONFIG["url"])
        with engine.connect() as conn:
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'index_realtime_quotes'
            """))
            tables = result.fetchall()
            
            if tables:
                print("✅ 指数表 index_realtime_quotes 存在")
                
                # 检查表中的数据
                result = conn.execute(text("SELECT COUNT(*) FROM index_realtime_quotes"))
                count = result.scalar()
                print(f"   - 表中记录数: {count}")
                
                if count > 0:
                    # 显示前几条数据
                    result = conn.execute(text("SELECT * FROM index_realtime_quotes LIMIT 3"))
                    rows = result.fetchall()
                    print("   - 前3条数据:")
                    for i, row in enumerate(rows):
                        print(f"     {i+1}. {row}")
                else:
                    print("   ⚠️ 表中没有数据")
                
                return True
            else:
                print("❌ 指数表 index_realtime_quotes 不存在")
                return False
                
    except Exception as e:
        print(f"❌ 检查表失败: {e}")
        return False

def check_industry_table_structure():
    """检查行业板块表结构"""
    print("\n🔍 检查行业板块表结构...")
    try:
        engine = create_engine(DATABASE_CONFIG["url"])
        with engine.connect() as conn:
            # 获取表的列信息
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'industry_board_realtime_quotes'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            
            if columns:
                print("   📋 行业板块表结构:")
                for col in columns:
                    print(f"     - {col[0]}: {col[1]} (可空: {col[2]}, 默认值: {col[3]})")
            else:
                print("   ⚠️ 行业板块表不存在")
            
            return True
                
    except Exception as e:
        print(f"❌ 检查行业板块表结构失败: {e}")
        return False

def check_table_structure():
    """检查表的详细结构"""
    print("\n🔍 检查指数表结构...")
    try:
        engine = create_engine(DATABASE_CONFIG["url"])
        with engine.connect() as conn:
            # 获取表的列信息
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'index_realtime_quotes'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            
            print("   📋 表结构:")
            for col in columns:
                print(f"     - {col[0]}: {col[1]} (可空: {col[2]}, 默认值: {col[3]})")
            
            return True
                
    except Exception as e:
        print(f"❌ 检查表结构失败: {e}")
        return False

def test_index_api_directly():
    """直接测试指数API"""
    print("\n🔍 直接测试指数API...")
    base_url = "http://localhost:5000"
    
    try:
        # 测试不带参数的请求
        print("   测试不带参数的请求...")
        response = requests.get(f"{base_url}/api/quotes/indices")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ API请求成功")
            print(f"   - 响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   ❌ API请求失败: {response.text}")
            
    except Exception as e:
        print(f"   ❌ API测试失败: {e}")
    
    try:
        # 测试带参数的请求
        print("\n   测试带参数的请求...")
        params = {
            'page': 1,
            'page_size': 10,
            'sort_by': 'pct_chg'
        }
        response = requests.get(f"{base_url}/api/quotes/indices", params=params)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ 带参数API请求成功")
            print(f"   - 响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   ❌ 带参数API请求失败: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 带参数API测试失败: {e}")

def check_backend_logs():
    """检查后端日志"""
    print("\n🔍 检查后端日志...")
    try:
        # 检查是否有日志文件
        log_files = [
            "backend_api/app.log",
            "backend_api/error.log",
            "logs/app.log",
            "logs/error.log"
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                print(f"   📄 找到日志文件: {log_file}")
                # 读取最后几行
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"   - 最后5行日志:")
                        for line in lines[-5:]:
                            print(f"     {line.strip()}")
            else:
                print(f"   ⚠️ 日志文件不存在: {log_file}")
                
    except Exception as e:
        print(f"   ❌ 检查日志失败: {e}")

def main():
    """主函数"""
    print("🚀 开始诊断指数API问题...")
    
    # 1. 测试数据库连接
    if not test_database_connection():
        print("\n❌ 数据库连接失败，无法继续测试")
        return
    
    # 2. 检查指数表结构
    check_table_structure()
    
    # 3. 检查行业板块表结构
    check_industry_table_structure()
    
    # 4. 检查表是否存在
    if not check_table_exists():
        print("\n❌ 指数表不存在，这是问题的根源")
        return
    
    # 5. 测试API
    test_index_api_directly()
    
    # 6. 检查日志
    check_backend_logs()
    
    print("\n🏁 诊断完成")

if __name__ == "__main__":
    main()
