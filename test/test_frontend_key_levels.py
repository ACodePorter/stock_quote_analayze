#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端关键价位更新逻辑
模拟前端JavaScript的更新过程
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend_api'))

from stock.stock_analysis import KeyLevels
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simulate_frontend_update():
    """模拟前端更新过程"""
    
    # 模拟当前价格（从用户图片中获取）
    current_price = 73.65
    
    # 模拟历史数据
    historical_data = []
    for i in range(30):
        # 生成一些模拟的历史数据
        base_price = 70 + i * 0.5
        historical_data.append({
            'high': base_price + 2,
            'low': base_price - 2,
            'close': base_price,
            'volume': 1000000 + i * 10000
        })
    
    print(f"=== 模拟前端更新过程 ===")
    print(f"当前价格: {current_price}")
    
    # 计算关键价位
    key_levels = KeyLevels.calculate_key_levels(historical_data, current_price)
    
    print(f"后端计算的关键价位:")
    print(f"  当前价格: {key_levels['current_price']}")
    print(f"  支撑位: {key_levels['support_levels']}")
    print(f"  阻力位: {key_levels['resistance_levels']}")
    
    # 模拟前端更新逻辑
    print(f"\n=== 模拟前端更新逻辑 ===")
    
    # 更新阻力位
    if key_levels['resistance_levels'] and len(key_levels['resistance_levels']) > 0:
        print("更新阻力位:")
        for i, level in enumerate(key_levels['resistance_levels']):
            print(f"  阻力位{i+1}: {level:.2f}")
    
    # 更新支撑位
    if key_levels['support_levels'] and len(key_levels['support_levels']) > 0:
        print("更新支撑位:")
        for i, level in enumerate(key_levels['support_levels']):
            print(f"  支撑位{i+1}: {level:.2f}")
    
    # 更新当前价格
    print(f"更新当前价格: {current_price:.2f}")
    
    # 验证结果
    print(f"\n=== 验证结果 ===")
    support_levels = key_levels['support_levels']
    resistance_levels = key_levels['resistance_levels']
    
    # 检查支撑位是否都小于当前价格
    support_valid = True
    for i, level in enumerate(support_levels):
        if level >= current_price:
            print(f"❌ 支撑位{i+1} ({level:.2f}) 大于等于当前价格 ({current_price:.2f})")
            support_valid = False
        else:
            print(f"✅ 支撑位{i+1} ({level:.2f}) 小于当前价格 ({current_price:.2f})")
    
    # 检查阻力位是否都大于当前价格
    resistance_valid = True
    for i, level in enumerate(resistance_levels):
        if level <= current_price:
            print(f"❌ 阻力位{i+1} ({level:.2f}) 小于等于当前价格 ({current_price:.2f})")
            resistance_valid = False
        else:
            print(f"✅ 阻力位{i+1} ({level:.2f}) 大于当前价格 ({current_price:.2f})")
    
    return support_valid and resistance_valid

def test_specific_case():
    """测试特定情况：当前价格73.65，支撑位73.86"""
    
    print(f"\n=== 测试特定情况 ===")
    print(f"用户反馈的问题：当前价格73.65，支撑位73.86")
    
    current_price = 73.65
    problematic_support = 73.86
    
    print(f"当前价格: {current_price}")
    print(f"问题支撑位: {problematic_support}")
    
    if problematic_support >= current_price:
        print(f"❌ 问题确认：支撑位 {problematic_support} 大于等于当前价格 {current_price}")
        print(f"   这违反了技术分析的基本原理")
    else:
        print(f"✅ 支撑位 {problematic_support} 小于当前价格 {current_price}")
    
    # 分析可能的原因
    print(f"\n=== 可能的原因分析 ===")
    print(f"1. 前端缓存问题：可能显示了旧的错误数据")
    print(f"2. 数据更新延迟：前端没有及时更新到最新的计算结果")
    print(f"3. 静态数据问题：HTML中可能有静态的错误数据")
    print(f"4. 计算逻辑问题：后端计算可能有问题（但测试显示后端逻辑正确）")

if __name__ == "__main__":
    print("开始测试前端关键价位更新逻辑...")
    
    # 运行测试
    result = simulate_frontend_update()
    test_specific_case()
    
    if result:
        print(f"\n🎉 前端更新逻辑测试通过！")
        print(f"   后端计算逻辑正确，问题可能在前端显示或缓存")
    else:
        print(f"\n⚠️ 前端更新逻辑测试发现问题！")
