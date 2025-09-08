#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试5天升跌计算API
"""

import requests
import json
from datetime import datetime, timedelta

# 配置
API_BASE_URL = "http://localhost:8000"
TEST_STOCK_CODE = "000001"  # 平安银行

def test_calculate_five_day_change():
    """测试计算5天升跌%API"""
    print("🧪 测试5天升跌计算API")
    print("=" * 50)
    
    # 设置测试日期范围（最近30天）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    request_data = {
        "stock_code": TEST_STOCK_CODE,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    print(f"请求参数: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
    
    try:
        # 调用API
        response = requests.post(
            f"{API_BASE_URL}/api/stock/history/calculate_five_day_change",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print("✅ 计算成功!")
            print(f"响应结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 验证返回结果
            if "updated_count" in result and "message" in result:
                print(f"✅ 更新记录数: {result['updated_count']}")
                print(f"✅ 消息: {result['message']}")
            else:
                print("❌ 响应格式不正确")
                
        else:
            error_data = response.json()
            print(f"❌ 计算失败: {error_data.get('detail', '未知错误')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def test_get_stock_history():
    """测试获取股票历史数据，验证5天升跌%字段"""
    print("\n📊 测试获取股票历史数据")
    print("=" * 50)
    
    try:
        # 获取历史数据
        response = requests.get(
            f"{API_BASE_URL}/api/stock/history",
            params={
                "code": TEST_STOCK_CODE,
                "start_date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
                "include_notes": False,
                "page": 1,
                "size": 10
            }
        )
        
        if response.ok:
            data = response.json()
            print(f"✅ 获取历史数据成功，共 {data.get('total', 0)} 条记录")
            
            if "items" in data and len(data["items"]) > 0:
                # 检查5天升跌%字段
                items_with_five_day = [item for item in data["items"] if item.get("five_day_change_percent") is not None]
                items_without_five_day = [item for item in data["items"] if item.get("five_day_change_percent") is None]
                
                print(f"✅ 包含5天升跌%的记录: {len(items_with_five_day)} 条")
                print(f"⚠️  不包含5天升跌%的记录: {len(items_without_five_day)} 条")
                
                # 显示前几条记录
                print("\n前3条记录:")
                for i, item in enumerate(data["items"][:3]):
                    print(f"  {i+1}. 日期: {item.get('date')}, 收盘价: {item.get('close')}, 5天升跌%: {item.get('five_day_change_percent', 'N/A')}")
            else:
                print("❌ 未获取到历史数据")
        else:
            print(f"❌ 获取历史数据失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def main():
    """主函数"""
    print("🚀 开始测试5天升跌计算功能")
    print("=" * 60)
    
    # 1. 测试计算5天升跌%API
    test_calculate_five_day_change()
    
    # 2. 测试获取历史数据，验证计算结果
    test_get_stock_history()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成!")

if __name__ == "__main__":
    main()
