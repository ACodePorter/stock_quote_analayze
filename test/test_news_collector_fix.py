#!/usr/bin/env python3
"""
测试新闻采集器修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_core.data_collectors.news_collector import NewsCollector

def test_news_collector():
    """测试新闻采集器"""
    print("🧪 测试新闻采集器修复...")
    
    try:
        collector = NewsCollector()
        
        print("📰 开始采集市场新闻...")
        news_list = collector.collect_market_news()
        
        print(f"✅ 采集完成，共处理 {len(news_list)} 条新闻")
        
        if news_list:
            print("\n📄 前3条新闻示例:")
            for i, news in enumerate(news_list[:3]):
                print(f"\n第 {i+1} 条:")
                print(f"  标题: {news['title']}")
                print(f"  内容: {news['content'][:100]}...")
                print(f"  发布时间: {news['publish_time']}")
                print(f"  来源: {news['source']}")
                print(f"  URL: {news['url']}")
        
        return len(news_list) > 0
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("🔧 新闻采集器修复测试")
    print("=" * 60)
    
    success = test_news_collector()
    
    if success:
        print("\n🎉 新闻采集器修复成功！")
        print("现在新闻采集应该能正常处理akshare返回的数据了。")
    else:
        print("\n⚠️ 新闻采集器仍有问题，需要进一步检查。")

if __name__ == "__main__":
    main()
