#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试排序逻辑
"""

import pandas as pd

def test_sorting_logic():
    """测试排序逻辑"""
    
    # 模拟财务数据
    data = {
        '报告期': ['2024-12-31', '2023-12-31', '2022-12-31', '2021-12-31', '2020-12-31'],
        '净利润': [7.02, 8.5, 6.8, 9.2, 5.1],
        '净资产收益率': [3.49, 4.2, 3.1, 4.8, 2.9]
    }
    
    df = pd.DataFrame(data)
    print("原始数据:")
    print(df)
    
    # 测试降序排列（修复前）
    df_desc = df.sort_values("报告期", ascending=False)
    print("\n降序排列（修复前）:")
    print(df_desc)
    
    # 测试升序排列（修复后）
    df_asc = df.sort_values("报告期", ascending=True)
    print("\n升序排列（修复后）:")
    print(df_asc)
    
    print("\n结论:")
    print("修复前：年份从左到右是 2024 -> 2023 -> 2022 -> 2021 -> 2020 (高到低)")
    print("修复后：年份从左到右是 2020 -> 2021 -> 2022 -> 2023 -> 2024 (低到高)")

if __name__ == "__main__":
    test_sorting_logic()
