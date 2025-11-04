#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试历史行情导出功能的格式化效果
"""

import requests
import csv
import io

# API基础URL
API_BASE_URL = "http://localhost:5000"

def test_export_format():
    """测试导出格式化功能"""
    
    print("🧪 测试历史行情导出格式化功能...")
    
    # 测试导出接口
    url = f"{API_BASE_URL}/api/stock/history/export"
    params = {
        "code": "300475",  # 使用聚光科技作为测试股票
        "start_date": "2025-09-01",
        "end_date": "2025-09-20",
        "include_notes": False
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            print("✅ 导出请求成功")
            
            # 解析CSV内容
            content = response.content.decode('utf-8-sig')  # 处理BOM
            csv_reader = csv.reader(io.StringIO(content))
            
            # 读取头部
            headers = next(csv_reader)
            print(f"📋 CSV头部: {headers}")
            
            # 读取前几行数据
            print("\n📊 导出数据示例:")
            for i, row in enumerate(csv_reader):
                if i >= 3:  # 只显示前3行数据
                    break
                
                print(f"第{i+1}行数据:")
                for j, (header, value) in enumerate(zip(headers, row)):
                    if "成交量" in header or "成交额" in header or "涨跌" in header:
                        print(f"  {header}: {value}")
                print()
                
        else:
            print(f"❌ 导出请求失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")

if __name__ == "__main__":
    test_export_format()