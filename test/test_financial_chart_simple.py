#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试财务数据盈利能力图表年份排序修复
"""

import requests
import json

def test_financial_indicator_list():
    """测试财务指标列表API的年份排序"""
    
    # 测试股票代码
    test_codes = ['000581', '000001']
    
    for code in test_codes:
        print(f"\n=== 测试股票代码: {code} ===")
        
        try:
            # 调用财务指标列表API
            url = f"http://localhost:8000/api/stock/financial_indicator_list?symbol={code}&indicator=2"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    periods = [item['报告期'] for item in data['data']]
                    print(f"报告期顺序: {periods}")
                    
                    # 检查是否按时间升序排列
                    is_ascending = True
                    for i in range(1, len(periods)):
                        if periods[i] < periods[i-1]:
                            is_ascending = False
                            break
                    
                    if is_ascending:
                        print("✅ 年份排序正确：从左到右按时间升序排列")
                    else:
                        print("❌ 年份排序错误：未按时间升序排列")
                        
                    # 显示前几个数据点
                    print("前5个数据点:")
                    for i, item in enumerate(data['data'][:5]):
                        print(f"  {i+1}. {item['报告期']} - 净利润: {item.get('净利润', 'N/A')} - ROE: {item.get('净资产收益率', 'N/A')}")
                        
                else:
                    print(f"❌ API返回失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

def main():
    """主函数"""
    print("开始测试财务数据盈利能力图表年份排序修复...")
    test_financial_indicator_list()
    print("\n测试完成！")

if __name__ == "__main__":
    main()
