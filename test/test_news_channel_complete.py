#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资讯频道完整功能测试脚本
"""

import requests
import json
import webbrowser
import time

def test_all_news_apis():
    """测试所有资讯相关API"""
    print("🧪 测试所有资讯API...")
    
    apis = [
        ("头条新闻", "/api/news/featured"),
        ("首页市场资讯", "/api/news/homepage?limit=3"),
        ("资讯分类", "/api/news/categories"),
        ("资讯列表", "/api/news/list?limit=5"),
        ("热门资讯", "/api/news/hot?limit=5")
    ]
    
    results = {}
    
    for name, endpoint in apis:
        try:
            response = requests.get(f'http://localhost:5000{endpoint}')
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f'✅ {name}API正常')
                    results[name] = True
                else:
                    print(f'❌ {name}API返回错误: {data.get("message", "未知错误")}')
                    results[name] = False
            else:
                print(f'❌ {name}API响应异常: {response.status_code}')
                results[name] = False
        except Exception as e:
            print(f'❌ {name}API连接失败: {e}')
            results[name] = False
    
    return results

def test_frontend_access():
    """测试前端页面访问"""
    print("\n🌐 测试前端页面访问...")
    
    pages = [
        ("首页", "http://localhost:8001/index.html"),
        ("资讯频道", "http://localhost:8001/news.html")
    ]
    
    results = {}
    
    for name, url in pages:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f'✅ {name}页面访问正常')
                results[name] = True
            else:
                print(f'❌ {name}页面访问异常: {response.status_code}')
                results[name] = False
        except Exception as e:
            print(f'❌ {name}页面访问失败: {e}')
            results[name] = False
    
    return results

def open_news_channel():
    """打开资讯频道页面"""
    print("\n🚀 打开资讯频道页面...")
    
    try:
        news_url = 'http://localhost:8001/news.html'
        webbrowser.open(news_url)
        print(f'✅ 资讯频道页面已打开: {news_url}')
        return True
    except Exception as e:
        print(f'❌ 打开资讯频道页面失败: {e}')
        return False

def main():
    """主函数"""
    print("🎯 资讯频道完整功能测试")
    print("=" * 60)
    
    # 测试所有API
    api_results = test_all_news_apis()
    
    # 测试前端页面
    page_results = test_frontend_access()
    
    # 统计结果
    api_success_count = sum(api_results.values())
    page_success_count = sum(page_results.values())
    
    print(f"\n📊 测试结果统计:")
    print(f"API测试: {api_success_count}/{len(api_results)} 通过")
    print(f"页面测试: {page_success_count}/{len(page_results)} 通过")
    
    # 如果大部分功能正常，打开页面
    if api_success_count >= 3 and page_success_count >= 1:
        open_news_channel()
        
        print("\n🎉 资讯频道功能测试完成!")
        print("\n✅ 主要功能正常:")
        for name, success in api_results.items():
            if success:
                print(f"  - {name}")
        
        print("\n💡 使用说明:")
        print("1. 资讯频道页面已自动打开")
        print("2. 可以测试头条新闻、分类筛选、资讯列表等功能")
        print("3. 首页市场资讯也会正常显示")
    else:
        print("\n❌ 部分功能异常，请检查:")
        for name, success in api_results.items():
            if not success:
                print(f"  - {name}API需要修复")
        for name, success in page_results.items():
            if not success:
                print(f"  - {name}页面需要检查")

if __name__ == "__main__":
    main()
