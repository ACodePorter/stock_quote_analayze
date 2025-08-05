# 测试日志API功能

import requests
import json
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:8000"

def test_logs_api():
    """测试日志API功能"""
    
    print("🧪 开始测试日志API...")
    
    # 1. 测试获取日志表列表
    print("\n1. 测试获取日志表列表")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/logs/tables")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试查询历史数据采集日志
    print("\n2. 测试查询历史数据采集日志")
    try:
        params = {
            "page": 1,
            "page_size": 10
        }
        response = requests.get(f"{BASE_URL}/api/admin/logs/query/historical_collect", params=params)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 3. 测试查询实时数据采集日志
    print("\n3. 测试查询实时数据采集日志")
    try:
        params = {
            "page": 1,
            "page_size": 10
        }
        response = requests.get(f"{BASE_URL}/api/admin/logs/query/realtime_collect", params=params)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 4. 测试查询自选股历史采集日志
    print("\n4. 测试查询自选股历史采集日志")
    try:
        params = {
            "page": 1,
            "page_size": 10
        }
        response = requests.get(f"{BASE_URL}/api/admin/logs/query/watchlist_history", params=params)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 5. 测试获取统计信息
    print("\n5. 测试获取统计信息")
    try:
        params = {
            "days": 7
        }
        response = requests.get(f"{BASE_URL}/api/admin/logs/stats/historical_collect", params=params)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 6. 测试获取最近日志
    print("\n6. 测试获取最近日志")
    try:
        params = {
            "limit": 5
        }
        response = requests.get(f"{BASE_URL}/api/admin/logs/recent/historical_collect", params=params)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n✅ 日志API测试完成")

if __name__ == "__main__":
    test_logs_api() 