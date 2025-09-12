#!/usr/bin/env python3
"""
测试登出API功能
"""

import requests
import json

def test_logout_api():
    """测试登出API"""
    base_url = "http://localhost:5000"
    
    print("=== 测试登出API功能 ===")
    
    # 测试1：直接调用登出API（不需要认证）
    print("\n1. 测试直接调用登出API（不需要认证）")
    try:
        response = requests.post(f"{base_url}/api/admin/auth/logout")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 登出API正常工作")
        else:
            print("❌ 登出API返回错误状态码")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 测试2：使用无效token调用登出API
    print("\n2. 测试使用无效token调用登出API")
    try:
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.post(f"{base_url}/api/admin/auth/logout", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 登出API正确处理无效token")
        else:
            print("❌ 登出API对无效token处理异常")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 测试3：检查API文档
    print("\n3. 检查API文档")
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"API文档状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ API文档可访问")
        else:
            print("❌ API文档不可访问")
    except Exception as e:
        print(f"❌ 无法访问API文档: {e}")

if __name__ == "__main__":
    test_logout_api()
