#!/usr/bin/env python3
"""
测试历史行情数据修复功能
验证修复后的API接口和前端功能是否正常工作
"""

import sys
import requests
import json
from pathlib import Path

def test_api_endpoints():
    """测试API接口"""
    print("🧪 测试修复后的API接口")
    print("=" * 60)
    
    base_url = "http://localhost:5000/api/quotes"
    
    # 测试1: 获取股票列表（移除DISTINCT）
    print("\n1. 测试获取股票列表（移除DISTINCT）...")
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
    
    # 测试2: 获取历史行情数据（不指定股票代码）
    print("\n2. 测试获取历史行情数据（不指定股票代码）...")
    try:
        params = {
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
                print(f"   示例: {sample.get('code')} - {sample.get('date')} - 收盘价: {sample.get('close')}")
        else:
            print(f"   ❌ 失败: HTTP {response.status_code}")
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 测试3: 获取指定股票的历史行情数据
    print("\n3. 测试获取指定股票的历史行情数据...")
    try:
        params = {
            'code': '000001',
            'page': 1,
            'size': 3,
            'include_notes': True
        }
        response = requests.get(f"{base_url}/history", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功: {len(data.get('items', []))} 条历史数据")
            print(f"   总数: {data.get('total', 0)}")
            if data.get('items'):
                sample = data['items'][0]
                print(f"   示例: {sample.get('code')} - {sample.get('date')} - 收盘价: {sample.get('close')}")
        else:
            print(f"   ❌ 失败: HTTP {response.status_code}")
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 测试4: 按日期范围筛选历史数据
    print("\n4. 测试按日期范围筛选历史数据...")
    try:
        params = {
            'code': '000001',
            'page': 1,
            'size': 3,
            'start_date': '2025-10-01',
            'end_date': '2025-10-31',
            'include_notes': True
        }
        response = requests.get(f"{base_url}/history", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功: {len(data.get('items', []))} 条历史数据")
            print(f"   总数: {data.get('total', 0)}")
            if data.get('items'):
                sample = data['items'][0]
                print(f"   示例: {sample.get('code')} - {sample.get('date')} - 收盘价: {sample.get('close')}")
        else:
            print(f"   ❌ 失败: HTTP {response.status_code}")
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")

def test_frontend_files():
    """测试前端文件修改"""
    print("\n🔧 测试前端文件修改")
    print("=" * 60)
    
    # 检查前端文件
    quotes_view_file = Path("admin/src/views/QuotesView.vue")
    quotes_service_file = Path("admin/src/services/quotes.service.ts")
    
    if quotes_view_file.exists():
        print("✅ QuotesView.vue 文件存在")
        content = quotes_view_file.read_text(encoding='utf-8')
        
        # 检查修改内容
        if 'code: historicalStockCode.value || \'\'' in content:
            print("✅ fetchHistoricalData 函数已修改，允许code为空")
        else:
            print("❌ fetchHistoricalData 函数修改不完整")
            
        if 'await fetchHistoricalData()' in content:
            print("✅ onMounted 中已添加自动加载历史数据")
        else:
            print("❌ onMounted 中未添加自动加载历史数据")
            
        if 'if (!historicalStockCode.value)' not in content:
            print("✅ 已移除股票代码为空的早期返回逻辑")
        else:
            print("❌ 仍存在股票代码为空的早期返回逻辑")
    else:
        print("❌ QuotesView.vue 文件不存在")
    
    if quotes_service_file.exists():
        print("✅ quotes.service.ts 文件存在")
        content = quotes_service_file.read_text(encoding='utf-8')
        
        # 检查修改内容
        if 'if (params.code)' in content and 'queryParams.append(\'code\', params.code)' in content:
            print("✅ getHistoricalQuotes 方法已修改，code参数可选")
        else:
            print("❌ getHistoricalQuotes 方法修改不完整")
    else:
        print("❌ quotes.service.ts 文件不存在")

def main():
    """主测试函数"""
    print("🚀 历史行情数据修复功能测试")
    print("=" * 60)
    
    print("📋 修复内容:")
    print("1. ✅ 后端API: 移除DISTINCT关键字")
    print("2. ✅ 后端API: 使code参数可选")
    print("3. ✅ 后端API: 修改查询逻辑支持无code查询")
    print("4. ✅ 前端服务: 修改参数处理逻辑")
    print("5. ✅ 前端组件: 移除股票代码为空的限制")
    print("6. ✅ 前端组件: 页面加载时自动获取历史数据")
    
    # 测试API接口
    test_api_endpoints()
    
    # 测试前端文件修改
    test_frontend_files()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    
    print("\n💡 预期效果:")
    print("1. 页面加载后自动显示最近的历史行情数据（所有股票）")
    print("2. 选择股票代码后，只显示该股票的历史行情数据")
    print("3. 可以按日期范围筛选")
    print("4. 每条数据都有'编辑'按钮，支持修改功能")
    print("5. 分页正常工作，显示实际的数据总数")
    
    print("\n🔧 使用说明:")
    print("1. 确保后端服务正在运行: python start_backend_api.py")
    print("2. 确保前端服务正在运行: cd admin && npm run dev")
    print("3. 访问管理端: http://localhost:3000/admin")
    print("4. 进入行情数据页面，点击'历史行情数据'标签页")
    print("5. 现在应该能看到历史数据，无需选择股票代码")

if __name__ == "__main__":
    main()
