#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票行情数据修复脚本
"""

import sys
import os
import requests
import json
from datetime import datetime

def test_quote_board_list():
    """测试股票行情排行接口"""
    print("🧪 测试股票行情排行接口...")
    
    # 测试参数
    test_cases = [
        {
            'ranking_type': 'rise',
            'market': 'all',
            'page': 1,
            'page_size': 5
        },
        {
            'ranking_type': 'fall',
            'market': 'all',
            'page': 1,
            'page_size': 5
        },
        {
            'ranking_type': 'volume',
            'market': 'all',
            'page': 1,
            'page_size': 5
        }
    ]
    
    base_url = "https://www.icemaplecity.com/api/stock/quote_board_list"
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 测试用例 {i}: {test_case}")
        
        try:
            # 构建查询参数
            params = test_case
            
            # 发送请求
            response = requests.get(base_url, params=params, timeout=30)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result_data = data.get('data', [])
                    print(f"✅ 成功获取 {len(result_data)} 条数据")
                    
                    # 检查数据结构
                    if result_data:
                        first_item = result_data[0]
                        print(f"📋 数据结构示例:")
                        for key, value in first_item.items():
                            print(f"  {key}: {value} (类型: {type(value).__name__})")
                        
                        # 检查数值字段
                        numeric_fields = ['current', 'change', 'change_percent', 'open', 'pre_close', 'high', 'low', 'volume', 'turnover', 'rate']
                        for field in numeric_fields:
                            if field in first_item:
                                value = first_item[field]
                                if value is not None:
                                    try:
                                        float(value)
                                        print(f"  ✅ {field}: {value} (数值有效)")
                                    except (ValueError, TypeError):
                                        print(f"  ❌ {field}: {value} (数值无效)")
                else:
                    print(f"❌ 接口返回失败: {data.get('message', '未知错误')}")
                    if 'error' in data:
                        print(f"错误详情: {data['error']}")
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求异常: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析异常: {e}")
        except Exception as e:
            print(f"❌ 其他异常: {e}")

def test_realtime_quote():
    """测试实时行情接口"""
    print("\n🧪 测试实时行情接口...")
    
    # 测试股票代码
    test_codes = ['000001', '600519', '000002']
    base_url = "https://www.icemaplecity.com/api/stock/realtime_quote_by_code"
    
    for code in test_codes:
        print(f"\n📈 测试股票代码: {code}")
        
        try:
            params = {'code': code}
            response = requests.get(base_url, params=params, timeout=30)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result_data = data.get('data', {})
                    print(f"✅ 成功获取 {code} 的实时行情")
                    
                    # 检查数据结构
                    print(f"📋 数据结构:")
                    for key, value in result_data.items():
                        print(f"  {key}: {value} (类型: {type(value).__name__})")
                else:
                    print(f"❌ 接口返回失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")

def test_batch_quote():
    """测试批量行情接口"""
    print("\n🧪 测试批量行情接口...")
    
    base_url = "https://www.icemaplecity.com/api/stock/quote"
    
    try:
        # 测试数据
        test_data = {
            "codes": ["000001", "600519", "000002"]
        }
        
        response = requests.post(base_url, json=test_data, timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result_data = data.get('data', [])
                print(f"✅ 成功获取 {len(result_data)} 只股票的批量行情")
                
                # 检查数据结构
                if result_data:
                    first_item = result_data[0]
                    print(f"📋 数据结构示例:")
                    for key, value in first_item.items():
                        print(f"  {key}: {value} (类型: {type(value).__name__})")
            else:
                print(f"❌ 接口返回失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")

def main():
    """主函数"""
    print("🚀 股票行情数据修复测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试各个接口
    test_quote_board_list()
    test_realtime_quote()
    test_batch_quote()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
    print("\n如果所有测试都通过，说明数据类型修复成功。")
    print("如果仍有错误，请检查具体的错误信息并进一步修复。")

if __name__ == "__main__":
    main()
