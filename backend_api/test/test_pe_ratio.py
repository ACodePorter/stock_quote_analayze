#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试市盈率数据获取
"""

import akshare as ak
import pandas as pd
import json

def test_stock_bid_ask_em():
    """测试akshare的stock_bid_ask_em接口，查看返回的市盈率字段"""
    
    # 测试几个不同的股票代码
    test_codes = ['000001', '600036', '603667', '300750']
    
    for code in test_codes:
        print(f"\n{'='*50}")
        print(f"测试股票代码: {code}")
        print(f"{'='*50}")
        
        try:
            # 调用akshare接口
            df = ak.stock_bid_ask_em(symbol=code)
            
            if df.empty:
                print(f"股票 {code} 未找到数据")
                continue
                
            print(f"原始数据列名: {list(df.columns)}")
            print(f"数据行数: {len(df)}")
            
            # 转换为字典格式
            data_dict = dict(zip(df['item'], df['value']))
            
            print(f"\n所有字段:")
            for key, value in data_dict.items():
                print(f"  {key}: {value}")
            
            # 特别关注市盈率相关字段
            pe_fields = [key for key in data_dict.keys() if '市盈率' in key or 'PE' in key.upper()]
            if pe_fields:
                print(f"\n市盈率相关字段:")
                for field in pe_fields:
                    print(f"  {field}: {data_dict[field]}")
            else:
                print(f"\n未找到市盈率相关字段")
                
            # 检查是否有其他可能包含市盈率信息的字段
            print(f"\n可能包含财务信息的字段:")
            for key, value in data_dict.items():
                if any(keyword in key for keyword in ['财务', '估值', '比率', '指标']):
                    print(f"  {key}: {value}")
                    
        except Exception as e:
            print(f"获取股票 {code} 数据时出错: {e}")
            import traceback
            traceback.print_exc()

def test_stock_zh_a_spot_em():
    """测试akshare的stock_zh_a_spot_em接口，查看是否有市盈率字段"""
    
    print(f"\n{'='*50}")
    print("测试 stock_zh_a_spot_em 接口")
    print(f"{'='*50}")
    
    try:
        # 调用akshare接口获取A股实时行情
        df = ak.stock_zh_a_spot_em()
        
        if df.empty:
            print("未获取到A股实时行情数据")
            return
            
        print(f"数据列名: {list(df.columns)}")
        print(f"数据列数: {len(df.columns)}")
        print(f"数据行数: {len(df)}")
        
        # 查看前几行数据
        print(f"\n前3行数据:")
        print(df.head(3))
        
        # 检查是否有市盈率相关列
        pe_columns = [col for col in df.columns if '市盈率' in col or 'PE' in col.upper()]
        if pe_columns:
            print(f"\n市盈率相关列: {pe_columns}")
            # 显示前几行的市盈率数据
            for col in pe_columns:
                print(f"\n{col} 列的前5个值:")
                print(df[col].head())
        else:
            print(f"\n未找到市盈率相关列")
            
    except Exception as e:
        print(f"获取A股实时行情数据时出错: {e}")
        import traceback
        traceback.print_exc()

def test_stock_a_pe():
    """测试akshare的stock_a_pe接口，专门获取市盈率数据"""
    
    print(f"\n{'='*50}")
    print("测试 stock_a_pe 接口")
    print(f"{'='*50}")
    
    try:
        # 调用akshare接口获取A股市盈率数据
        df = ak.stock_a_pe(symbol="000001")
        
        if df.empty:
            print("未获取到市盈率数据")
            return
            
        print(f"数据列名: {list(df.columns)}")
        print(f"数据行数: {len(df)}")
        
        print(f"\n市盈率数据:")
        print(df)
        
    except Exception as e:
        print(f"获取市盈率数据时出错: {e}")
        import traceback
        traceback.print_exc()

def test_stock_a_pb():
    """测试akshare的stock_a_pb接口，查看是否有相关估值数据"""
    
    print(f"\n{'='*50}")
    print("测试 stock_a_pb 接口")
    print(f"{'='*50}")
    
    try:
        # 调用akshare接口获取A股市净率数据
        df = ak.stock_a_pb(symbol="000001")
        
        if df.empty:
            print("未获取到市净率数据")
            return
            
        print(f"数据列名: {list(df.columns)}")
        print(f"数据行数: {len(df)}")
        
        print(f"\n市净率数据:")
        print(df)
        
    except Exception as e:
        print(f"获取市净率数据时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始测试市盈率数据获取...")
    
    # 测试主要接口
    test_stock_bid_ask_em()
    
    # 测试其他可能包含市盈率的接口
    test_stock_zh_a_spot_em()
    test_stock_a_pe()
    test_stock_a_pb()
    
    print("\n测试完成!")
