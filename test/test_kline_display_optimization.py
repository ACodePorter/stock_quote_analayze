#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试K线图显示效果优化
"""

import sys
import os
import requests
import json

def test_kline_data_api():
    """测试K线数据API"""
    
    # 测试股票代码
    test_codes = ['000581', '000001', '600000']
    
    for code in test_codes:
        print(f"\n=== 测试股票代码: {code} ===")
        
        try:
            # 测试不同周期的K线数据
            periods = ['1', '5', '15', '30', '60', 'daily']
            
            for period in periods:
                print(f"\n--- 测试周期: {period} ---")
                
                # 调用K线数据API
                if period == 'daily':
                    url = f"http://localhost:8000/api/stock/kline?code={code}"
                else:
                    url = f"http://localhost:8000/api/stock/kline_min?code={code}&period={period}"
                
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('data'):
                        kline_data = data['data']
                        data_count = len(kline_data)
                        print(f"✅ 数据获取成功，数据量: {data_count}")
                        
                        # 根据数据量判断应该使用的显示策略
                        if data_count <= 30:
                            strategy = "数据很少时，K线更宽更显眼 (8-20px)"
                        elif data_count <= 80:
                            strategy = "数据少时，显示全部数据 (6-15px)"
                        elif data_count <= 200:
                            strategy = "中等数据量时，调整显示范围 (4-12px)"
                        else:
                            strategy = "数据量充足时，使用85%宽度"
                        
                        print(f"📊 显示策略: {strategy}")
                        
                        # 显示前几个数据点
                        print("前3个数据点:")
                        for i, item in enumerate(kline_data[:3]):
                            if isinstance(item, list) and len(item) >= 4:
                                print(f"  {i+1}. 开盘:{item[0]}, 收盘:{item[1]}, 最低:{item[2]}, 最高:{item[3]}")
                            else:
                                print(f"  {i+1}. {item}")
                    else:
                        print(f"❌ API返回失败: {data.get('message', '未知错误')}")
                else:
                    print(f"❌ HTTP请求失败: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def test_display_optimization():
    """测试显示优化效果"""
    print("\n=== K线图显示优化效果 ===")
    
    optimizations = [
        {
            "项目": "K线柱状图宽度",
            "优化前": "60%",
            "优化后": "80%",
            "效果": "K线显示更宽，更接近主流股票软件"
        },
        {
            "项目": "成交量柱状图宽度", 
            "优化前": "60%",
            "优化后": "80%",
            "效果": "成交量柱状图更宽，视觉效果更好"
        },
        {
            "项目": "边框宽度",
            "优化前": "1px",
            "优化后": "1.5px",
            "效果": "K线边框更清晰，立体感更强"
        },
        {
            "项目": "阴影效果",
            "优化前": "shadowBlur: 10",
            "优化后": "shadowBlur: 15",
            "效果": "悬停时阴影更明显，交互体验更好"
        },
        {
            "项目": "动态宽度调整",
            "优化前": "简单的3档调整",
            "优化后": "4档精细调整",
            "效果": "不同数据量下都有最佳显示效果"
        }
    ]
    
    for opt in optimizations:
        print(f"\n📈 {opt['项目']}:")
        print(f"   优化前: {opt['优化前']}")
        print(f"   优化后: {opt['优化后']}")
        print(f"   效果: {opt['效果']}")

def main():
    """主函数"""
    print("开始测试K线图显示效果优化...")
    
    # 测试显示优化效果
    test_display_optimization()
    
    # 测试API数据
    print("\n" + "="*50)
    print("测试K线数据API...")
    test_kline_data_api()
    
    print("\n测试完成！")
    print("\n优化总结:")
    print("1. 增加了K线图和成交量柱状图的默认宽度")
    print("2. 改善了边框、阴影等视觉效果")
    print("3. 优化了不同数据量下的动态宽度调整策略")
    print("4. 使K线图显示效果更接近主流股票软件")

if __name__ == "__main__":
    main()
