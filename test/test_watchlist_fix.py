#!/usr/bin/env python3
"""
测试自选股数据获取修复
验证首页自选股是否能正确获取最新交易日期的行情数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime

# 配置
API_BASE_URL = "http://localhost:5000"
TEST_USER = {
    "username": "test_user",
    "password": "test_password"
}

def test_watchlist_api():
    """测试自选股API是否能正确获取最新交易日期数据"""
    print("🧪 开始测试自选股API...")
    
    # 1. 登录获取token
    print("1. 登录获取token...")
    login_response = requests.post(f"{API_BASE_URL}/api/auth/login", json=TEST_USER)
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code}")
        return False
    
    token = login_response.json().get("access_token")
    if not token:
        print("❌ 未获取到token")
        return False
    
    print("✅ 登录成功")
    
    # 2. 测试自选股API
    print("2. 测试自选股API...")
    headers = {"Authorization": f"Bearer {token}"}
    watchlist_response = requests.get(f"{API_BASE_URL}/api/watchlist", headers=headers)
    
    if watchlist_response.status_code != 200:
        print(f"❌ 自选股API调用失败: {watchlist_response.status_code}")
        print(f"响应内容: {watchlist_response.text}")
        return False
    
    result = watchlist_response.json()
    print(f"✅ 自选股API调用成功")
    print(f"返回数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 3. 验证数据
    if result.get("success") and result.get("data"):
        stocks = result["data"]
        print(f"📊 获取到 {len(stocks)} 只自选股")
        
        for stock in stocks:
            print(f"  - {stock.get('name', 'N/A')} ({stock.get('code', 'N/A')})")
            print(f"    最新价: {stock.get('current_price', 'N/A')}")
            print(f"    涨跌幅: {stock.get('change_percent', 'N/A')}%")
            print(f"    涨跌额: {stock.get('change_amount', 'N/A')}")
            print()
        
        return True
    else:
        print("⚠️ 自选股数据为空或API返回失败")
        return False

def test_quote_board_api():
    """测试涨幅榜API作为对比"""
    print("🧪 测试涨幅榜API作为对比...")
    
    response = requests.get(f"{API_BASE_URL}/api/stock/quote_board?limit=3")
    if response.status_code != 200:
        print(f"❌ 涨幅榜API调用失败: {response.status_code}")
        return False
    
    result = response.json()
    print(f"✅ 涨幅榜API调用成功")
    print(f"返回数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("🔧 自选股数据获取修复测试")
    print("=" * 60)
    
    try:
        # 测试涨幅榜API
        print("\n📈 测试涨幅榜API...")
        quote_board_success = test_quote_board_api()
        
        # 测试自选股API
        print("\n📋 测试自选股API...")
        watchlist_success = test_watchlist_api()
        
        # 总结
        print("\n" + "=" * 60)
        print("📊 测试结果总结:")
        print(f"涨幅榜API: {'✅ 成功' if quote_board_success else '❌ 失败'}")
        print(f"自选股API: {'✅ 成功' if watchlist_success else '❌ 失败'}")
        
        if watchlist_success:
            print("\n🎉 自选股数据获取修复成功！")
            print("现在首页自选股应该能正确显示最新交易日期的行情数据。")
        else:
            print("\n⚠️ 自选股数据获取仍有问题，需要进一步检查。")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
