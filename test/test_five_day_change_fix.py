#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试5天升跌计算修复
验证最后5天数据是否能正确计算5天升跌%
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置
API_BASE_URL = "http://localhost:5000"
TEST_STOCK_CODE = "603667"  # 使用图片中的股票代码

def test_five_day_change_calculation():
    """测试5天升跌计算功能"""
    print("=" * 60)
    print("测试5天升跌计算修复")
    print("=" * 60)
    
    # 设置测试日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # 最近30天
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    print(f"测试股票代码: {TEST_STOCK_CODE}")
    print(f"测试日期范围: {start_date_str} 到 {end_date_str}")
    print()
    
    # 1. 先查询原始数据
    print("1. 查询原始历史数据...")
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/stock/history",
            params={
                "code": TEST_STOCK_CODE,
                "start_date": start_date_str,
                "end_date": end_date_str,
                "include_notes": False,
                "page": 1,
                "size": 50
            }
        )
        
        if response.status_code != 200:
            print(f"❌ 查询历史数据失败: {response.status_code}")
            return False
            
        data = response.json()
        print(f"✅ 查询成功，共 {data['total']} 条记录")
        
        # 检查最后5条记录的5天升跌%情况
        items = data['items']
        print(f"前5条记录的5天升跌%情况:")
        for i, item in enumerate(items[:5]):
            five_day_change = item.get('five_day_change_percent')
            status = "✅ 已计算" if five_day_change is not None else "❌ 未计算"
            print(f"  {item['date']}: {five_day_change}% ({status})")
            
    except Exception as e:
        print(f"❌ 查询历史数据异常: {e}")
        return False
    
    # 2. 执行5天升跌计算
    print("\n2. 执行5天升跌计算...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/stock/history/calculate_five_day_change",
            headers={"Content-Type": "application/json"},
            json={
                "stock_code": TEST_STOCK_CODE,
                "start_date": start_date_str,
                "end_date": end_date_str
            }
        )
        
        if response.status_code != 200:
            print(f"❌ 计算5天升跌失败: {response.status_code}")
            error_data = response.json()
            print(f"错误信息: {error_data}")
            return False
            
        result = response.json()
        print(f"✅ 计算完成: {result['message']}")
        print(f"更新记录数: {result['updated_count']}")
        print(f"总记录数: {result['total_records']}")
        
    except Exception as e:
        print(f"❌ 计算5天升跌异常: {e}")
        return False
    
    # 3. 再次查询数据验证结果
    print("\n3. 验证计算结果...")
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/stock/history",
            params={
                "code": TEST_STOCK_CODE,
                "start_date": start_date_str,
                "end_date": end_date_str,
                "include_notes": False,
                "page": 1,
                "size": 50
            }
        )
        
        if response.status_code != 200:
            print(f"❌ 验证查询失败: {response.status_code}")
            return False
            
        data = response.json()
        items = data['items']
        
        # 检查最后5条记录的5天升跌%情况
        print(f"计算后前5条记录的5天升跌%情况:")
        success_count = 0
        for i, item in enumerate(items[:5]):
            five_day_change = item.get('five_day_change_percent')
            if five_day_change is not None:
                status = "✅ 已计算"
                success_count += 1
            else:
                status = "❌ 未计算"
            print(f"  {item['date']}: {five_day_change}% ({status})")
        
        print(f"\n📊 测试结果: {success_count}/5 条记录成功计算5天升跌%")
        
        if success_count == 5:
            print("🎉 测试通过！所有最后5天数据都成功计算了5天升跌%")
            return True
        else:
            print("⚠️ 测试部分通过，仍有部分记录未计算")
            return False
            
    except Exception as e:
        print(f"❌ 验证查询异常: {e}")
        return False

def test_edge_cases():
    """测试边界情况"""
    print("\n" + "=" * 60)
    print("测试边界情况")
    print("=" * 60)
    
    # 测试数据不足的情况
    print("1. 测试数据不足的情况...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/stock/history/calculate_five_day_change",
            headers={"Content-Type": "application/json"},
            json={
                "stock_code": "INVALID_CODE",
                "start_date": "2024-01-01",
                "end_date": "2024-01-05"
            }
        )
        
        if response.status_code == 400:
            print("✅ 正确处理了数据不足的情况")
        else:
            print(f"⚠️ 数据不足情况处理异常: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 边界测试异常: {e}")

if __name__ == "__main__":
    print("开始测试5天升跌计算修复...")
    print(f"API地址: {API_BASE_URL}")
    print()
    
    # 检查API是否可用
    try:
        response = requests.get(f"{API_BASE_URL}/api/stock/history?code=000001&page=1&size=1", timeout=5)
        if response.status_code == 200:
            print("✅ API服务正常")
        else:
            print("⚠️ API服务响应异常")
    except Exception as e:
        print(f"❌ API服务不可用: {e}")
        print("请确保后端API服务正在运行")
        sys.exit(1)
    
    # 执行测试
    success = test_five_day_change_calculation()
    test_edge_cases()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 所有测试完成，修复验证成功！")
    else:
        print("⚠️ 测试完成，但存在问题需要进一步检查")
    print("=" * 60)
