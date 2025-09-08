#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导出功能是否包含备注信息
"""

import requests
import csv
import io
from datetime import datetime, timedelta

# API基础URL
API_BASE_URL = "http://localhost:8000"

def test_export_with_notes():
    """测试包含备注的导出功能"""
    print("=== 测试包含备注的导出功能 ===")
    
    # 测试股票代码
    stock_code = "300058"
    
    # 设置日期范围
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"股票代码: {stock_code}")
    print(f"开始日期: {start_date}")
    print(f"结束日期: {end_date}")
    
    # 1. 测试包含备注的导出
    print("\n1. 测试包含备注的导出...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/stock/history/export", params={
            "code": stock_code,
            "start_date": start_date,
            "end_date": end_date,
            "include_notes": True
        })
        
        if response.status_code == 200:
            print("导出成功!")
            
            # 解析CSV内容
            csv_content = response.content.decode('utf-8-sig')  # 去掉BOM头
            csv_reader = csv.reader(io.StringIO(csv_content))
            
            # 读取表头
            headers = next(csv_reader)
            print(f"CSV表头: {headers}")
            
            # 检查是否包含备注相关列
            has_user_notes = "用户备注" in headers
            has_strategy_type = "策略类型" in headers
            has_risk_level = "风险等级" in headers
            
            print(f"包含用户备注列: {has_user_notes}")
            print(f"包含策略类型列: {has_strategy_type}")
            print(f"包含风险等级列: {has_risk_level}")
            
            # 读取前几行数据
            row_count = 0
            for row in csv_reader:
                if row_count < 5:  # 只显示前5行
                    print(f"第{row_count + 1}行: {row}")
                row_count += 1
                if row_count >= 10:  # 最多显示10行
                    break
            
            print(f"总行数: {row_count}")
            
        else:
            print(f"导出失败: {response.status_code}")
            print(response.text)
            return
            
    except Exception as e:
        print(f"导出异常: {e}")
        return
    
    # 2. 测试不包含备注的导出
    print("\n2. 测试不包含备注的导出...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/stock/history/export", params={
            "code": stock_code,
            "start_date": start_date,
            "end_date": end_date,
            "include_notes": False
        })
        
        if response.status_code == 200:
            print("导出成功!")
            
            # 解析CSV内容
            csv_content = response.content.decode('utf-8-sig')  # 去掉BOM头
            csv_reader = csv.reader(io.StringIO(csv_content))
            
            # 读取表头
            headers = next(csv_reader)
            print(f"CSV表头: {headers}")
            
            # 检查是否包含备注相关列
            has_user_notes = "用户备注" in headers
            has_strategy_type = "策略类型" in headers
            has_risk_level = "风险等级" in headers
            
            print(f"包含用户备注列: {has_user_notes}")
            print(f"包含策略类型列: {has_strategy_type}")
            print(f"包含风险等级列: {has_risk_level}")
            
        else:
            print(f"导出失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"导出异常: {e}")

def test_export_data_consistency():
    """测试导出数据的一致性"""
    print("\n=== 测试导出数据的一致性 ===")
    
    stock_code = "300058"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # 1. 获取API数据
    print("1. 获取API数据...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/stock/history", params={
            "code": stock_code,
            "start_date": start_date,
            "end_date": end_date,
            "page": 1,
            "size": 50,
            "include_notes": True
        })
        
        if response.status_code == 200:
            api_data = response.json()
            print(f"API获取到 {len(api_data['items'])} 条记录")
            
            # 2. 获取导出数据
            print("2. 获取导出数据...")
            export_response = requests.get(f"{API_BASE_URL}/api/stock/history/export", params={
                "code": stock_code,
                "start_date": start_date,
                "end_date": end_date,
                "include_notes": True
            })
            
            if export_response.status_code == 200:
                # 解析CSV内容
                csv_content = export_response.content.decode('utf-8-sig')
                csv_reader = csv.reader(io.StringIO(csv_content))
                
                # 跳过表头
                headers = next(csv_reader)
                
                # 比较数据
                export_count = 0
                for row in csv_reader:
                    export_count += 1
                
                print(f"导出数据行数: {export_count}")
                print(f"API数据行数: {len(api_data['items'])}")
                
                if export_count == len(api_data['items']):
                    print("✓ 数据行数一致")
                else:
                    print(f"⚠ 数据行数不一致: API={len(api_data['items'])}, 导出={export_count}")
                
                # 检查备注字段
                print("\n3. 检查备注字段...")
                notes_with_content = 0
                for item in api_data['items']:
                    if item.get('user_notes') and item['user_notes'].strip():
                        notes_with_content += 1
                        print(f"  有备注的记录: {item['date']} - {item['user_notes'][:50]}...")
                
                print(f"有备注内容的记录数: {notes_with_content}")
                
                if notes_with_content > 0:
                    print("✓ 发现备注内容，导出功能应该能正确显示")
                else:
                    print("⚠ 没有发现备注内容，可能需要先添加一些备注")
                
            else:
                print(f"导出失败: {export_response.status_code}")
                
        else:
            print(f"获取API数据失败: {response.status_code}")
            
    except Exception as e:
        print(f"测试数据一致性异常: {e}")

def main():
    """主函数"""
    print("开始测试导出功能是否包含备注信息...")
    print(f"API基础URL: {API_BASE_URL}")
    print("=" * 60)
    
    try:
        # 测试导出功能
        test_export_with_notes()
        
        # 测试数据一致性
        test_export_data_consistency()
        
        print("\n" + "=" * 60)
        print("测试完成!")
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生异常: {e}")

if __name__ == "__main__":
    main()
