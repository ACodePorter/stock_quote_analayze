#!/usr/bin/env python3
"""
测试修复后的API接口
验证历史行情数据功能是否正常工作
"""

import sys
import requests
import json
from pathlib import Path

def test_api_endpoints():
    """测试API接口"""
    print("🧪 测试API接口")
    print("=" * 60)
    
    base_url = "http://localhost:5000/api/quotes"
    
    # 测试1: 获取股票列表
    print("\n1. 测试获取股票列表...")
    try:
        response = requests.get(f"{base_url}/stocks/list")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功: {len(data.get('data', []))} 只股票")
            if data.get('data'):
                sample = data['data'][0]
                print(f"   示例: {sample.get('code')} - {sample.get('name')}")
        else:
            print(f"   ❌ 失败: HTTP {response.status_code}")
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 测试2: 获取历史行情数据
    print("\n2. 测试获取历史行情数据...")
    try:
        params = {
            'code': '000001',
            'page': 1,
            'size': 5,
            'include_notes': True
        }
        response = requests.get(f"{base_url}/history", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功: {len(data.get('items', []))} 条历史数据")
            print(f"   总数: {data.get('total', 0)}")
            if data.get('items'):
                sample = data['items'][0]
                print(f"   示例: {sample.get('date')} - 收盘价: {sample.get('close')}")
        else:
            print(f"   ❌ 失败: HTTP {response.status_code}")
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 测试3: 获取股票实时行情
    print("\n3. 测试获取股票实时行情...")
    try:
        params = {
            'page': 1,
            'page_size': 5
        }
        response = requests.get(f"{base_url}/stocks", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功: {len(data.get('data', []))} 条实时数据")
            print(f"   总数: {data.get('total', 0)}")
        else:
            print(f"   ❌ 失败: HTTP {response.status_code}")
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")

def test_frontend_integration():
    """测试前端集成"""
    print("\n🔧 测试前端集成")
    print("=" * 60)
    
    # 检查前端文件
    quotes_view_file = Path("admin/src/views/QuotesView.vue")
    quotes_service_file = Path("admin/src/services/quotes.service.ts")
    
    if quotes_view_file.exists():
        print("✅ QuotesView.vue 文件存在")
        content = quotes_view_file.read_text(encoding='utf-8')
        if '历史行情数据' in content:
            print("✅ 包含历史行情数据标签页")
        if 'historicalStockCode' in content:
            print("✅ 包含历史行情数据相关变量")
    else:
        print("❌ QuotesView.vue 文件不存在")
    
    if quotes_service_file.exists():
        print("✅ quotes.service.ts 文件存在")
        content = quotes_service_file.read_text(encoding='utf-8')
        if 'getHistoricalQuotes' in content:
            print("✅ 包含历史行情数据服务方法")
        if 'getStockList' in content:
            print("✅ 包含股票列表服务方法")
    else:
        print("❌ quotes.service.ts 文件不存在")

def main():
    """主测试函数"""
    print("🚀 API接口修复验证测试")
    print("=" * 60)
    
    print("📋 修复内容:")
    print("1. ✅ 添加了 /api/quotes/stocks/list 接口")
    print("2. ✅ 添加了 /api/quotes/history 接口")
    print("3. ✅ 添加了 /api/quotes/history/{code}/{date} 更新接口")
    print("4. ✅ 修复了前端服务调用")
    
    # 测试API接口
    test_api_endpoints()
    
    # 测试前端集成
    test_frontend_integration()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    
    print("\n💡 使用说明:")
    print("1. 确保后端服务正在运行: python start_backend_api.py")
    print("2. 确保前端服务正在运行: cd admin && npm run dev")
    print("3. 访问管理端: http://localhost:3000/admin")
    print("4. 进入行情数据页面，点击'历史行情数据'标签页")
    print("5. 选择股票代码开始查询历史数据")
    
    print("\n🔧 如果仍有问题:")
    print("1. 检查后端服务是否正常运行")
    print("2. 检查数据库连接是否正常")
    print("3. 检查API路由是否正确注册")
    print("4. 查看浏览器控制台的详细错误信息")

if __name__ == "__main__":
    main()
