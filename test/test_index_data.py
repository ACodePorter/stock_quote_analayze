#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试指数数据收集和查询
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend_core.data_collectors.akshare.realtime_index_spot_ak import RealtimeIndexSpotAkCollector
from backend_core.database.db import SessionLocal
from backend_api.models import IndexRealtimeQuotes
from sqlalchemy import text

def test_collect_index_data():
    """测试收集指数数据"""
    print("=" * 50)
    print("开始测试指数数据收集...")
    print("=" * 50)
    
    collector = RealtimeIndexSpotAkCollector()
    try:
        df = collector.collect_quotes()
        if df is not None and not df.empty:
            print(f"\n成功收集到 {len(df)} 条指数数据")
            print("\n前10条数据预览:")
            print(df[['代码', '名称', '最新价', '涨跌幅']].head(10))
            
            # 检查是否有深证成指和创业板指
            print("\n检查目标指数:")
            target_indices = ['深证成指', '深圳成指', '创业板指']
            for name in target_indices:
                matching = df[df['名称'].str.contains(name, na=False)]
                if not matching.empty:
                    print(f"  ✓ 找到 {name}:")
                    for _, row in matching.iterrows():
                        print(f"    代码: {row['代码']}, 名称: {row['名称']}, 最新价: {row['最新价']}")
                else:
                    print(f"  ✗ 未找到 {name}")
        else:
            print("收集到的数据为空")
    except Exception as e:
        print(f"收集数据时出错: {e}")
        import traceback
        traceback.print_exc()

def test_query_index_data():
    """测试查询数据库中的指数数据"""
    print("\n" + "=" * 50)
    print("开始测试数据库查询...")
    print("=" * 50)
    
    session = SessionLocal()
    try:
        # 查询所有指数数据
        all_indices = session.query(IndexRealtimeQuotes).all()
        print(f"\n数据库中总共有 {len(all_indices)} 条指数数据")
        
        if len(all_indices) > 0:
            print("\n前10条数据:")
            for idx, row in enumerate(all_indices[:10], 1):
                print(f"  {idx}. 代码: {row.code}, 名称: {row.name}, 价格: {row.price}, 更新时间: {row.update_time}")
        
        # 查询目标指数
        print("\n查询目标指数:")
        target_codes = ['399001', '399006', '000001', '000300']
        target_names = ['深证成指', '深圳成指', '创业板指']
        
        for code in target_codes:
            rows = session.query(IndexRealtimeQuotes).filter(
                IndexRealtimeQuotes.code == code
            ).all()
            if rows:
                print(f"  ✓ 代码 {code} 找到 {len(rows)} 条记录:")
                for row in rows:
                    print(f"    名称: {row.name}, 价格: {row.price}, 更新时间: {row.update_time}")
            else:
                # 尝试带前缀的代码
                if code.startswith('399'):
                    prefix_code = f'sz{code}'
                elif code.startswith('000'):
                    prefix_code = f'sh{code}'
                else:
                    prefix_code = code
                
                rows = session.query(IndexRealtimeQuotes).filter(
                    IndexRealtimeQuotes.code == prefix_code
                ).all()
                if rows:
                    print(f"  ✓ 代码 {prefix_code} 找到 {len(rows)} 条记录:")
                    for row in rows:
                        print(f"    名称: {row.name}, 价格: {row.price}, 更新时间: {row.update_time}")
                else:
                    print(f"  ✗ 代码 {code} 和 {prefix_code} 都未找到")
        
        for name in target_names:
            rows = session.query(IndexRealtimeQuotes).filter(
                IndexRealtimeQuotes.name == name
            ).all()
            if rows:
                print(f"  ✓ 名称 '{name}' 找到 {len(rows)} 条记录:")
                for row in rows:
                    print(f"    代码: {row.code}, 价格: {row.price}, 更新时间: {row.update_time}")
            else:
                print(f"  ✗ 名称 '{name}' 未找到")
        
        # 使用模糊查询
        print("\n使用模糊查询:")
        for name in target_names:
            rows = session.query(IndexRealtimeQuotes).filter(
                IndexRealtimeQuotes.name.like(f'%{name}%')
            ).all()
            if rows:
                print(f"  ✓ 名称包含 '{name}' 找到 {len(rows)} 条记录:")
                for row in rows:
                    print(f"    代码: {row.code}, 名称: {row.name}, 价格: {row.price}")
            else:
                print(f"  ✗ 名称包含 '{name}' 未找到")
                
    except Exception as e:
        print(f"查询数据库时出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    # 先收集数据
    test_collect_index_data()
    
    # 再查询数据
    test_query_index_data()

