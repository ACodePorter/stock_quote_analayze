#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
头条新闻API修复测试脚本
"""

import requests
import json

def test_featured_news_api():
    """测试头条新闻API"""
    print("🧪 测试头条新闻API修复...")
    
    try:
        response = requests.get('http://localhost:5000/api/news/featured')
        if response.status_code == 200:
            data = response.json()
            print('✅ 头条新闻API修复成功')
            print(f'标题: {data["data"]["title"]}')
            print(f'时间: {data["data"]["publish_time"]}')
            print(f'来源: {data["data"]["source"]}')
            print(f'阅读量: {data["data"]["read_count"]}')
            print(f'是否热门: {data["data"]["is_hot"]}')
            return True
        else:
            print(f'❌ API响应异常: {response.status_code}')
            print(f'响应内容: {response.text}')
            return False
    except Exception as e:
        print(f'❌ API连接失败: {e}')
        return False

def test_homepage_news_api():
    """测试首页市场资讯API"""
    print("\n🧪 测试首页市场资讯API...")
    
    try:
        response = requests.get('http://localhost:5000/api/news/homepage?limit=3')
        if response.status_code == 200:
            data = response.json()
            print('✅ 首页市场资讯API正常')
            print(f'返回资讯数量: {len(data["data"])}')
            return True
        else:
            print(f'❌ API响应异常: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ API连接失败: {e}')
        return False

def main():
    """主函数"""
    print("🎯 资讯频道API修复测试")
    print("=" * 50)
    
    # 测试头条新闻API
    featured_success = test_featured_news_api()
    
    # 测试首页市场资讯API
    homepage_success = test_homepage_news_api()
    
    if featured_success and homepage_success:
        print("\n🎉 所有API修复测试通过!")
        print("✅ 头条新闻API正常")
        print("✅ 首页市场资讯API正常")
        print("\n💡 现在可以正常访问资讯频道页面了")
    else:
        print("\n❌ 部分API仍有问题，请检查:")
        if not featured_success:
            print("- 头条新闻API需要进一步调试")
        if not homepage_success:
            print("- 首页市场资讯API需要检查")

if __name__ == "__main__":
    main()
