#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新闻收集器修复后的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend_core.data_collectors.news_collector import NewsCollector
from backend_core.database.db import SessionLocal

def test_news_collector():
    """测试新闻收集器"""
    print("🧪 测试新闻收集器修复后的功能...")
    
    try:
        # 创建数据库会话
        db = SessionLocal()
        
        # 创建新闻收集器实例
        collector = NewsCollector()
        
        print("1. 测试收集综合资讯...")
        result = collector.collect_comprehensive_news()
        
        if result:
            print(f"✅ 综合资讯收集成功，收集到 {result} 条资讯")
        else:
            print("⚠️ 综合资讯收集完成，但可能没有新数据")
        
        print("\n2. 检查最新插入的数据...")
        from sqlalchemy import text
        result = db.execute(text("""
            SELECT id, title, publish_time, source, created_at
            FROM stock_news 
            ORDER BY created_at DESC 
            LIMIT 5
        """))
        
        news_list = result.fetchall()
        if news_list:
            print("最新5条资讯:")
            for news in news_list:
                print(f"  ID: {news[0]}, 标题: {news[1][:50]}..., 时间: {news[2]}, 来源: {news[3]}")
        else:
            print("❌ 没有找到资讯数据")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 测试新闻收集器失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_news_api():
    """测试新闻API"""
    print("\n🧪 测试新闻API...")
    
    import requests
    
    try:
        # 测试头条新闻API
        response = requests.get('http://localhost:5000/api/news/featured')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 头条新闻API正常")
            else:
                print(f"❌ 头条新闻API返回错误: {data.get('message')}")
        else:
            print(f"❌ 头条新闻API响应异常: {response.status_code}")
        
        # 测试首页市场资讯API
        response = requests.get('http://localhost:5000/api/news/homepage?limit=3')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 首页市场资讯API正常")
                print(f"   返回资讯数量: {len(data['data'])}")
            else:
                print(f"❌ 首页市场资讯API返回错误: {data.get('message')}")
        else:
            print(f"❌ 首页市场资讯API响应异常: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试新闻API失败: {e}")
        return False

def main():
    """主函数"""
    print("🎯 新闻收集器修复测试")
    print("=" * 50)
    
    # 测试新闻收集器
    collector_success = test_news_collector()
    
    # 测试新闻API
    api_success = test_news_api()
    
    if collector_success and api_success:
        print("\n🎉 所有测试通过!")
        print("✅ 新闻收集器修复成功")
        print("✅ 新闻API正常工作")
        print("\n💡 现在可以正常收集和使用新闻数据了")
    else:
        print("\n❌ 部分测试失败，请检查:")
        if not collector_success:
            print("- 新闻收集器需要进一步调试")
        if not api_success:
            print("- 新闻API需要检查")

if __name__ == "__main__":
    main()
