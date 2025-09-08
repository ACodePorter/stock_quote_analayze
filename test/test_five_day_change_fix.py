#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的5天升跌计算功能
"""

import requests
import json
from datetime import datetime, timedelta

# API基础URL
API_BASE_URL = "http://localhost:8000"

def test_calculate_five_day_change():
    """测试5天升跌计算功能"""
    print("=== 测试5天升跌计算功能 ===")
    
    # 测试股票代码
    stock_code = "300058"
    
    # 设置日期范围（确保有足够的数据）
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"股票代码: {stock_code}")
    print(f"开始日期: {start_date}")
    print(f"结束日期: {end_date}")
    
    # 1. 先获取当前的历史数据，查看5天升跌%字段状态
    print("\n1. 获取当前历史数据...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/stock/history", params={
            "code": stock_code,
            "start_date": start_date,
            "end_date": end_date,
            "page": 1,
            "size": 50,
            "include_notes": False
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"获取到 {len(data['items'])} 条记录")
            
            # 检查5天升跌%字段状态
            null_count = 0
            zero_count = 0
            has_value_count = 0
            
            for item in data['items']:
                if item.get('five_day_change_percent') is None:
                    null_count += 1
                elif item.get('five_day_change_percent') == 0:
                    zero_count += 1
                else:
                    has_value_count += 1
            
            print(f"5天升跌%字段状态:")
            print(f"  - NULL值: {null_count}")
            print(f"  - 0值: {zero_count}")
            print(f"  - 有值: {has_value_count}")
            
        else:
            print(f"获取历史数据失败: {response.status_code}")
            print(response.text)
            return
            
    except Exception as e:
        print(f"获取历史数据异常: {e}")
        return
    
    # 2. 调用5天升跌计算API
    print("\n2. 调用5天升跌计算API...")
    try:
        response = requests.post(f"{API_BASE_URL}/api/stock/history/calculate_five_day_change", json={
            "stock_code": stock_code,
            "start_date": start_date,
            "end_date": end_date
        })
        
        if response.status_code == 200:
            result = response.json()
            print("计算成功!")
            print(f"消息: {result['message']}")
            print(f"更新记录数: {result['updated_count']}")
            print(f"总记录数: {result['total_records']}")
        else:
            print(f"计算失败: {response.status_code}")
            print(response.text)
            return
            
    except Exception as e:
        print(f"调用计算API异常: {e}")
        return
    
    # 3. 再次获取历史数据，验证计算结果
    print("\n3. 验证计算结果...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/stock/history", params={
            "code": stock_code,
            "start_date": start_date,
            "end_date": end_date,
            "page": 1,
            "size": 50,
            "include_notes": False
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"获取到 {len(data['items'])} 条记录")
            
            # 再次检查5天升跌%字段状态
            null_count_after = 0
            zero_count_after = 0
            has_value_count_after = 0
            
            for item in data['items']:
                if item.get('five_day_change_percent') is None:
                    null_count_after += 1
                elif item.get('five_day_change_percent') == 0:
                    zero_count_after += 0
                else:
                    has_value_count_after += 1
            
            print(f"计算后的5天升跌%字段状态:")
            print(f"  - NULL值: {null_count_after}")
            print(f"  - 0值: {zero_count_after}")
            print(f"  - 有值: {has_value_count_after}")
            
            # 显示具体的计算结果
            print(f"\n具体的5天升跌%计算结果:")
            for item in data['items'][:10]:  # 只显示前10条
                date = item['date']
                close = item['close']
                five_day_change = item.get('five_day_change_percent')
                if five_day_change is not None:
                    print(f"  {date}: 收盘价={close}, 5天升跌%={five_day_change}%")
                else:
                    print(f"  {date}: 收盘价={close}, 5天升跌%=未计算")
            
        else:
            print(f"获取历史数据失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"验证计算结果异常: {e}")

def test_multiple_calculations():
    """测试多次计算是否正常工作"""
    print("\n=== 测试多次计算功能 ===")
    
    stock_code = "300058"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"对同一日期范围进行第二次计算...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/stock/history/calculate_five_day_change", json={
            "stock_code": stock_code,
            "start_date": start_date,
            "end_date": end_date
        })
        
        if response.status_code == 200:
            result = response.json()
            print("第二次计算成功!")
            print(f"消息: {result['message']}")
            print(f"更新记录数: {result['updated_count']}")
            print(f"总记录数: {result['total_records']}")
            
            # 如果更新记录数为0，说明所有记录都已经计算过了
            if result['updated_count'] == 0:
                print("✓ 所有记录都已经计算完成，无需重复计算")
            else:
                print(f"⚠ 仍有 {result['updated_count']} 条记录被更新")
                
        else:
            print(f"第二次计算失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"第二次计算异常: {e}")

def main():
    """主函数"""
    print("开始测试修复后的5天升跌计算功能...")
    print(f"API基础URL: {API_BASE_URL}")
    print("=" * 50)
    
    try:
        # 测试基本功能
        test_calculate_five_day_change()
        
        # 测试多次计算
        test_multiple_calculations()
        
        print("\n" + "=" * 50)
        print("测试完成!")
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生异常: {e}")

if __name__ == "__main__":
    main()
