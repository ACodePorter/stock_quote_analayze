#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据采集系统
"""

import requests
import json

def test_system():
    """测试整个数据采集系统"""
    print("=== 测试数据采集系统 ===")
    
    # 1. 测试API服务（5000端口）
    print("\n1. 测试API服务（5000端口）...")
    try:
        response = requests.get("http://localhost:5000/data-collection/stock-list", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API服务正常，获取到 {data.get('total', 0)} 只股票")
        else:
            print(f"❌ API服务异常，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ API服务连接失败: {e}")
    
    # 2. 测试Vite代理（8001端口）
    print("\n2. 测试Vite代理（8001端口）...")
    try:
        response = requests.get("http://localhost:8001/api/data-collection/stock-list", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Vite代理正常，获取到 {data.get('total', 0)} 只股票")
        else:
            print(f"❌ Vite代理异常，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ Vite代理连接失败: {e}")
    
    # 3. 测试数据采集API
    print("\n3. 测试数据采集API...")
    try:
        # 使用测试模式
        request_data = {
            "start_date": "2025-09-01",
            "end_date": "2025-09-03",
            "test_mode": True
        }
        
        response = requests.post("http://localhost:5000/data-collection/historical", 
                               json=request_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 数据采集API正常，任务ID: {data.get('task_id')}")
            print(f"   状态: {data.get('status')}")
        else:
            print(f"❌ 数据采集API异常，状态码: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 数据采集API连接失败: {e}")
    
    print("\n=== 测试完成 ===")
    print("\n现在可以访问以下地址：")
    print("1. Vue组件版本: http://localhost:8001/datacollect")
    print("2. 静态HTML版本: http://localhost:5000/admin/datacollect.html")

if __name__ == "__main__":
    test_system()
