#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试历史行情导出格式化函数
"""

def test_format_functions():
    """测试格式化函数"""
    
    # 从history_api.py中复制的格式化函数
    def format_volume(volume):
        """格式化成交量为万手"""
        if volume is None:
            return '-'
        vol = float(volume)
        if vol >= 10000:
            return f"{vol / 10000:.2f}万手"
        return f"{vol:.0f}手"
    
    def format_amount(amount):
        """格式化成交额为亿"""
        if amount is None:
            return '-'
        amt = float(amount)
        return f"{amt / 100000000:.2f}亿"
    
    def format_percent(value):
        """格式化百分比"""
        if value is None:
            return '-'
        return f"{float(value):.2f}%"
    
    def format_price(value):
        """格式化价格"""
        if value is None:
            return '-'
        return f"{float(value):.2f}"
    
    print("🧪 测试格式化函数...")
    
    # 测试成交量格式化
    print("\n📊 成交量格式化测试:")
    test_volumes = [5723, 57230, 572300, 5723000, None]
    for vol in test_volumes:
        result = format_volume(vol)
        print(f"  原始值: {vol} -> 格式化: {result}")
    
    # 测试成交额格式化
    print("\n💰 成交额格式化测试:")
    test_amounts = [572340, 57234000, 572340000, 57234000000, 572340000000, None]
    for amt in test_amounts:
        result = format_amount(amt)
        print(f"  原始值: {amt} -> 格式化: {result}")
    
    # 测试百分比格式化
    print("\n📈 百分比格式化测试:")
    test_percents = [1.23, -2.45, 0, 10.12345, None]
    for pct in test_percents:
        result = format_percent(pct)
        print(f"  原始值: {pct} -> 格式化: {result}")
    
    # 测试价格格式化
    print("\n💵 价格格式化测试:")
    test_prices = [12.34, 123.456, 1.2, 0.01, None]
    for price in test_prices:
        result = format_price(price)
        print(f"  原始值: {price} -> 格式化: {result}")
    
    print("\n✅ 格式化函数测试完成!")

if __name__ == "__main__":
    test_format_functions()