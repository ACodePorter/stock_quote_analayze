#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AKShare行业板块接口，检查返回的数据结构
"""

import akshare as ak
import pandas as pd
from datetime import datetime

def test_akshare_industry_board():
    """测试AKShare行业板块接口"""
    
    print("🧪 测试AKShare行业板块接口")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    try:
        # 调用AKShare接口
        print("📡 调用 ak.stock_board_industry_name_em()...")
        df = ak.stock_board_industry_name_em()
        
        print(f"✅ 成功获取数据，共 {len(df)} 条记录")
        print(f"📊 数据形状: {df.shape}")
        
        # 显示列名
        print(f"\n📋 列名信息:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1:2d}. {col}")
        
        # 显示前几行数据
        print(f"\n📊 前3行数据:")
        print(df.head(3).to_string())
        
        # 检查关键字段是否存在
        print(f"\n🔍 关键字段检查:")
        key_fields = ["领涨股", "领涨股涨跌幅", "领涨股代码"]
        for field in key_fields:
            if field in df.columns:
                print(f"  ✅ {field}: 存在")
                # 检查是否有非空值
                non_null_count = df[field].notna().sum()
                total_count = len(df)
                print(f"      非空值: {non_null_count}/{total_count} ({non_null_count/total_count*100:.1f}%)")
                
                # 显示前几个非空值
                non_null_values = df[df[field].notna()][field].head(3)
                if len(non_null_values) > 0:
                    print(f"      示例值: {non_null_values.tolist()}")
                else:
                    print(f"      所有值都为空")
            else:
                print(f"  ❌ {field}: 不存在")
        
        # 检查数据类型
        print(f"\n🔍 数据类型检查:")
        for col in df.columns:
            dtype = df[col].dtype
            print(f"  {col}: {dtype}")
        
        # 检查是否有空值
        print(f"\n🔍 空值检查:")
        for col in df.columns:
            null_count = df[col].isna().sum()
            total_count = len(df)
            if null_count > 0:
                print(f"  {col}: {null_count}/{total_count} ({null_count/total_count*100:.1f}%) 为空")
        
        # 尝试获取一个具体的板块数据
        print(f"\n🔍 具体板块数据示例:")
        if len(df) > 0:
            first_row = df.iloc[0]
            print(f"  第一个板块: {first_row['板块名称']} ({first_row['板块代码']})")
            print(f"    涨跌幅: {first_row['涨跌幅']}%")
            print(f"    领涨股: {first_row.get('领涨股', 'N/A')}")
            print(f"    领涨股涨跌幅: {first_row.get('领涨股涨跌幅', 'N/A')}%")
            print(f"    领涨股代码: {first_row.get('领涨股代码', 'N/A')}")
        
        print("-" * 80)
        print("🏁 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        tb = traceback.format_exc()
        print(f"错误详情:\n{tb}")

if __name__ == "__main__":
    test_akshare_industry_board()
