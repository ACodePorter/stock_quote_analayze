#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试导出功能修复
"""

import requests

def test_export_with_notes():
    """测试包含备注的导出功能"""
    print("测试包含备注的导出功能...")
    
    url = "http://localhost:5000/api/stock/history/export"
    params = {
        "code": "300058",
        "start_date": "2025-05-01",
        "end_date": "2025-08-29",
        "include_notes": True
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ 包含备注导出成功!")
            print(f"响应大小: {len(response.content)} 字节")
            return True
        else:
            print(f"✗ 包含备注导出失败")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        return False

def test_export_without_notes():
    """测试不包含备注的导出功能"""
    print("\n测试不包含备注的导出功能...")
    
    url = "http://localhost:5000/api/stock/history/export"
    params = {
        "code": "300058",
        "start_date": "2025-05-01",
        "end_date": "2025-08-29",
        "include_notes": False
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ 不包含备注导出成功!")
            print(f"响应大小: {len(response.content)} 字节")
            return True
        else:
            print(f"✗ 不包含备注导出失败")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("测试导出功能修复")
    print("=" * 50)
    
    # 测试包含备注的导出
    success1 = test_export_with_notes()
    
    # 测试不包含备注的导出
    success2 = test_export_without_notes()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✓ 所有测试通过！导出功能修复成功！")
    else:
        print("✗ 部分测试失败，需要进一步检查")
    print("=" * 50)
