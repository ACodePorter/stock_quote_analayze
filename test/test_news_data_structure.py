#!/usr/bin/env python3
"""
测试新闻数据结构
"""

import akshare as ak
import pandas as pd

def test_news_data_structure():
    """测试akshare返回的新闻数据结构"""
    print("🧪 测试akshare新闻数据结构...")
    
    try:
        # 获取新闻数据
        news_df = ak.stock_news_main_cx()
        
        if news_df is None or news_df.empty:
            print("❌ akshare返回空数据")
            return
        
        print(f"✅ akshare返回 {len(news_df)} 条数据")
        print(f"📊 数据形状: {news_df.shape}")
        
        # 显示列名
        print(f"📋 列名: {list(news_df.columns)}")
        
        # 显示前几行数据
        print("\n📄 前3行数据:")
        for i, (_, row) in enumerate(news_df.head(3).iterrows()):
            print(f"\n第 {i+1} 行:")
            for col in news_df.columns:
                value = row.get(col, '')
                print(f"  {col}: {value} (类型: {type(value)})")
        
        # 检查关键字段
        print("\n🔍 检查关键字段:")
        for col in ['新闻标题', '标题', '新闻内容', '内容', '发布时间', '时间']:
            if col in news_df.columns:
                non_null_count = news_df[col].notna().sum()
                print(f"  {col}: {non_null_count}/{len(news_df)} 条非空")
                
                # 显示一些示例值
                sample_values = news_df[col].dropna().head(3).tolist()
                print(f"    示例值: {sample_values}")
            else:
                print(f"  {col}: 列不存在")
        
        # 检查数据过滤条件
        print("\n🔍 检查数据过滤条件:")
        title_cols = ['新闻标题', '标题']
        content_cols = ['新闻内容', '内容']
        
        valid_count = 0
        for _, row in news_df.iterrows():
            title = None
            content = None
            
            # 获取标题
            for col in title_cols:
                if col in news_df.columns:
                    val = row.get(col, '')
                    if val and str(val).strip():
                        title = str(val).strip()
                        break
            
            # 获取内容
            for col in content_cols:
                if col in news_df.columns:
                    val = row.get(col, '')
                    if val and str(val).strip():
                        content = str(val).strip()
                        break
            
            if title and content:
                valid_count += 1
        
        print(f"  有效数据条数: {valid_count}/{len(news_df)}")
        print(f"  过滤率: {(len(news_df) - valid_count) / len(news_df) * 100:.1f}%")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_news_data_structure()
