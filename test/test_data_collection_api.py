#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据采集API测试脚本
测试重构后的数据采集API服务功能
"""

import requests
import time
import json
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:5000"

def test_api_endpoints():
    """测试API端点可用性"""
    print("=== 测试API端点可用性 ===")
    
    endpoints = [
        "/data-collection/stock-list",
        "/data-collection/current-task",
        "/data-collection/tasks"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"✓ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"✗ {endpoint}: {e}")

def test_get_stock_list():
    """测试获取股票列表"""
    print("\n=== 测试获取股票列表 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/data-collection/stock-list")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 获取股票列表成功")
            print(f"  总股票数: {data.get('total', 0)}")
            print(f"  前5只股票: {data.get('stocks', [])[:5]}")
        else:
            print(f"✗ 获取股票列表失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 获取股票列表异常: {e}")

def test_get_current_task():
    """测试获取当前任务状态"""
    print("\n=== 测试获取当前任务状态 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/data-collection/current-task")
        if response.status_code == 200:
            data = response.json()
            current_task = data.get('current_task')
            if current_task:
                print(f"✓ 当前有任务运行中")
                print(f"  任务ID: {current_task.get('task_id')}")
                print(f"  状态: {current_task.get('status')}")
                print(f"  开始时间: {current_task.get('start_time')}")
            else:
                print("✓ 当前无任务运行")
        else:
            print(f"✗ 获取当前任务状态失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 获取当前任务状态异常: {e}")

def test_single_task_execution():
    """测试单任务执行逻辑"""
    print("\n=== 测试单任务执行逻辑 ===")
    
    # 设置测试日期
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 测试数据
    test_data = {
        "start_date": start_date,
        "end_date": end_date,
        "stock_codes": ["000001", "000002"],
        "test_mode": True
    }
    
    print("1. 启动第一个任务...")
    try:
        response1 = requests.post(f"{BASE_URL}/data-collection/historical", json=test_data)
        if response1.status_code == 200:
            task1_data = response1.json()
            task1_id = task1_data.get('task_id')
            print(f"✓ 第一个任务启动成功: {task1_id}")
            
            # 等待一小段时间让任务开始运行
            time.sleep(2)
            
            # 检查当前任务状态
            current_response = requests.get(f"{BASE_URL}/data-collection/current-task")
            if current_response.status_code == 200:
                current_data = current_response.json()
                current_task = current_data.get('current_task')
                if current_task and current_task.get('task_id') == task1_id:
                    print("✓ 单任务执行逻辑正常：当前任务ID匹配")
                else:
                    print("✗ 单任务执行逻辑异常：当前任务ID不匹配")
            
            print("2. 尝试启动第二个任务（应该被拒绝）...")
            response2 = requests.post(f"{BASE_URL}/data-collection/historical", json=test_data)
            if response2.status_code == 400:
                error_detail = response2.json().get('detail', '')
                if '已有采集任务正在运行' in error_detail:
                    print("✓ 单任务执行逻辑正常：第二个任务被正确拒绝")
                else:
                    print(f"✗ 单任务执行逻辑异常：错误信息不正确 - {error_detail}")
            else:
                print(f"✗ 单任务执行逻辑异常：第二个任务应该被拒绝，但返回 {response2.status_code}")
            
            # 等待第一个任务完成或取消它
            print("3. 等待任务完成或取消...")
            max_wait = 30  # 最多等待30秒
            wait_time = 0
            while wait_time < max_wait:
                status_response = requests.get(f"{BASE_URL}/data-collection/tasks")
                if status_response.status_code == 200:
                    tasks = status_response.json()
                    task1 = next((t for t in tasks if t.get('task_id') == task1_id), None)
                    if task1:
                        status = task1.get('status')
                        if status in ['completed', 'failed']:
                            print(f"✓ 第一个任务已完成，状态: {status}")
                            break
                        elif status == 'running':
                            print(f"  任务仍在运行中... (等待 {wait_time}s)")
                        else:
                            print(f"  任务状态: {status}")
                
                time.sleep(2)
                wait_time += 2
            
            # 如果任务仍在运行，取消它
            if wait_time >= max_wait:
                print("4. 取消仍在运行的任务...")
                cancel_response = requests.delete(f"{BASE_URL}/data-collection/tasks/{task1_id}")
                if cancel_response.status_code == 200:
                    print("✓ 任务取消成功")
                else:
                    print(f"✗ 任务取消失败: {cancel_response.status_code}")
            
            # 验证当前任务状态已清除
            time.sleep(1)
            final_current_response = requests.get(f"{BASE_URL}/data-collection/current-task")
            if final_current_response.status_code == 200:
                final_current_data = final_current_response.json()
                if not final_current_data.get('current_task'):
                    print("✓ 单任务执行逻辑正常：任务完成后当前任务状态已清除")
                else:
                    print("✗ 单任务执行逻辑异常：任务完成后当前任务状态未清除")
            
        else:
            print(f"✗ 第一个任务启动失败: {response1.status_code}")
            print(f"  错误信息: {response1.text}")
            
    except Exception as e:
        print(f"✗ 单任务执行测试异常: {e}")

def test_collection_modes():
    """测试不同的采集模式"""
    print("\n=== 测试不同的采集模式 ===")
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 测试单个股票采集
    print("1. 测试单个股票采集...")
    single_stock_data = {
        "start_date": start_date,
        "end_date": end_date,
        "stock_codes": ["000001"],
        "test_mode": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/data-collection/historical", json=single_stock_data)
        if response.status_code == 200:
            print("✓ 单个股票采集启动成功")
            task_id = response.json().get('task_id')
            
            # 等待任务完成
            wait_for_task_completion(task_id)
        else:
            print(f"✗ 单个股票采集启动失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 单个股票采集测试异常: {e}")
    
    # 测试多个股票采集
    print("2. 测试多个股票采集...")
    multiple_stocks_data = {
        "start_date": start_date,
        "end_date": end_date,
        "stock_codes": ["000001", "000002", "000858"],
        "test_mode": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/data-collection/historical", json=multiple_stocks_data)
        if response.status_code == 200:
            print("✓ 多个股票采集启动成功")
            task_id = response.json().get('task_id')
            
            # 等待任务完成
            wait_for_task_completion(task_id)
        else:
            print(f"✗ 多个股票采集启动失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 多个股票采集测试异常: {e}")
    
    # 测试全量采集（测试模式）
    print("3. 测试全量采集（测试模式）...")
    all_stocks_data = {
        "start_date": start_date,
        "end_date": end_date,
        "test_mode": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/data-collection/historical", json=all_stocks_data)
        if response.status_code == 200:
            print("✓ 全量采集启动成功")
            task_id = response.json().get('task_id')
            
            # 等待任务完成
            wait_for_task_completion(task_id)
        else:
            print(f"✗ 全量采集启动失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 全量采集测试异常: {e}")

def wait_for_task_completion(task_id, max_wait=60):
    """等待任务完成"""
    print(f"  等待任务 {task_id} 完成...")
    wait_time = 0
    while wait_time < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/data-collection/tasks")
            if response.status_code == 200:
                tasks = response.json()
                task = next((t for t in tasks if t.get('task_id') == task_id), None)
                if task:
                    status = task.get('status')
                    if status in ['completed', 'failed']:
                        print(f"  ✓ 任务完成，状态: {status}")
                        print(f"    统计: 总{task.get('total_stocks', 0)}, 成功{task.get('success_count', 0)}, 失败{task.get('failed_count', 0)}")
                        return
                    elif status == 'cancelled':
                        print(f"  ✓ 任务已取消")
                        return
                    else:
                        progress = task.get('progress', 0)
                        print(f"    进度: {progress}% (等待 {wait_time}s)")
            
            time.sleep(2)
            wait_time += 2
        except Exception as e:
            print(f"    等待过程中出错: {e}")
            time.sleep(2)
            wait_time += 2
    
    print(f"  ⚠ 任务等待超时 ({max_wait}s)")

def test_task_management():
    """测试任务管理功能"""
    print("\n=== 测试任务管理功能 ===")
    
    # 获取所有任务
    try:
        response = requests.get(f"{BASE_URL}/data-collection/tasks")
        if response.status_code == 200:
            tasks = response.json()
            print(f"✓ 获取任务列表成功，共 {len(tasks)} 个任务")
            
            # 显示最近的任务
            if tasks:
                recent_tasks = sorted(tasks, key=lambda x: x.get('start_time', ''), reverse=True)[:3]
                for i, task in enumerate(recent_tasks, 1):
                    print(f"  {i}. 任务ID: {task.get('task_id')}")
                    print(f"     状态: {task.get('status')}")
                    print(f"     开始时间: {task.get('start_time')}")
                    print(f"     统计: 总{task.get('total_stocks', 0)}, 成功{task.get('success_count', 0)}, 失败{task.get('failed_count', 0)}")
        else:
            print(f"✗ 获取任务列表失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 任务管理测试异常: {e}")

def main():
    """主函数"""
    print("数据采集API测试开始")
    print("=" * 50)
    
    # 测试API端点
    test_api_endpoints()
    
    # 测试获取股票列表
    test_get_stock_list()
    
    # 测试获取当前任务状态
    test_get_current_task()
    
    # 测试单任务执行逻辑
    test_single_task_execution()
    
    # 测试不同的采集模式
    test_collection_modes()
    
    # 测试任务管理功能
    test_task_management()
    
    print("\n" + "=" * 50)
    print("数据采集API测试完成")

if __name__ == "__main__":
    main()
