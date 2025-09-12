#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试行情数据获取修复效果
"""

import requests
import json
from datetime import datetime

def test_frontend_api_path():
    """测试前端会访问的API路径"""
    print("🧪 测试前端API路径修复效果...")
    
    # 模拟前端会生成的API路径
    base_url = "http://localhost:5000/api"  # 去掉/admin后的基础URL
    
    test_endpoints = [
        f"{base_url}/quotes/stocks?page=1&page_size=5",
        f"{base_url}/quotes/indices?page=1&page_size=5", 
        f"{base_url}/quotes/industries?page=1&page_size=5",
        f"{base_url}/quotes/stats",
    ]
    
    results = []
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                data_count = len(data.get('data', []))
                results.append({
                    'endpoint': endpoint,
                    'status': 'success',
                    'data_count': data_count,
                    'success': success
                })
                print(f"  ✅ {endpoint.split('/')[-1]} - 成功 (数据: {data_count} 条)")
            else:
                results.append({
                    'endpoint': endpoint,
                    'status': 'failed',
                    'status_code': response.status_code
                })
                print(f"  ❌ {endpoint.split('/')[-1]} - 失败 ({response.status_code})")
        except Exception as e:
            results.append({
                'endpoint': endpoint,
                'status': 'error',
                'error': str(e)
            })
            print(f"  ❌ {endpoint.split('/')[-1]} - 错误: {str(e)}")
    
    return results

def test_quotes_refresh():
    """测试刷新功能"""
    print("\n🔄 测试刷新功能...")
    
    try:
        response = requests.post("http://localhost:5000/api/quotes/refresh", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 刷新成功: {data.get('message')}")
            return True
        else:
            print(f"  ❌ 刷新失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ 刷新错误: {str(e)}")
        return False

def summary_report(results):
    """生成总结报告"""
    print("\n📊 修复效果总结:")
    
    total_tests = len(results)
    successful_tests = len([r for r in results if r['status'] == 'success'])
    
    print(f"  总测试数: {total_tests}")
    print(f"  成功测试: {successful_tests}")
    print(f"  成功率: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("\n  🎉 所有API端点都正常工作！")
        print("  ✅ 行情数据获取问题已完全修复")
    else:
        print("\n  ⚠️  部分API端点仍有问题，需要进一步检查")

if __name__ == "__main__":
    print(f"🚀 开始测试行情数据修复效果 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试API端点
    results = test_frontend_api_path()
    
    # 测试刷新功能
    refresh_success = test_quotes_refresh()
    
    # 生成总结报告
    summary_report(results)
    
    print(f"\n✅ 测试完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
