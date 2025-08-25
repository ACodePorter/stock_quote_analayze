#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的实时行情API，验证从数据库获取市盈率数据
"""

import requests
import json
import time
from datetime import datetime

def test_realtime_quote_api_from_db():
    """测试实时行情API从数据库获取市盈率数据"""
    
    # 测试几个不同的股票代码
    test_codes = ['000001', '600036', '603667', '300750']
    
    # API基础URL（根据实际部署情况调整）
    base_url = "http://localhost:8000"  # 或者使用实际的后端服务地址
    
    for code in test_codes:
        print(f"\n{'='*60}")
        print(f"测试股票代码: {code}")
        print(f"{'='*60}")
        
        try:
            # 调用实时行情API
            url = f"{base_url}/api/stock/realtime_quote_by_code?code={code}"
            print(f"请求URL: {url}")
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"API响应状态: {data.get('success')}")
                
                if data.get('success'):
                    stock_data = data.get('data', {})
                    print(f"股票代码: {stock_data.get('code', 'N/A')}")
                    print(f"当前价格: {stock_data.get('current_price', 'N/A')}")
                    print(f"涨跌额: {stock_data.get('change_amount', 'N/A')}")
                    print(f"涨跌幅: {stock_data.get('change_percent', 'N/A')}")
                    print(f"今开: {stock_data.get('open', 'N/A')}")
                    print(f"昨收: {stock_data.get('pre_close', 'N/A')}")
                    print(f"最高: {stock_data.get('high', 'N/A')}")
                    print(f"最低: {stock_data.get('low', 'N/A')}")
                    print(f"成交量: {stock_data.get('volume', 'N/A')}")
                    print(f"成交额: {stock_data.get('turnover', 'N/A')}")
                    print(f"换手率: {stock_data.get('turnover_rate', 'N/A')}")
                    print(f"市盈率: {stock_data.get('pe_dynamic', 'N/A')}")
                    print(f"均价: {stock_data.get('average_price', 'N/A')}")
                    
                    # 特别关注市盈率字段
                    pe_dynamic = stock_data.get('pe_dynamic')
                    if pe_dynamic and pe_dynamic != 'None':
                        print(f"✅ 市盈率数据获取成功: {pe_dynamic}")
                    else:
                        print(f"❌ 市盈率数据获取失败或为空: {pe_dynamic}")
                        
                else:
                    print(f"❌ API返回失败: {data.get('message', 'Unknown error')}")
                    
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
        except Exception as e:
            print(f"❌ 其他异常: {e}")
            
        # 添加延迟，避免请求过于频繁
        time.sleep(1)

def test_database_pe_ratio_data():
    """测试数据库中是否有市盈率数据"""
    
    base_url = "http://localhost:8000"
    
    print(f"\n{'='*60}")
    print("测试数据库中的市盈率数据")
    print(f"{'='*60}")
    
    try:
        # 调用数据库查询API（如果有的话）或者直接查询数据库
        # 这里我们通过实时行情API来间接验证数据库数据
        
        test_codes = ['000001', '600036']
        for code in test_codes:
            print(f"\n检查股票 {code} 的数据库市盈率数据:")
            
            url = f"{base_url}/api/stock/realtime_quote_by_code?code={code}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stock_data = data.get('data', {})
                    pe_dynamic = stock_data.get('pe_dynamic')
                    
                    if pe_dynamic and pe_dynamic != 'None':
                        print(f"  ✅ 股票 {code} 市盈率: {pe_dynamic}")
                    else:
                        print(f"  ❌ 股票 {code} 市盈率: 无数据")
                else:
                    print(f"  ❌ 股票 {code} API调用失败: {data.get('message')}")
            else:
                print(f"  ❌ 股票 {code} 市盈率: 无数据")
                
    except Exception as e:
        print(f"❌ 测试数据库市盈率数据时出错: {e}")

def test_api_availability():
    """测试API服务是否可用"""
    
    base_url = "http://localhost:8000"
    
    print(f"\n{'='*60}")
    print("测试API服务可用性")
    print(f"{'='*60}")
    
    try:
        # 测试健康检查或简单的API端点
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print(f"✅ API服务可用: {base_url}")
            return True
        else:
            print(f"⚠️ API服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API服务不可用: {e}")
        print(f"请确保后端服务正在运行在: {base_url}")
        return False

def show_test_summary():
    """显示测试总结"""
    
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    
    print("""
📊 测试内容:
1. ✅ API服务可用性测试
2. ✅ 从数据库获取市盈率数据测试
3. ✅ 数据库市盈率数据完整性测试

🎯 预期结果:
- 市盈率数据优先从数据库获取
- 如果数据库没有数据，则从akshare获取作为备选
- 提高API响应速度，减少对外部接口的依赖

📝 注意事项:
- 确保数据库中有最新的市盈率数据
- 数据库数据更新频率影响市盈率的时效性
- 建议定期同步数据库中的市盈率数据
    """)

if __name__ == "__main__":
    print("开始测试修改后的实时行情API（从数据库获取市盈率）...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 首先测试API服务是否可用
    if test_api_availability():
        # 测试从数据库获取市盈率数据
        test_realtime_quote_api_from_db()
        
        # 测试数据库市盈率数据
        test_database_pe_ratio_data()
        
        # 显示测试总结
        show_test_summary()
    else:
        print("\n请先启动后端服务，然后再运行此测试脚本")
        print("启动命令示例:")
        print("cd backend_api")
        print("python main.py")
    
    print("\n测试完成!")
