#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

def test_sixty_day_change():
    """测试60天涨跌计算功能"""
    print("测试60天涨跌计算功能...")
    
    # 测试API端点
    url = "http://localhost:5000/api/stock/history/calculate_sixty_day_change"
    data = {
        "stock_code": "603667",
        "start_date": "2025-08-01", 
        "end_date": "2025-09-02"
    }
    
    try:
        print(f"发送请求到: {url}")
        print(f"请求数据: {data}")
        
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=data, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 60天涨跌计算API测试成功！")
            return True
        else:
            print("❌ 60天涨跌计算API测试失败")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务，请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

if __name__ == "__main__":
    test_sixty_day_change()
