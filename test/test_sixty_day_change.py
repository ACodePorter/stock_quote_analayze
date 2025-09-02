#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime, timedelta

def test_sixty_day_change_api():
    """测试60天涨跌计算API"""
    print("=== 60天涨跌计算功能测试 ===")
    
    # 测试参数
    stock_code = "603667"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"测试股票代码: {stock_code}")
    print(f"开始日期: {start_date}")
    print(f"结束日期: {end_date}")
    
    # 1. 测试API端点是否存在
    print("\n1. 测试API端点存在性...")
    try:
        response = requests.get("http://localhost:5000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API服务正常运行")
        else:
            print("❌ API服务异常")
            return False
    except Exception as e:
        print(f"❌ 无法连接到API服务: {e}")
        return False
    
    # 2. 查询初始数据
    print("\n2. 查询初始历史数据...")
    try:
        query_url = f"http://localhost:5000/api/stock/history?code={stock_code}&start_date={start_date}&end_date={end_date}&page=1&size=10"
        response = requests.get(query_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 查询成功，获取到 {len(data['items'])} 条记录")
            
            # 检查60天涨跌字段是否存在
            if data['items']:
                first_item = data['items'][0]
                if 'sixty_day_change_percent' in first_item:
                    print(f"✅ 60天涨跌字段存在，当前值: {first_item['sixty_day_change_percent']}")
                else:
                    print("❌ 60天涨跌字段不存在")
                    return False
        else:
            print(f"❌ 查询失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 查询异常: {e}")
        return False
    
    # 3. 执行60天涨跌计算
    print("\n3. 执行60天涨跌计算...")
    try:
        calculate_url = "http://localhost:5000/api/stock/history/calculate_sixty_day_change"
        request_data = {
            "stock_code": stock_code,
            "start_date": start_date,
            "end_date": end_date
        }
        
        response = requests.post(
            calculate_url,
            headers={'Content-Type': 'application/json'},
            json=request_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 60天涨跌计算成功")
            print(f"   更新记录数: {result['updated_count']}")
            print(f"   总记录数: {result['total_records']}")
            print(f"   消息: {result['message']}")
        else:
            error_data = response.json()
            print(f"❌ 60天涨跌计算失败: {error_data.get('detail', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 60天涨跌计算异常: {e}")
        return False
    
    # 4. 验证计算结果
    print("\n4. 验证计算结果...")
    try:
        response = requests.get(query_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['items']:
                # 检查前几条记录的60天涨跌值
                for i, item in enumerate(data['items'][:5]):
                    sixty_day_value = item.get('sixty_day_change_percent')
                    if sixty_day_value is not None:
                        print(f"   记录 {i+1}: 60天涨跌% = {sixty_day_value}%")
                    else:
                        print(f"   记录 {i+1}: 60天涨跌% = 未计算")
                print("✅ 60天涨跌计算验证完成")
            else:
                print("❌ 没有数据可验证")
                return False
        else:
            print(f"❌ 验证查询失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 验证异常: {e}")
        return False
    
    # 5. 测试边界情况
    print("\n5. 测试边界情况...")
    
    # 测试数据不足的情况
    try:
        # 使用一个很短的日期范围，确保数据不足61天
        short_start = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        short_end = datetime.now().strftime("%Y-%m-%d")
        
        request_data = {
            "stock_code": stock_code,
            "start_date": short_start,
            "end_date": short_end
        }
        
        response = requests.post(
            calculate_url,
            headers={'Content-Type': 'application/json'},
            json=request_data,
            timeout=10
        )
        
        if response.status_code == 400:
            error_data = response.json()
            if "数据不足61天" in error_data.get('detail', ''):
                print("✅ 边界情况测试通过：数据不足时正确返回错误")
            else:
                print(f"❌ 边界情况测试失败：{error_data.get('detail', '')}")
        else:
            print("❌ 边界情况测试失败：应该返回400错误")
            
    except Exception as e:
        print(f"❌ 边界情况测试异常: {e}")
    
    print("\n=== 60天涨跌计算功能测试完成 ===")
    return True

if __name__ == "__main__":
    test_sixty_day_change_api()
