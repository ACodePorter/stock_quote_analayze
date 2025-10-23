#!/usr/bin/env python3
"""
测试管理端历史行情数据功能
验证前端和后端的集成
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_historical_quotes_api():
    """测试历史行情数据API接口"""
    print("=" * 60)
    print("测试历史行情数据API接口")
    print("=" * 60)
    
    try:
        import requests
        import json
        
        # 测试API基础URL
        base_url = "http://localhost:8000/api"
        
        print("1. 测试获取历史行情数据...")
        
        # 测试获取历史行情数据
        test_params = {
            'code': '000001',
            'page': 1,
            'size': 10,
            'include_notes': True
        }
        
        response = requests.get(f"{base_url}/quotes/history", params=test_params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API调用成功")
            print(f"   数据项数量: {len(data.get('items', []))}")
            print(f"   总记录数: {data.get('total', 0)}")
            
            if data.get('items'):
                sample_item = data['items'][0]
                print(f"   示例数据字段: {list(sample_item.keys())}")
        else:
            print(f"   ❌ API调用失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_stock_list_api():
    """测试股票列表API接口"""
    print("\n" + "=" * 60)
    print("测试股票列表API接口")
    print("=" * 60)
    
    try:
        import requests
        
        base_url = "http://localhost:8000/api"
        
        print("1. 测试获取股票列表...")
        
        response = requests.get(f"{base_url}/quotes/stocks/list")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API调用成功")
            print(f"   股票数量: {len(data.get('data', []))}")
            
            if data.get('data'):
                sample_stock = data['data'][0]
                print(f"   示例股票: {sample_stock.get('code')} - {sample_stock.get('name')}")
        else:
            print(f"   ❌ API调用失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_frontend_integration():
    """测试前端集成"""
    print("\n" + "=" * 60)
    print("测试前端集成")
    print("=" * 60)
    
    print("1. 检查前端文件...")
    
    # 检查QuotesView.vue文件
    quotes_view_file = Path("admin/src/views/QuotesView.vue")
    if quotes_view_file.exists():
        print(f"   ✅ QuotesView.vue 文件存在")
        
        # 检查是否包含历史行情数据标签页
        content = quotes_view_file.read_text(encoding='utf-8')
        if '历史行情数据' in content:
            print(f"   ✅ 包含历史行情数据标签页")
        else:
            print(f"   ❌ 未找到历史行情数据标签页")
            
        if 'historicalStockCode' in content:
            print(f"   ✅ 包含历史行情数据相关变量")
        else:
            print(f"   ❌ 未找到历史行情数据相关变量")
    else:
        print(f"   ❌ QuotesView.vue 文件不存在")
    
    # 检查quotes.service.ts文件
    quotes_service_file = Path("admin/src/services/quotes.service.ts")
    if quotes_service_file.exists():
        print(f"   ✅ quotes.service.ts 文件存在")
        
        content = quotes_service_file.read_text(encoding='utf-8')
        if 'getHistoricalQuotes' in content:
            print(f"   ✅ 包含历史行情数据服务方法")
        else:
            print(f"   ❌ 未找到历史行情数据服务方法")
    else:
        print(f"   ❌ quotes.service.ts 文件不存在")

def test_database_connection():
    """测试数据库连接"""
    print("\n" + "=" * 60)
    print("测试数据库连接")
    print("=" * 60)
    
    try:
        from backend_core.database.db import SessionLocal
        
        print("1. 测试数据库连接...")
        session = SessionLocal()
        
        # 测试查询历史行情数据表
        from sqlalchemy import text
        result = session.execute(text("SELECT COUNT(*) FROM historical_quotes"))
        count = result.scalar()
        
        print(f"   ✅ 数据库连接成功")
        print(f"   历史行情数据记录数: {count}")
        
        session.close()
        
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")

def main():
    """主测试函数"""
    print("🚀 管理端历史行情数据功能测试")
    print("这个测试将验证前端和后端的集成")
    
    # 测试数据库连接
    test_database_connection()
    
    # 测试API接口
    test_historical_quotes_api()
    test_stock_list_api()
    
    # 测试前端集成
    test_frontend_integration()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("💡 如果API测试失败，请确保后端服务正在运行")
    print("💡 如果前端集成测试失败，请检查文件是否正确更新")

if __name__ == "__main__":
    main()
