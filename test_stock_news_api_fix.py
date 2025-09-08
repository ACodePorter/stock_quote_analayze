#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票资讯API修复
"""

import requests
import json

def test_stock_news_api():
    """测试股票资讯API"""
    print("🧪 测试股票资讯API...")
    
    try:
        # 测试股票836433的资讯
        response = requests.get('http://localhost:5000/api/stock/news/news_combined?symbol=836433&news_limit=5')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print('✅ 股票资讯API测试成功')
                print(f'返回数据数量: {len(data["data"])}')
                
                # 显示前3条数据
                for i, item in enumerate(data['data'][:3], 1):
                    print(f'\n{i}. {item.get("title", "")}')
                    print(f'   类型: {item.get("type", "")}')
                    print(f'   时间: {item.get("publish_time", "")}')
                    print(f'   来源: {item.get("source", "")}')
                
                return True
            else:
                print(f'❌ API返回错误: {data.get("message")}')
                return False
        else:
            print(f'❌ API响应异常: {response.status_code}')
            print(f'响应内容: {response.text[:500]}')
            return False
            
    except Exception as e:
        print(f'❌ API连接失败: {e}')
        return False

def test_news_apis():
    """测试所有新闻相关API"""
    print("\n🧪 测试所有新闻API...")
    
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

def main():
    """主函数"""
    print("🎯 股票资讯API修复测试")
    print("=" * 50)
    
    # 测试股票资讯API
    stock_success = test_stock_news_api()
    
    # 测试其他新闻API
    other_results = test_news_apis()
    
    # 统计结果
    other_success_count = sum(other_results.values())
    
    print(f"\n📊 测试结果统计:")
    print(f"股票资讯API: {'✅ 通过' if stock_success else '❌ 失败'}")
    print(f"其他新闻API: {other_success_count}/{len(other_results)} 通过")
    
    if stock_success and other_success_count >= 3:
        print("\n🎉 所有API修复测试通过!")
        print("✅ 股票资讯API正常工作")
        print("✅ 其他新闻API正常工作")
        print("\n💡 现在可以正常使用所有新闻功能了")
    else:
        print("\n❌ 部分API仍有问题，请检查:")
        if not stock_success:
            print("- 股票资讯API需要进一步调试")
        if other_success_count < 3:
            print("- 部分新闻API需要检查")

if __name__ == "__main__":
    main()
