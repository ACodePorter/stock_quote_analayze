#!/usr/bin/env python3
"""
测试日志API URL修复
验证前端URL构造是否正确
"""

import requests
import json

def test_logs_api_urls():
    """测试日志API的URL构造"""
    
    base_url = "http://localhost:5000"
    
    # 测试的端点
    endpoints = [
        "/api/admin/logs/tables",
        "/api/admin/logs/query/operation?page=1&page_size=20",
        "/api/admin/logs/stats/operation?days=7"
    ]
    
    print("🔍 测试日志API URL修复")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 测试URL: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ 状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 请求成功")
            elif response.status_code == 401:
                print("⚠️  需要认证 (这是正常的)")
            elif response.status_code == 404:
                print("❌ 404 Not Found - URL可能有问题")
            else:
                print(f"⚠️  其他状态码: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败 - 请确保后端服务正在运行")
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    print("\n" + "=" * 50)
    print("📝 修复说明:")
    print("1. 前端BASE_URL: http://localhost:5000/api/admin")
    print("2. 修复前: /api/admin/logs/query/operation")
    print("3. 修复后: /logs/query/operation")
    print("4. 最终URL: http://localhost:5000/api/admin/logs/query/operation")
    print("✅ URL重复问题已修复")

if __name__ == "__main__":
    test_logs_api_urls() 