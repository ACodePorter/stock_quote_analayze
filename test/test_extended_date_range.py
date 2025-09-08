#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试延长日期范围后的5天升跌计算功能
"""

import requests
import json
from datetime import datetime, timedelta

# API基础URL
API_BASE_URL = "http://localhost:8000"

def add_business_days(date_str, days):
    """添加工作日（跳过周末）"""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    added_days = 0
    current_date = date
    
    while added_days < days:
        current_date += timedelta(days=1)
        
        # 跳过周末（周一=0，周日=6）
        if current_date.weekday() < 5:  # 0-4 表示周一到周五
            added_days += 1
    
    return current_date.strftime("%Y-%m-%d")

def test_extended_date_range_calculation():
    """测试延长日期范围后的5天升跌计算功能"""
    print("=== 测试延长日期范围后的5天升跌计算功能 ===")
    
    # 测试股票代码
    stock_code = "300058"
    
    # 设置日期范围
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # 延长结束日期5个工作日
    extended_end_date = add_business_days(end_date, 5)
    
    print(f"股票代码: {stock_code}")
    print(f"原始开始日期: {start_date}")
    print(f"原始结束日期: {end_date}")
    print(f"延长后结束日期: {extended_end_date}")
    
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
            dash_count = 0
            
            for item in data['items']:
                if item.get('five_day_change_percent') is None:
                    null_count += 1
                elif item.get('five_day_change_percent') == 0:
                    zero_count += 1
                elif item.get('five_day_change_percent') == '-':
                    dash_count += 1
                else:
                    has_value_count += 1
            
            print(f"5天升跌%字段状态:")
            print(f"  - NULL值: {null_count}")
            print(f"  - 0值: {zero_count}")
            print(f"  - 破折号(-): {dash_count}")
            print(f"  - 有值: {has_value_count}")
            
            # 显示最后几条记录的状态
            print(f"\n最后5条记录的5天升跌%状态:")
            for i, item in enumerate(data['items'][:5]):
                date = item['date']
                close = item['close']
                five_day_change = item.get('five_day_change_percent')
                status = "有值" if five_day_change and five_day_change != '-' else "无值"
                print(f"  {date}: 收盘价={close}, 5天升跌%={five_day_change}, 状态={status}")
            
        else:
            print(f"获取历史数据失败: {response.status_code}")
            print(response.text)
            return
            
    except Exception as e:
        print(f"获取历史数据异常: {e}")
        return
    
    # 2. 调用5天升跌计算API（使用延长的日期范围）
    print(f"\n2. 调用5天升跌计算API（使用延长的日期范围）...")
    try:
        response = requests.post(f"{API_BASE_URL}/api/stock/history/calculate_five_day_change", json={
            "stock_code": stock_code,
            "start_date": start_date,
            "end_date": extended_end_date
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
            dash_count_after = 0
            
            for item in data['items']:
                if item.get('five_day_change_percent') is None:
                    null_count_after += 1
                elif item.get('five_day_change_percent') == 0:
                    zero_count_after += 1
                elif item.get('five_day_change_percent') == '-':
                    dash_count_after += 1
                else:
                    has_value_count_after += 1
            
            print(f"计算后的5天升跌%字段状态:")
            print(f"  - NULL值: {null_count_after}")
            print(f"  - 0值: {zero_count_after}")
            print(f"  - 破折号(-): {dash_count_after}")
            print(f"  - 有值: {has_value_count_after}")
            
            # 显示最后几条记录的状态
            print(f"\n计算后最后5条记录的5天升跌%状态:")
            for i, item in enumerate(data['items'][:5]):
                date = item['date']
                close = item['close']
                five_day_change = item.get('five_day_change_percent')
                status = "有值" if five_day_change and five_day_change != '-' else "无值"
                print(f"  {date}: 收盘价={close}, 5天升跌%={five_day_change}, 状态={status}")
            
            # 统计改进情况
            improvement = has_value_count_after - has_value_count
            if improvement > 0:
                print(f"\n✓ 改进效果: 新增了 {improvement} 条有值的记录")
            elif improvement == 0:
                print(f"\n✓ 所有记录都已经有值，无需改进")
            else:
                print(f"\n⚠ 异常情况: 有值记录减少了 {abs(improvement)} 条")
            
        else:
            print(f"获取历史数据失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"验证计算结果异常: {e}")

def test_business_day_calculation():
    """测试工作日计算函数"""
    print("\n=== 测试工作日计算函数 ===")
    
    test_dates = [
        "2025-01-20",  # 周一
        "2025-01-21",  # 周二
        "2025-01-22",  # 周三
        "2025-01-23",  # 周四
        "2025-01-24",  # 周五
        "2025-01-25",  # 周六
        "2025-01-26",  # 周日
    ]
    
    for test_date in test_dates:
        extended_date = add_business_days(test_date, 5)
        print(f"原始日期: {test_date} -> 延长5个工作日: {extended_date}")

def main():
    """主函数"""
    print("开始测试延长日期范围后的5天升跌计算功能...")
    print(f"API基础URL: {API_BASE_URL}")
    print("=" * 60)
    
    try:
        # 测试工作日计算
        test_business_day_calculation()
        
        # 测试延长日期范围的计算
        test_extended_date_range_calculation()
        
        print("\n" + "=" * 60)
        print("测试完成!")
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生异常: {e}")

if __name__ == "__main__":
    main()
