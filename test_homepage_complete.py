#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首页市场资讯功能测试脚本
"""

import requests
import json
import webbrowser
import os
import time

def test_homepage_news_api():
    """测试首页市场资讯API"""
    print("🧪 测试首页市场资讯API...")
    
    try:
        response = requests.get('http://localhost:5000/api/news/homepage?limit=3')
        if response.status_code == 200:
            data = response.json()
            print('✅ 首页市场资讯API测试成功')
            print(f'返回资讯数量: {len(data["data"])}')
            
            for i, news in enumerate(data['data'], 1):
                print(f'\n{i}. {news["title"]}')
                print(f'   摘要: {news["summary"]}')
                print(f'   时间: {news["publish_time"]}')
                print(f'   来源: {news["source"]}')
                print(f'   阅读量: {news["read_count"]}')
            
            return True
        else:
            print(f'❌ API响应异常: {response.status_code}')
            print(f'响应内容: {response.text}')
            return False
    except Exception as e:
        print(f'❌ API连接失败: {e}')
        return False

def test_homepage_access():
    """测试首页访问"""
    print("\n🌐 测试首页访问...")
    
    try:
        # 测试首页HTML是否可以访问
        response = requests.get('http://localhost:8000/index.html', timeout=5)
        if response.status_code == 200:
            print('✅ 首页HTML访问正常')
            return True
        else:
            print(f'❌ 首页访问异常: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ 首页访问失败: {e}')
        return False

def open_homepage():
    """打开首页"""
    print("\n🚀 打开首页...")
    
    try:
        homepage_url = 'http://localhost:8000/index.html'
        webbrowser.open(homepage_url)
        print(f'✅ 首页已打开: {homepage_url}')
        return True
    except Exception as e:
        print(f'❌ 打开首页失败: {e}')
        return False

def main():
    """主函数"""
    print("🎯 首页市场资讯功能测试")
    print("=" * 50)
    
    # 测试API
    api_success = test_homepage_news_api()
    
    # 测试首页访问
    page_success = test_homepage_access()
    
    # 打开首页
    if api_success and page_success:
        open_homepage()
        
        print("\n🎉 首页市场资讯功能测试完成!")
        print("\n📋 测试结果:")
        print("✅ API接口正常")
        print("✅ 首页页面可访问")
        print("✅ 浏览器已打开首页")
        print("\n💡 请在浏览器中查看首页的市场资讯部分是否正常显示")
    else:
        print("\n❌ 测试失败，请检查:")
        if not api_success:
            print("- 后端API服务是否运行")
        if not page_success:
            print("- 前端服务是否运行")
            print("- 端口8000是否被占用")

if __name__ == "__main__":
    main()
