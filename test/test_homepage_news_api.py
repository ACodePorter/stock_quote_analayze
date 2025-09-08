#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首页市场资讯API测试脚本
"""

import requests
import json

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
        else:
            print(f'❌ API响应异常: {response.status_code}')
            print(f'响应内容: {response.text}')
    except Exception as e:
        print(f'❌ API连接失败: {e}')

if __name__ == "__main__":
    test_homepage_news_api()
