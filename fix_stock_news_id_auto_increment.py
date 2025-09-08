#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复stock_news表id字段自增问题
"""

from backend_core.database.db import engine
from sqlalchemy import text

def fix_stock_news_id_auto_increment():
    """修复stock_news表id字段自增问题"""
    print("🔧 修复stock_news表id字段自增问题...")
    
    try:
        with engine.connect() as conn:
            # 开始事务
            trans = conn.begin()
            
            try:
                # 1. 创建序列
                print("1. 创建序列...")
                conn.execute(text('''
                    CREATE SEQUENCE IF NOT EXISTS stock_news_id_seq
                    START WITH 1
                    INCREMENT BY 1
                    NO MINVALUE
                    NO MAXVALUE
                    CACHE 1
                '''))
                
                # 2. 设置序列的当前值为表中最大id+1
                print("2. 设置序列当前值...")
                result = conn.execute(text('SELECT MAX(id) FROM stock_news'))
                max_id = result.fetchone()[0]
                if max_id:
                    conn.execute(text(f'SELECT setval(\'stock_news_id_seq\', {max_id + 1})'))
                    print(f"   序列当前值设置为: {max_id + 1}")
                else:
                    conn.execute(text('SELECT setval(\'stock_news_id_seq\', 1)'))
                    print("   序列当前值设置为: 1")
                
                # 3. 修改id字段默认值为序列的nextval
                print("3. 修改id字段默认值...")
                conn.execute(text('''
                    ALTER TABLE stock_news 
                    ALTER COLUMN id SET DEFAULT nextval('stock_news_id_seq')
                '''))
                
                # 4. 将序列的所有权转移给id字段
                print("4. 设置序列所有权...")
                conn.execute(text('''
                    ALTER SEQUENCE stock_news_id_seq OWNED BY stock_news.id
                '''))
                
                # 提交事务
                trans.commit()
                print("✅ stock_news表id字段自增修复完成!")
                
                # 验证修复结果
                print("\n🧪 验证修复结果...")
                result = conn.execute(text('''
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'stock_news' AND column_name = 'id'
                '''))
                
                row = result.fetchone()
                if row:
                    print(f"id字段信息:")
                    print(f"  字段名: {row[0]}")
                    print(f"  数据类型: {row[1]}")
                    print(f"  可空: {row[2]}")
                    print(f"  默认值: {row[3]}")
                    
                    if 'nextval' in str(row[3]):
                        print("✅ id字段默认值已正确设置为自增")
                    else:
                        print("❌ id字段默认值设置可能有问题")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ 修复失败，已回滚: {e}")
                raise
                
    except Exception as e:
        print(f"❌ 修复stock_news表id字段失败: {e}")

def test_insert_without_id():
    """测试不提供id的插入"""
    print("\n🧪 测试不提供id的插入...")
    
    try:
        with engine.connect() as conn:
            # 测试插入一条记录（不提供id）
            result = conn.execute(text('''
                INSERT INTO stock_news 
                (title, content, publish_time, source, url, category_id, 
                 summary, tags, read_count, is_hot, stock_code, image_url)
                VALUES (:title, :content, :publish_time, :source, :url, :category_id,
                        :summary, :tags, :read_count, :is_hot, :stock_code, :image_url)
                RETURNING id
            '''), {
                'title': '测试新闻标题',
                'content': '测试新闻内容',
                'publish_time': '2025-09-08 20:30:00',
                'source': '测试来源',
                'url': 'http://test.com',
                'category_id': 1,
                'summary': '测试摘要',
                'tags': ['测试'],
                'read_count': 0,
                'is_hot': False,
                'stock_code': '000001',
                'image_url': ''
            })
            
            new_id = result.fetchone()[0]
            print(f"✅ 测试插入成功，新记录id: {new_id}")
            
            # 清理测试数据
            conn.execute(text('DELETE FROM stock_news WHERE id = :id'), {'id': new_id})
            print("✅ 测试数据已清理")
            
    except Exception as e:
        print(f"❌ 测试插入失败: {e}")

if __name__ == "__main__":
    fix_stock_news_id_auto_increment()
    test_insert_without_id()
