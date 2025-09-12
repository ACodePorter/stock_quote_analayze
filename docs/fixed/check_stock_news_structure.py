#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查stock_news表结构
"""

from backend_core.database.db import engine
from sqlalchemy import text

def check_stock_news_structure():
    """检查stock_news表结构"""
    print("🔍 检查stock_news表结构...")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text('''
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'stock_news' 
                ORDER BY ordinal_position
            '''))
            
            print('\nstock_news表结构:')
            print('=' * 80)
            print(f'{"字段名":<20} {"数据类型":<20} {"可空":<10} {"默认值":<20}')
            print('-' * 80)
            
            for row in result:
                column_name = row[0]
                data_type = row[1]
                is_nullable = row[2]
                column_default = row[3] or "无默认值"
                
                print(f'{column_name:<20} {data_type:<20} {is_nullable:<10} {column_default:<20}')
                
                # 特别关注id字段
                if column_name == 'id':
                    print(f'  ⚠️  id字段类型: {data_type}, 可空: {is_nullable}, 默认值: {column_default}')
            
            print('=' * 80)
            
    except Exception as e:
        print(f'❌ 检查表结构失败: {e}')

def check_id_sequence():
    """检查id字段的序列"""
    print("\n🔍 检查id字段序列...")
    
    try:
        with engine.connect() as conn:
            # 检查是否有序列
            result = conn.execute(text('''
                SELECT sequence_name, data_type, start_value, minimum_value, maximum_value, increment
                FROM information_schema.sequences 
                WHERE sequence_name LIKE '%stock_news%'
            '''))
            
            sequences = result.fetchall()
            if sequences:
                print("找到相关序列:")
                for seq in sequences:
                    print(f"  序列名: {seq[0]}")
                    print(f"  数据类型: {seq[1]}")
                    print(f"  起始值: {seq[2]}")
                    print(f"  最小值: {seq[3]}")
                    print(f"  最大值: {seq[4]}")
                    print(f"  增量: {seq[5]}")
            else:
                print("❌ 未找到相关序列")
                
            # 检查当前id值
            result = conn.execute(text('SELECT MAX(id) FROM stock_news'))
            max_id = result.fetchone()[0]
            print(f"\n当前最大id值: {max_id}")
            
    except Exception as e:
        print(f'❌ 检查序列失败: {e}')

if __name__ == "__main__":
    check_stock_news_structure()
    check_id_sequence()
