#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试支撑阻力位计算逻辑
验证支撑位价格不能大于当前价格的问题
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend_api'))

from stock.stock_analysis import KeyLevels
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_support_resistance_logic():
    """测试支撑阻力位计算逻辑"""
    
    # 测试数据：当前价格73.65
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
    
    logger.info(f"测试当前价格: {current_price}")
    logger.info(f"历史数据长度: {len(historical_data)}")
    
    # 计算关键价位
    key_levels = KeyLevels.calculate_key_levels(historical_data, current_price)
    
    logger.info("=== 计算结果 ===")
    logger.info(f"当前价格: {key_levels['current_price']}")
    logger.info(f"支撑位: {key_levels['support_levels']}")
    logger.info(f"阻力位: {key_levels['resistance_levels']}")
    
    # 验证支撑位逻辑
    support_levels = key_levels['support_levels']
    resistance_levels = key_levels['resistance_levels']
    
    print("\n=== 验证结果 ===")
    
    # 检查支撑位是否都小于当前价格
    support_valid = True
    for i, level in enumerate(support_levels):
        if level >= current_price:
            print(f"❌ 支撑位{i+1} ({level}) 大于等于当前价格 ({current_price})")
            support_valid = False
        else:
            print(f"✅ 支撑位{i+1} ({level}) 小于当前价格 ({current_price})")
    
    # 检查阻力位是否都大于当前价格
    resistance_valid = True
    for i, level in enumerate(resistance_levels):
        if level <= current_price:
            print(f"❌ 阻力位{i+1} ({level}) 小于等于当前价格 ({current_price})")
            resistance_valid = False
        else:
            print(f"✅ 阻力位{i+1} ({level}) 大于当前价格 ({current_price})")
    
    # 总结
    print(f"\n=== 总结 ===")
    if support_valid and resistance_valid:
        print("✅ 所有支撑阻力位计算逻辑正确")
        return True
    else:
        print("❌ 支撑阻力位计算逻辑存在问题")
        return False

def test_psychological_levels():
    """测试心理价位计算"""
    current_price = 73.65
    
    print(f"\n=== 测试心理价位计算 ===")
    print(f"当前价格: {current_price}")
    
    # 测试支撑位心理价位
    support_levels = KeyLevels._calculate_psychological_levels(current_price, is_support=True)
    print(f"支撑位心理价位: {support_levels}")
    
    # 测试阻力位心理价位
    resistance_levels = KeyLevels._calculate_psychological_levels(current_price, is_support=False)
    print(f"阻力位心理价位: {resistance_levels}")
    
    # 验证支撑位心理价位
    print("\n支撑位心理价位验证:")
    for level in support_levels:
        if level < current_price:
            print(f"✅ {level} < {current_price}")
        else:
            print(f"❌ {level} >= {current_price}")
    
    # 验证阻力位心理价位
    print("\n阻力位心理价位验证:")
    for level in resistance_levels:
        if level > current_price:
            print(f"✅ {level} > {current_price}")
        else:
            print(f"❌ {level} <= {current_price}")

def test_filter_and_sort():
    """测试过滤和排序逻辑"""
    current_price = 73.65
    
    print(f"\n=== 测试过滤和排序逻辑 ===")
    print(f"当前价格: {current_price}")
    
    # 测试数据：包含一些错误的价位
    test_levels = [70.0, 72.0, 73.65, 74.0, 75.0, 76.0, 77.0]
    
    # 测试支撑位过滤
    support_levels = KeyLevels._filter_and_sort_levels(test_levels, current_price, is_support=True)
    print(f"支撑位过滤结果: {support_levels}")
    
    # 测试阻力位过滤
    resistance_levels = KeyLevels._filter_and_sort_levels(test_levels, current_price, is_support=False)
    print(f"阻力位过滤结果: {resistance_levels}")
    
    # 验证结果
    print("\n支撑位验证:")
    for level in support_levels:
        if level < current_price:
            print(f"✅ {level} < {current_price}")
        else:
            print(f"❌ {level} >= {current_price}")
    
    print("\n阻力位验证:")
    for level in resistance_levels:
        if level > current_price:
            print(f"✅ {level} > {current_price}")
        else:
            print(f"❌ {level} <= {current_price}")

if __name__ == "__main__":
    print("开始测试支撑阻力位计算逻辑...")
    
    # 运行所有测试
    test_psychological_levels()
    test_filter_and_sort()
    result = test_support_resistance_logic()
    
    if result:
        print("\n🎉 所有测试通过！支撑阻力位计算逻辑正确。")
    else:
        print("\n⚠️ 测试发现问题，需要修复支撑阻力位计算逻辑。")
