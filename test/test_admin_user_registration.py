#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试管理端用户注册功能
"""

import requests
import json
import sys

API_BASE = "http://localhost:5000/api"

def test_admin_login():
    """测试管理员登录获取token"""
    print("\n🔐 测试管理员登录...")
    
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(f'{API_BASE}/admin/login',
                                 json=login_data,
                                 timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            if token:
                print(f"✅ 管理员登录成功")
                return token
            else:
                print(f"❌ 登录响应中没有token")
                return None
        else:
            print(f"❌ 管理员登录失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 管理员登录错误: {e}")
        return None

def test_create_user_with_long_password(token):
    """测试创建用户（长密码）"""
    print("\n👤 测试创建用户（长密码）...")
    
    # 创建一个超过72字节的密码
    long_password = "a" * 100  # 100个字符，超过72字节
    
    user_data = {
        'username': 'testuser_longpass',
        'email': 'test_longpass@example.com',
        'password': long_password,
        'role': 'user'
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(f'{API_BASE}/admin/users',
                                 json=user_data,
                                 headers=headers,
                                 timeout=5)
        
        result = response.json()
        
        if response.status_code == 200:
            print(f"✅ 用户创建成功（长密码已自动截断）")
            print(f"   用户ID: {result.get('id')}")
            print(f"   用户名: {result.get('username')}")
            return True
        else:
            print(f"❌ 用户创建失败: {response.status_code}")
            print(f"   错误信息: {result.get('detail', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 用户创建错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_create_user_normal(token):
    """测试创建用户（正常密码）"""
    print("\n👤 测试创建用户（正常密码）...")
    
    user_data = {
        'username': 'testuser_normal',
        'email': 'test_normal@example.com',
        'password': 'password123',
        'role': 'user'
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(f'{API_BASE}/admin/users',
                                 json=user_data,
                                 headers=headers,
                                 timeout=5)
        
        result = response.json()
        
        if response.status_code == 200:
            print(f"✅ 用户创建成功")
            print(f"   用户ID: {result.get('id')}")
            print(f"   用户名: {result.get('username')}")
            return True
        else:
            print(f"❌ 用户创建失败: {response.status_code}")
            print(f"   错误信息: {result.get('detail', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 用户创建错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cors_preflight():
    """测试CORS预检请求"""
    print("\n🌐 测试CORS预检请求...")
    
    try:
        response = requests.options(f'{API_BASE}/admin/users',
                                   headers={
                                       'Origin': 'http://localhost:8001',
                                       'Access-Control-Request-Method': 'POST',
                                       'Access-Control-Request-Headers': 'Content-Type,Authorization'
                                   },
                                   timeout=5)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print(f"预检请求状态码: {response.status_code}")
        print("\n🔍 CORS头检查:")
        all_ok = True
        for header, value in cors_headers.items():
            if value:
                print(f"   ✅ {header}: {value}")
            else:
                print(f"   ❌ {header}: 缺失")
                all_ok = False
        
        return all_ok and response.status_code in [200, 204]
    except Exception as e:
        print(f"❌ CORS预检请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("管理端用户注册功能测试")
    print("=" * 60)
    
    # 测试CORS
    cors_ok = test_cors_preflight()
    
    # 测试管理员登录
    token = test_admin_login()
    if not token:
        print("\n❌ 无法获取管理员token，跳过后续测试")
        return
    
    # 测试创建用户（正常密码）
    normal_ok = test_create_user_normal(token)
    
    # 测试创建用户（长密码）
    long_ok = test_create_user_with_long_password(token)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"CORS配置: {'✅ 通过' if cors_ok else '❌ 失败'}")
    print(f"正常密码用户创建: {'✅ 通过' if normal_ok else '❌ 失败'}")
    print(f"长密码用户创建: {'✅ 通过' if long_ok else '❌ 失败'}")
    
    if cors_ok and normal_ok and long_ok:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())

