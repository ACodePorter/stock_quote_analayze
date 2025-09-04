#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试全量采集功能
"""

import requests
import json
import time
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:5000"

def test_full_collection_mode():
    """测试全量采集模式"""
    print("🧪 测试全量采集功能...")
    
    # 1. 测试获取股票列表（包含全量采集状态）
    print("\n1. 获取股票列表（包含全量采集状态）...")
    try:
        response = requests.get(f"{BASE_URL}/data-collection/stock-list")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取到 {data['total']} 只股票")
            if data['stocks']:
                stock = data['stocks'][0]
                print(f"   示例股票: {stock['code']} - {stock['name']}")
                print(f"   全量采集状态: {stock.get('full_collection_completed', 'N/A')}")
                print(f"   完成时间: {stock.get('full_collection_date', 'N/A')}")
        else:
            print(f"❌ 获取股票列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取股票列表异常: {e}")
        return False
    
    # 2. 测试获取未完成全量采集的股票列表
    print("\n2. 获取未完成全量采集的股票列表...")
    try:
        response = requests.get(f"{BASE_URL}/data-collection/stock-list?only_uncompleted=true")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取到 {data['total']} 只未完成全量采集的股票")
            print(f"   过滤模式: {data['only_uncompleted']}")
        else:
            print(f"❌ 获取未完成股票列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取未完成股票列表异常: {e}")
        return False
    
    # 3. 测试启动全量采集任务（测试模式）
    print("\n3. 启动全量采集任务（测试模式）...")
    try:
        request_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-03",
            "stock_codes": None,  # 不指定股票代码，表示全量采集
            "test_mode": True,    # 测试模式
            "full_collection_mode": True  # 全量采集模式
        }
        
        response = requests.post(f"{BASE_URL}/data-collection/historical", json=request_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 任务启动成功: {data['task_id']}")
            print(f"   状态: {data['status']}")
            print(f"   全量采集模式: {data['full_collection_mode']}")
            print(f"   测试模式: {data['test_mode']}")
            
            # 等待任务完成
            task_id = data['task_id']
            print(f"\n4. 等待任务完成...")
            max_wait = 60  # 最多等待60秒
            wait_count = 0
            
            while wait_count < max_wait:
                time.sleep(2)
                wait_count += 2
                
                try:
                    status_response = requests.get(f"{BASE_URL}/data-collection/status/{task_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   进度: {status_data['progress']}% ({status_data['processed_stocks']}/{status_data['total_stocks']})")
                        
                        if status_data['status'] in ['completed', 'failed']:
                            print(f"   任务完成: {status_data['status']}")
                            print(f"   成功: {status_data['success_count']}, 失败: {status_data['failed_count']}")
                            print(f"   新增: {status_data['collected_count']}, 跳过: {status_data['skipped_count']}")
                            break
                    else:
                        print(f"   获取状态失败: {status_response.status_code}")
                        break
                except Exception as e:
                    print(f"   获取状态异常: {e}")
                    break
            
            if wait_count >= max_wait:
                print("   ⏰ 等待超时")
                
        else:
            print(f"❌ 启动任务失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 启动任务异常: {e}")
        return False
    
    # 5. 检查全量采集标志是否更新
    print("\n5. 检查全量采集标志更新情况...")
    try:
        response = requests.get(f"{BASE_URL}/data-collection/stock-list")
        if response.status_code == 200:
            data = response.json()
            completed_count = sum(1 for stock in data['stocks'] if stock.get('full_collection_completed', False))
            print(f"✅ 前100只股票中已完成全量采集: {completed_count} 只")
        else:
            print(f"❌ 检查更新情况失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 检查更新情况异常: {e}")
    
    print("\n✅ 全量采集功能测试完成！")
    return True

def test_single_stock_collection():
    """测试单只股票采集"""
    print("\n🧪 测试单只股票采集功能...")
    
    try:
        request_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-03",
            "stock_codes": ["000001"],  # 指定单只股票
            "test_mode": False,
            "full_collection_mode": False
        }
        
        response = requests.post(f"{BASE_URL}/data-collection/historical", json=request_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 单只股票采集任务启动成功: {data['task_id']}")
            print(f"   股票代码: {data['stock_codes']}")
            print(f"   全量采集模式: {data['full_collection_mode']}")
        else:
            print(f"❌ 单只股票采集任务启动失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 单只股票采集测试异常: {e}")

if __name__ == "__main__":
    print("🚀 开始测试数据采集API...")
    print(f"   目标服务器: {BASE_URL}")
    print(f"   测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试全量采集模式
    test_full_collection_mode()
    
    # 测试单只股票采集
    test_single_stock_collection()
    
    print("\n🎉 所有测试完成！")
