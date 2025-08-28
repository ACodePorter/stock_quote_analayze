#!/usr/bin/env python3
"""
测试市场指数API
验证从指数实时行情表获取数据的功能
"""

import requests
import json
from typing import List, Dict, Any

def test_market_indices_api():
    """测试市场指数API功能"""
    base_url = "http://localhost:8000"
    
    print("🔍 测试市场指数API...")
    print("=" * 60)
    
    try:
        # 请求指数数据
        url = f"{base_url}/api/market/indices"
        print(f"请求URL: {url}")
        
        response = requests.get(url)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get("success"):
                indices = data.get("data", [])
                print(f"✅ 获取到 {len(indices)} 个指数数据")
                
                for i, index in enumerate(indices):
                    print(f"\n📊 指数 {i+1}:")
                    print(f"  代码: {index.get('code', 'N/A')}")
                    print(f"  名称: {index.get('name', 'N/A')}")
                    print(f"  当前值: {index.get('current', 'N/A')}")
                    print(f"  涨跌额: {index.get('change', 'N/A')}")
                    print(f"  涨跌幅: {index.get('change_percent', 'N/A')}%")
                    print(f"  成交量: {index.get('volume', 'N/A')}")
                    print(f"  更新时间: {index.get('timestamp', 'N/A')}")
                    
                    # 检查数据完整性
                    if all(index.get(field) is not None for field in ['code', 'name', 'current', 'change', 'change_percent']):
                        print("  ✅ 数据完整")
                    else:
                        print("  ❌ 数据不完整")
                        
            else:
                print(f"❌ API返回失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 测试完成!")

if __name__ == "__main__":
    test_market_indices_api()
