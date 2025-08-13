#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试时区问题修复的脚本
用于验证 backend_api/stock/stock_manage.py 中的时区处理逻辑
"""

import sys
import os
from datetime import datetime, timezone, timedelta
from dateutil import parser

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def test_timezone_parsing():
    """测试时区解析和格式化逻辑"""
    print("=== 测试时区问题修复 ===")
    
    # 模拟前端发送的ISO时间字符串
    test_cases = [
        "2025-08-09T06:15:33.616Z",  # UTC时间
        "2025-08-09T14:15:33+08:00",  # 带时区偏移
        "2025-08-09T06:15:33.616",   # 无时区信息
        "2025-08-09 06:15:33",       # 简单格式
    ]
    
    for test_time in test_cases:
        print(f"\n测试时间字符串: {test_time}")
        
        try:
            # 使用修复后的逻辑
            dt = parser.isoparse(test_time)
            print(f"  解析后的时间对象: {dt}")
            print(f"  时区信息: {dt.tzinfo}")
            
            # 转换为本地时间（去掉时区信息）
            if dt.tzinfo:
                dt_local = dt.astimezone().replace(tzinfo=None)
                print(f"  转换后的本地时间: {dt_local}")
            else:
                dt_local = dt
                print(f"  无需转换（无时区信息）")
            
            # 格式化为akshare期望的格式
            formatted = dt_local.strftime('%Y%m%d%H%M%S')
            print(f"  格式化后的结果: {formatted}")
            
        except Exception as e:
            print(f"  解析失败: {e}")
            # 使用备用方法
            try:
                backup_formatted = test_time.replace('-', '').replace(':', '').replace(' ', '')
                print(f"  备用方法结果: {backup_formatted}")
            except Exception as backup_e:
                print(f"  备用方法也失败: {backup_e}")

def test_edge_cases():
    """测试边界情况"""
    print("\n=== 测试边界情况 ===")
    
    edge_cases = [
        None,  # 空值
        "",    # 空字符串
        "invalid_time",  # 无效格式
        "2025-13-45T25:70:99",  # 无效日期时间
    ]
    
    for test_case in edge_cases:
        print(f"\n测试边界情况: {test_case}")
        
        try:
            if test_case is None:
                print("  空值，跳过处理")
                continue
                
            dt = parser.isoparse(test_case)
            formatted = dt.strftime('%Y%m%d%H%M%S')
            print(f"  成功解析并格式化: {formatted}")
            
        except Exception as e:
            print(f"  解析失败: {e}")
            # 使用备用方法
            try:
                if isinstance(test_case, str):
                    backup_formatted = test_case.replace('-', '').replace(':', '').replace(' ', '')
                    print(f"  备用方法结果: {backup_formatted}")
                else:
                    print("  备用方法不适用")
            except Exception as backup_e:
                print(f"  备用方法也失败: {backup_e}")

def test_akshare_format():
    """测试akshare期望的格式"""
    print("\n=== 测试akshare格式 ===")
    
    # 模拟当前时间
    now = datetime.now()
    print(f"当前时间: {now}")
    
    # 测试不同的时间周期
    periods = ['1', '5', '15', '30', '60']
    
    for period in periods:
        # 模拟前端发送的时间范围
        if period == '1':
            # 1分钟：当天数据
            start_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
            end_time = now.replace(hour=15, minute=0, second=0, microsecond=0)
        elif period == '5':
            # 5分钟：最近3天
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=3)
            end_time = now
        else:
            # 其他周期：最近7天
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
            end_time = now
        
        print(f"\n周期 {period} 分钟:")
        print(f"  开始时间: {start_time}")
        print(f"  结束时间: {end_time}")
        
        # 转换为ISO格式（模拟前端发送）
        start_iso = start_time.isoformat() + 'Z'
        end_iso = end_time.isoformat() + 'Z'
        print(f"  前端发送的开始时间: {start_iso}")
        print(f"  前端发送的结束时间: {end_iso}")
        
        # 使用修复后的逻辑处理
        try:
            start_dt = parser.isoparse(start_iso)
            end_dt = parser.isoparse(end_iso)
            
            if start_dt.tzinfo:
                start_dt = start_dt.astimezone().replace(tzinfo=None)
            if end_dt.tzinfo:
                end_dt = end_dt.astimezone().replace(tzinfo=None)
            
            start_formatted = start_dt.strftime('%Y%m%d%H%M%S')
            end_formatted = end_dt.strftime('%Y%m%d%H%M%S')
            
            print(f"  发送给akshare的开始时间: {start_formatted}")
            print(f"  发送给akshare的结束时间: {end_formatted}")
            
        except Exception as e:
            print(f"  处理失败: {e}")

if __name__ == "__main__":
    try:
        test_timezone_parsing()
        test_edge_cases()
        test_akshare_format()
        print("\n=== 所有测试完成 ===")
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装 python-dateutil: pip install python-dateutil")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
