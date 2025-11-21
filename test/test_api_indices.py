#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API接口返回的指数数据
"""

import sys
import requests
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 测试API接口
API_BASE_URL = "http://localhost:5000"

def test_api_indices():
    """测试API接口"""
    print("=" * 50)
    print("测试API接口: /api/market/indices")
    print("=" * 50)
    
    try:
        url = f"{API_BASE_URL}/api/market/indices"
        print(f"\n请求URL: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('success'):
                data = result.get('data', [])
                print(f"\n返回了 {len(data)} 条指数数据:")
                for idx, index in enumerate(data, 1):
                    print(f"  {idx}. 代码: {index.get('code')}, 名称: {index.get('name')}, 当前价: {index.get('current')}")
                
                # 检查目标指数
                target_codes = ['000001', '399001', '399006', '000300']
                print("\n检查目标指数:")
                for code in target_codes:
                    found = [idx for idx in data if idx.get('code') == code]
                    if found:
                        print(f"  ✓ 找到代码 {code}: {found[0].get('name')}")
                    else:
                        print(f"  ✗ 未找到代码 {code}")
            else:
                print(f"\nAPI返回错误: {result.get('message')}")
                if 'traceback' in result:
                    print(f"错误堆栈:\n{result['traceback']}")
        else:
            print(f"\n请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n无法连接到API服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"\n测试时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_indices()

