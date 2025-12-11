"""
低九策略单元测试
用于验证策略逻辑的正确性
"""

from stock.low_nine_strategy import LowNineStrategy


def test_low_nine_pattern():
    """测试低九策略形态识别"""
    
    # 测试用例1: 满足条件的数据
    print("=" * 50)
    print("测试用例1: 满足低九策略条件")
    print("=" * 50)
    
    # 构造测试数据：连续9天，每天收盘价都低于前4天
    # 数据是倒序的（最新在前）
    test_data_valid = []
    base_price = 10.0
    
    # 生成13天数据
    for i in range(13):
        # 从最新到最旧，价格逐渐升高
        # 这样可以确保每天的收盘价都低于前4天
        price = base_price + (i * 0.1)
        test_data_valid.append({
            'date': f'2025-12-{13-i:02d}',
            'close': price,
            'open': price + 0.05,
            'high': price + 0.1,
            'low': price - 0.05
        })
    
    is_valid, info = LowNineStrategy.check_low_nine_pattern(test_data_valid)
    
    print(f"结果: {'✓ 通过' if is_valid else '✗ 失败'}")
    if info:
        print(f"形态开始日期: {info['pattern_start_date']}")
        print(f"形态结束日期: {info['pattern_end_date']}")
        print(f"形态开始价格: {info['pattern_start_price']:.2f}")
        print(f"当前价格: {info['current_price']:.2f}")
        print(f"9天跌幅: {info['decline_ratio']*100:.2f}%")
        print(f"9天最高价: {info['max_price_in_9days']:.2f}")
        print(f"9天最低价: {info['min_price_in_9days']:.2f}")
    
    # 测试用例2: 不满足条件的数据（第5天不满足）
    print("\n" + "=" * 50)
    print("测试用例2: 不满足低九策略条件（中间有一天不符合）")
    print("=" * 50)
    
    test_data_invalid = []
    for i in range(13):
        if i == 4:
            # 第5天（索引4）的收盘价高于前4天，破坏形态
            price = base_price + (i * 0.1) + 1.0
        else:
            price = base_price + (i * 0.1)
        
        test_data_invalid.append({
            'date': f'2025-12-{13-i:02d}',
            'close': price,
            'open': price + 0.05,
            'high': price + 0.1,
            'low': price - 0.05
        })
    
    is_valid, info = LowNineStrategy.check_low_nine_pattern(test_data_invalid)
    
    print(f"结果: {'✓ 通过 (正确识别为不满足)' if not is_valid else '✗ 失败 (错误识别为满足)'}")
    
    # 测试用例3: 数据不足
    print("\n" + "=" * 50)
    print("测试用例3: 数据不足（少于13天）")
    print("=" * 50)
    
    test_data_insufficient = test_data_valid[:10]  # 只有10天数据
    
    is_valid, info = LowNineStrategy.check_low_nine_pattern(test_data_insufficient)
    
    print(f"结果: {'✓ 通过 (正确识别为数据不足)' if not is_valid else '✗ 失败 (错误处理数据不足)'}")
    
    # 测试用例4: 真实场景模拟 - 下跌趋势
    print("\n" + "=" * 50)
    print("测试用例4: 真实场景模拟 - 持续下跌")
    print("=" * 50)
    
    # 构造真实下跌场景：数据是倒序的（最新在前）
    # 最新的9天（索引0-8）每天都要低于其前4天（索引4-12）
    test_data_realistic = []
    
    # 从旧到新的价格序列（实际时间顺序）
    # 索引12-9: 前4天（较高价格）
    # 索引8-0: 后9天（逐渐下跌，每天都低于前4天）
    prices_chronological = [
        10.3, 10.2, 10.1, 10.0,  # 索引12-9: 前4天
        9.9, 9.8, 9.7, 9.6, 9.5, 9.4, 9.3, 9.2, 9.1  # 索引8-0: 后9天
    ]
    
    # 反转为倒序（最新在前）
    prices_reversed = list(reversed(prices_chronological))
    
    for i, price in enumerate(prices_reversed):
        test_data_realistic.append({
            'date': f'2025-12-{13-i:02d}',
            'close': price,
            'open': price + 0.05,
            'high': price + 0.1,
            'low': price - 0.05
        })
    
    # 打印前几天数据用于调试
    print("\n数据验证（前5天）:")
    for i in range(min(5, len(test_data_realistic))):
        fourth_day = test_data_realistic[i + 4] if i + 4 < len(test_data_realistic) else None
        fourth_close = fourth_day['close'] if fourth_day else None
        fourth_close_str = f"{fourth_close:.2f}" if fourth_close is not None else "N/A"
        is_valid_day = fourth_day and test_data_realistic[i]['close'] < fourth_day['close']
        print(f"  第{i+1}天: 日期={test_data_realistic[i]['date']}, "
              f"收盘={test_data_realistic[i]['close']:.2f}, "
              f"前4天收盘={fourth_close_str}, "
              f"满足条件={'✓' if is_valid_day else '✗'}")
    
    is_valid, info = LowNineStrategy.check_low_nine_pattern(test_data_realistic)
    
    print(f"\n结果: {'✓ 通过' if is_valid else '✗ 失败'}")
    if info:
        print(f"形态开始日期: {info['pattern_start_date']}")
        print(f"形态结束日期: {info['pattern_end_date']}")
        print(f"形态开始价格: {info['pattern_start_price']:.2f}")
        print(f"当前价格: {info['current_price']:.2f}")
        print(f"9天跌幅: {info['decline_ratio']*100:.2f}%")
        print(f"9天最高价: {info['max_price_in_9days']:.2f}")
        print(f"9天最低价: {info['min_price_in_9days']:.2f}")
    else:
        print("未找到符合条件的形态")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    test_low_nine_pattern()
