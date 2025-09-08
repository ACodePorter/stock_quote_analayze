#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资讯频道API测试脚本
"""

import requests
import json
import sys

def test_news_api():
    """测试资讯频道API"""
    base_url = 'http://localhost:5000'
    
    print("🧪 开始测试资讯频道API...")
    
    # 测试获取分类
    print("\n1. 测试获取分类API...")
    try:
        response = requests.get(f'{base_url}/api/news/categories')
        if response.status_code == 200:
            data = response.json()
            print('✅ 获取分类API测试成功')
            print(f'分类数量: {len(data["data"])}')
            for cat in data['data']:
                print(f'  - {cat["name"]}: {cat["description"]}')
        else:
            print(f'❌ 获取分类API失败: {response.status_code}')
    except Exception as e:
        print(f'❌ 获取分类API异常: {e}')

    # 测试获取资讯列表
    print("\n2. 测试获取资讯列表API...")
    try:
        response = requests.get(f'{base_url}/api/news/list?page=1&page_size=5')
        if response.status_code == 200:
            data = response.json()
            print('✅ 获取资讯列表API测试成功')
            print(f'资讯数量: {len(data["data"]["items"])}')
            for news in data['data']['items']:
                print(f'  - {news["title"]} ({news["source"]})')
        else:
            print(f'❌ 获取资讯列表API失败: {response.status_code}')
    except Exception as e:
        print(f'❌ 获取资讯列表API异常: {e}')

    # 测试获取热门资讯
    print("\n3. 测试获取热门资讯API...")
    try:
        response = requests.get(f'{base_url}/api/news/hot?limit=3')
        if response.status_code == 200:
            data = response.json()
            print('✅ 获取热门资讯API测试成功')
            print(f'热门资讯数量: {len(data["data"])}')
            for news in data['data']:
                print(f'  - {news["title"]} ({news["read_count"]}阅读)')
        else:
            print(f'❌ 获取热门资讯API失败: {response.status_code}')
    except Exception as e:
        print(f'❌ 获取热门资讯API异常: {e}')

    # 测试获取头条新闻
    print("\n4. 测试获取头条新闻API...")
    try:
        response = requests.get(f'{base_url}/api/news/featured')
        if response.status_code == 200:
            data = response.json()
            print('✅ 获取头条新闻API测试成功')
            print(f'头条新闻: {data["data"]["title"]}')
        else:
            print(f'❌ 获取头条新闻API失败: {response.status_code}')
    except Exception as e:
        print(f'❌ 获取头条新闻API异常: {e}')

    print("\n🎉 资讯频道API测试完成!")

if __name__ == "__main__":
    test_news_api()
