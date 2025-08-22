#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试行情数据API
"""

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:5000"

def test_quotes_api():
    """测试行情数据API"""
    print("🧪 开始测试行情数据API...")
    
    # 测试股票行情数据
    print("\n📊 测试股票行情数据...")
    try:
        response = requests.get(f"{BASE_URL}/api/quotes/stocks?page=1&page_size=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 股票行情API调用成功")
            print(f"   状态: {data.get('success')}")
            print(f"   数据条数: {len(data.get('data', []))}")
            print(f"   总数: {data.get('total')}")
        else:
            print(f"❌ 股票行情API调用失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 股票行情API调用异常: {str(e)}")
    
    # 测试指数行情数据
    print("\n📈 测试指数行情数据...")
    try:
        response = requests.get(f"{BASE_URL}/api/quotes/indices?page=1&page_size=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 指数行情API调用成功")
            print(f"   状态: {data.get('success')}")
            print(f"   数据条数: {len(data.get('data', []))}")
            print(f"   总数: {data.get('total')}")
        else:
            print(f"❌ 指数行情API调用失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 指数行情API调用异常: {str(e)}")
    
    # 测试行业板块行情数据
    print("\n🏢 测试行业板块行情数据...")
    try:
        response = requests.get(f"{BASE_URL}/api/quotes/industries?page=1&page_size=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 行业板块行情API调用成功")
            print(f"   状态: {data.get('success')}")
            print(f"   数据条数: {len(data.get('data', []))}")
            print(f"   总数: {data.get('total')}")
        else:
            print(f"❌ 行业板块行情API调用失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 行业板块行情API调用异常: {str(e)}")
    
    # 测试统计数据
    print("\n📊 测试统计数据...")
    try:
        response = requests.get(f"{BASE_URL}/api/quotes/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 统计数据API调用成功")
            print(f"   状态: {data.get('success')}")
            if data.get('success'):
                stats = data.get('data', {})
                print(f"   股票总数: {stats.get('totalStocks')}")
                print(f"   指数总数: {stats.get('totalIndices')}")
                print(f"   行业板块总数: {stats.get('totalIndustries')}")
                print(f"   最后更新时间: {stats.get('lastUpdateTime')}")
        else:
            print(f"❌ 统计数据API调用失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 统计数据API调用异常: {str(e)}")
    
    # 测试刷新功能
    print("\n🔄 测试刷新功能...")
    try:
        response = requests.post(f"{BASE_URL}/api/quotes/refresh")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 刷新API调用成功")
            print(f"   状态: {data.get('success')}")
            print(f"   消息: {data.get('message')}")
        else:
            print(f"❌ 刷新API调用失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 刷新API调用异常: {str(e)}")

def test_search_and_filter():
    """测试搜索和过滤功能"""
    print("\n🔍 测试搜索和过滤功能...")
    
    # 测试股票搜索
    print("\n   测试股票搜索...")
    try:
        response = requests.get(f"{BASE_URL}/api/quotes/stocks?page=1&page_size=5&keyword=平安")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 股票搜索成功")
            print(f"      搜索结果: {len(data.get('data', []))} 条")
        else:
            print(f"   ❌ 股票搜索失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 股票搜索异常: {str(e)}")
    
    # 测试市场过滤
    print("\n   测试市场过滤...")
    try:
        response = requests.get(f"{BASE_URL}/api/quotes/stocks?page=1&page_size=5&market=sh")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 市场过滤成功")
            print(f"      上交所股票: {len(data.get('data', []))} 条")
        else:
            print(f"   ❌ 市场过滤失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 市场过滤异常: {str(e)}")

if __name__ == "__main__":
    print(f"🚀 行情数据API测试开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 测试目标: {BASE_URL}")
    
    try:
        test_quotes_api()
        test_search_and_filter()
        
        print(f"\n✅ 行情数据API测试完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
