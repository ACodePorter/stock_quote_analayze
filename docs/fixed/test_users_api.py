#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户管理API
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/api/admin/auth/login"
USERS_URL = f"{BASE_URL}/api/admin/users"

def test_login():
    """测试登录获取token"""
    print("=== 测试登录 ===")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"登录状态码: {response.status_code}")
        print(f"登录响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                token = result.get("data", {}).get("access_token")
                print(f"获取到token: {token[:20]}...")
                return token
            else:
                print("登录失败，响应中没有success字段")
        else:
            print(f"登录请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"登录异常: {e}")
    
    return None

def test_get_users(token):
    """测试获取用户列表"""
    print("\n=== 测试获取用户列表 ===")
    
    if not token:
        print("没有token，跳过测试")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试不同参数
    test_cases = [
        {"page": 1, "pageSize": 20, "search": ""},
        {"page": 1, "pageSize": 10, "search": ""},
        {"page": 1, "pageSize": 20, "search": "admin"}
    ]
    
    for i, params in enumerate(test_cases):
        print(f"\n--- 测试用例 {i+1}: {params} ---")
        
        try:
            # 构建查询参数
            query_params = {
                "skip": (params["page"] - 1) * params["pageSize"],
                "limit": params["pageSize"]
            }
            
            if params["search"]:
                query_params["search"] = params["search"]
            
            response = requests.get(USERS_URL, headers=headers, params=query_params)
            print(f"请求URL: {response.url}")
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    
                    # 验证响应结构
                    if "data" in result and "total" in result:
                        users = result["data"]
                        total = result["total"]
                        print(f"✅ 用户数量: {len(users)}, 总数: {total}")
                        
                        if users:
                            print("用户列表:")
                            for user in users[:3]:  # 只显示前3个
                                print(f"  - ID: {user.get('id')}, 用户名: {user.get('username')}, 邮箱: {user.get('email')}")
                        else:
                            print("⚠️ 用户列表为空")
                    else:
                        print("❌ 响应结构不正确，缺少data或total字段")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"响应内容: {response.text}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")

def test_user_stats(token):
    """测试用户统计"""
    print("\n=== 测试用户统计 ===")
    
    if not token:
        print("没有token，跳过测试")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{USERS_URL}/stats", headers=headers)
        print(f"统计API状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"统计响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError as e:
                print(f"统计JSON解析失败: {e}")
                print(f"响应内容: {response.text}")
        else:
            print(f"统计API失败: {response.status_code}")
            print(f"错误响应: {response.text}")
            
    except Exception as e:
        print(f"统计API异常: {e}")

def main():
    """主函数"""
    print("开始测试用户管理API")
    print(f"测试时间: {datetime.now()}")
    print(f"基础URL: {BASE_URL}")
    
    # 测试登录
    token = test_login()
    
    if token:
        # 测试获取用户列表
        test_get_users(token)
        
        # 测试用户统计
        test_user_stats(token)
    else:
        print("登录失败，无法继续测试")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
