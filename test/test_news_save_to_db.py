#!/usr/bin/env python3
"""
测试新闻保存到数据库
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_core.data_collectors.news_collector import NewsCollector

def test_news_save_to_db():
    """测试新闻保存到数据库"""
    print("🧪 测试新闻保存到数据库...")
    
    try:
        collector = NewsCollector()
        
        print("📰 开始采集市场新闻...")
        news_list = collector.collect_market_news()
        
        print(f"✅ 采集完成，共处理 {len(news_list)} 条新闻")
        
        if news_list:
            print("💾 开始保存到数据库...")
            saved_count = collector.save_news_to_db(news_list)
            print(f"✅ 保存完成，共保存 {saved_count} 条新闻")
            
            return saved_count > 0
        else:
            print("⚠️ 没有新闻数据需要保存")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("🔧 新闻保存到数据库测试")
    print("=" * 60)
    
    success = test_news_save_to_db()
    
    if success:
        print("\n🎉 新闻保存到数据库成功！")
        print("现在新闻采集和保存功能应该能正常工作了。")
    else:
        print("\n⚠️ 新闻保存仍有问题，需要进一步检查。")

if __name__ == "__main__":
    main()
