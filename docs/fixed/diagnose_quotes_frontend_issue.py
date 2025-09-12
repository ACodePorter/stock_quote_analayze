#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断前端行情数据获取失败的问题
"""

import requests
import json
from datetime import datetime

def test_api_endpoints():
    """测试API端点的可达性"""
    print("🔍 诊断行情数据API可达性...")
    
    base_urls = [
        "http://localhost:5000",
        "http://localhost:5000/api",
        "http://localhost:5000/api/admin"
    ]
    
    endpoints = [
        "/quotes/stocks?page=1&page_size=5",
        "/quotes/stats"
    ]
    
    for base_url in base_urls:
        print(f"\n📍 测试基础URL: {base_url}")
        for endpoint in endpoints:
            full_url = base_url + endpoint
            try:
                response = requests.get(full_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ {endpoint} - 成功 (数据: {len(data.get('data', []))} 条)")
                else:
                    print(f"  ❌ {endpoint} - 失败 ({response.status_code})")
            except requests.exceptions.RequestException as e:
                print(f"  ❌ {endpoint} - 连接失败: {str(e)}")

def check_admin_auth_requirements():
    """检查admin API是否需要认证"""
    print("\n🔐 检查认证要求...")
    
    # 测试admin端点
    admin_endpoints = [
        "http://localhost:5000/api/admin/quotes/realtime",
        "http://localhost:5000/api/admin/users"
    ]
    
    for endpoint in admin_endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"  📊 {endpoint} - {response.status_code}")
            if response.status_code == 401:
                print(f"      需要认证")
            elif response.status_code == 404:
                print(f"      端点不存在")
        except Exception as e:
            print(f"  ❌ {endpoint} - 连接失败")

def suggest_solutions():
    """提供解决方案建议"""
    print("\n💡 解决方案建议:")
    print("1. 前端API基础URL配置问题")
    print("   - 当前: http://localhost:5000/api/admin")
    print("   - 行情API实际路径: http://localhost:5000/api/quotes")
    print("   - 解决方案: 修改环境配置或API路径")
    
    print("\n2. 可能的解决方案:")
    print("   A. 修改前端环境配置，使用正确的基础URL")
    print("   B. 在quotes service中使用完整的API路径")
    print("   C. 调整后端API路径结构")

if __name__ == "__main__":
    print(f"🚀 开始诊断行情数据获取问题 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_api_endpoints()
    check_admin_auth_requirements()
    suggest_solutions()
    
    print(f"\n✅ 诊断完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
