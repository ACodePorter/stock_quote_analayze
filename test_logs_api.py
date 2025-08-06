#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试系统日志API
"""

import requests
import json

def test_logs_api():
    """测试系统日志API"""
    print("🔍 测试系统日志API...")
    
    # 1. 登录获取token
    print("1. 登录获取token...")
    try:
        response = requests.post(
            'http://localhost:5000/api/admin/auth/login',
            data={'username': 'admin', 'password': '123456'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            print(f"✅ 登录成功，获取到token: {token[:20]}...")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return
    
    # 2. 测试日志查询API
    print("\n2. 测试日志查询API...")
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(
            'http://localhost:5000/api/admin/logs/query/historical_collect',
            headers=headers,
            timeout=5
        )
        
        print(f"📊 日志查询API状态: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 日志查询成功")
            print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"❌ 日志查询失败: {response.text}")
    except Exception as e:
        print(f"❌ 日志查询请求失败: {e}")
    
    # 3. 测试操作日志API
    print("\n3. 测试操作日志API...")
    try:
        response = requests.get(
            'http://localhost:5000/api/admin/operation-logs/query',
            headers=headers,
            timeout=5
        )
        
        print(f"📋 操作日志API状态: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 操作日志查询成功")
            print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"❌ 操作日志查询失败: {response.text}")
    except Exception as e:
        print(f"❌ 操作日志查询请求失败: {e}")

if __name__ == "__main__":
    test_logs_api() 