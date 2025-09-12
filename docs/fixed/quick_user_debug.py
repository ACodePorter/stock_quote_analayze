#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速用户调试脚本
"""

import requests
import json

def test_backend_status():
    """测试后端状态"""
    print("=== 测试后端状态 ===")
    
    try:
        # 测试基础连接
        response = requests.get("http://localhost:5000/")
        print(f"基础连接: {response.status_code}")
        
        # 测试健康检查
        response = requests.get("http://localhost:5000/health")
        print(f"健康检查: {response.status_code}")
        
        # 测试API文档
        response = requests.get("http://localhost:5000/docs")
        print(f"API文档: {response.status_code}")
        
    except Exception as e:
        print(f"连接失败: {e}")

def test_user_api():
    """测试用户API（无需认证）"""
    print("\n=== 测试用户API（无需认证） ===")
    
    try:
        response = requests.get("http://localhost:5000/api/admin/users")
        print(f"用户API状态: {response.status_code}")
        print(f"响应内容: {response.text[:200]}...")
        
    except Exception as e:
        print(f"用户API测试失败: {e}")

def test_database():
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    
    try:
        # 尝试连接数据库
        import psycopg2
        
        # 这里需要根据实际配置调整
        conn = psycopg2.connect(
            host="localhost",
            database="stock_analysis",
            user="postgres",
            password="postgres"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"数据库连接成功，用户表记录数: {count}")
        
        cursor.close()
        conn.close()
        
    except ImportError:
        print("psycopg2未安装")
    except Exception as e:
        print(f"数据库连接失败: {e}")

def main():
    """主函数"""
    print("开始快速用户调试...")
    
    test_backend_status()
    test_user_api()
    test_database()
    
    print("\n=== 调试完成 ===")

if __name__ == "__main__":
    main()
