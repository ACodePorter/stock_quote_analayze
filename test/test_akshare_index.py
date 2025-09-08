#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import akshare as ak
import pandas as pd

def test_akshare_indices():
    """测试akshare指数数据获取"""
    try:
        print("=== 测试akshare指数数据获取 ===")
        
        # 获取实时指数数据
        print("正在获取沪深重要指数数据...")
        df1 = ak.stock_zh_index_spot_em(symbol="沪深重要指数")
        print(f"沪深重要指数: 获取到 {len(df1)} 条数据")
        
        print("正在获取上证系列指数数据...")
        df2 = ak.stock_zh_index_spot_em(symbol="上证系列指数")
        print(f"上证系列指数: 获取到 {len(df2)} 条数据")
        
        print("正在获取深证系列指数数据...")
        df3 = ak.stock_zh_index_spot_em(symbol="深证系列指数")
        print(f"深证系列指数: 获取到 {len(df3)} 条数据")
        
        # 合并数据
        df = pd.concat([df1, df2, df3], ignore_index=True)
        df = df.drop_duplicates(subset=['代码'], keep='first')
        print(f"\n合并后总共 {len(df)} 条唯一指数数据")
        
        # 显示数据列名
        print("\n数据列名:")
        print(df.columns.tolist())
        
        # 显示前几条数据
        print("\n前5条数据:")
        print(df[['代码', '名称', '最新价', '涨跌额', '涨跌幅']].head())
        
        # 检查涨跌幅字段
        print("\n=== 涨跌幅字段分析 ===")
        print(f"涨跌幅字段类型: {df['涨跌幅'].dtype}")
        print(f"涨跌幅字段是否有null: {df['涨跌幅'].isnull().sum()}")
        print(f"涨跌幅字段是否有空字符串: {(df['涨跌幅'] == '').sum()}")
        print(f"涨跌幅字段是否有'-': {(df['涨跌幅'] == '-').sum()}")
        
        # 显示涨跌幅字段的唯一值
        print(f"\n涨跌幅字段唯一值 (前20个):")
        unique_values = df['涨跌幅'].unique()
        print(unique_values[:20])
        
        # 检查具体的数据样例
        print("\n=== 具体数据样例 ===")
        sample_data = df[['代码', '名称', '最新价', '涨跌额', '涨跌幅']].head(10)
        for _, row in sample_data.iterrows():
            print(f"代码: {row['代码']}, 名称: {row['名称']}, 涨跌幅: '{row['涨跌幅']}' (类型: {type(row['涨跌幅'])})")
        
        # 检查是否有正常的涨跌幅数据
        non_null_pct = df[df['涨跌幅'].notna() & (df['涨跌幅'] != '') & (df['涨跌幅'] != '-')]
        print(f"\n非null且非空的涨跌幅数据: {len(non_null_pct)} 条")
        if len(non_null_pct) > 0:
            print("前5条正常涨跌幅数据:")
            print(non_null_pct[['代码', '名称', '涨跌幅']].head())
        
        return df
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    df = test_akshare_indices()
    if df is not None:
        print(f"\n测试完成，总共获取到 {len(df)} 条指数数据")
