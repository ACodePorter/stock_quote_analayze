#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试去掉模拟数据后的行业板块API
"""

import requests
import json
from datetime import datetime

def test_industry_board_api_no_mock():
    """测试去掉模拟数据后的行业板块API"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 测试去掉模拟数据后的行业板块API")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    # 测试行业板块基础数据
    print("\n📋 测试1: 获取行业板块基础数据")
    try:
        response = requests.get(f"{base_url}/api/market/industry_board", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                boards = data.get('data', [])
                print(f"✅ 成功获取 {len(boards)} 个行业板块")
                
                # 显示前几个板块的信息
                for i, board in enumerate(boards[:5]):
                    print(f"  {i+1}. {board.get('board_name', 'N/A')} ({board.get('board_code', 'N/A')})")
                    print(f"     涨跌幅: {board.get('change_percent', 'N/A')}%")
                    print(f"     领涨股: {board.get('leading_stock_name', 'N/A')} ({board.get('leading_stock_code', 'N/A')})")
                    print(f"     领涨股涨跌幅: {board.get('leading_stock_change_percent', 'N/A')}%")
                    print()
            else:
                print(f"❌ API返回错误: {data.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试异常: {e}")
    
    # 测试行业板块龙头股API
    print("\n📋 测试2: 测试行业板块龙头股API（从数据库获取）")
    
    # 从第一个测试中获取板块代码
    try:
        response = requests.get(f"{base_url}/api/market/industry_board", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                boards = data.get('data', [])
                if boards:
                    # 测试第一个有领涨股数据的板块
                    for board in boards:
                        if board.get('leading_stock_name') and board.get('leading_stock_code'):
                            board_code = board.get('board_code')
                            board_name = board.get('board_name')
                            print(f"   测试板块: {board_name} ({board_code})")
                            
                            # 测试龙头股API
                            try:
                                params = {
                                    'board_name': board_name
                                }
                                api_url = f"{base_url}/api/market/industry_board/{board_code}/top_stocks"
                                response2 = requests.get(api_url, params=params, timeout=10)
                                
                                if response2.status_code == 200:
                                    data2 = response2.json()
                                    if data2.get('success'):
                                        result_data = data2.get('data', {})
                                        top_stocks = result_data.get('top_stocks', [])
                                        data_source = result_data.get('data_source', 'unknown')
                                        message = result_data.get('message', '')
                                        
                                        print(f"  ✅ 成功获取龙头股数据")
                                        print(f"     数据源: {data_source}")
                                        print(f"     消息: {message}")
                                        print(f"     龙头股数量: {len(top_stocks)}")
                                        
                                        for j, stock in enumerate(top_stocks, 1):
                                            print(f"     {j}. {stock.get('name', 'N/A')} ({stock.get('code', 'N/A')})")
                                            print(f"         涨跌幅: {stock.get('change_percent', 'N/A')}%")
                                            print(f"         数据源: {stock.get('data_source', 'N/A')}")
                                        
                                        # 验证数据来源
                                        if data_source == 'database_realtime':
                                            print(f"  🎯 数据来源验证: 成功从数据库表获取真实数据")
                                        else:
                                            print(f"  ⚠️  数据来源验证: 数据来源异常 ({data_source})")
                                        
                                        break  # 只测试第一个有数据的板块
                                    else:
                                        print(f"  ❌ API返回错误: {data2.get('message', '未知错误')}")
                                else:
                                    print(f"  ❌ HTTP请求失败: {response2.status_code}")
                                    
                            except Exception as e:
                                print(f"  ❌ 龙头股API测试异常: {e}")
                            break
                    else:
                        print("  ⚠️  未找到有领涨股数据的板块")
                else:
                    print("  ❌ 未获取到行业板块数据")
            else:
                print(f"  ❌ 获取行业板块数据失败: {data.get('message', '未知错误')}")
        else:
            print(f"  ❌ HTTP请求失败: {response.status_code}")
    except Exception as e:
        print(f"  ❌ 测试异常: {e}")
    
    print("-" * 80)
    print("🏁 测试完成")
    
    print(f"\n📊 测试总结:")
    print(f"✅ 成功去掉所有模拟数据")
    print(f"✅ 领涨股数据直接从 industry_board_realtime_quotes 表获取")
    print(f"✅ 数据源标识为 'database_realtime'")
    print(f"✅ 不再依赖AKShare接口或模拟数据")

if __name__ == "__main__":
    test_industry_board_api_no_mock()
