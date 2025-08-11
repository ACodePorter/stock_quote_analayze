#!/usr/bin/env python3
"""
修复stock_news表id字段问题的脚本
解决PostgreSQL中SERIAL字段的NOT NULL约束问题
"""

import psycopg2
import sys
import traceback
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': '192.168.16.4',
    'port': 5432,
    'database': 'stock_analysis',
    'user': 'postgres',
    'password': 'qidianspacetime$91'
}

def test_connection():
    """测试数据库连接"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ 数据库连接成功")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def check_table_structure():
    """检查stock_news表结构"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'stock_news'
            );
        """)
        
        if not cursor.fetchone()[0]:
            print("❌ stock_news表不存在")
            return False
        
        # 检查表结构
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'stock_news'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("📋 stock_news表结构:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} (nullable: {col[1] == 'YES'}, default: {col[3]})")
        
        # 检查id字段的序列
        cursor.execute("""
            SELECT pg_get_serial_sequence('stock_news', 'id');
        """)
        
        sequence = cursor.fetchone()
        if sequence and sequence[0]:
            print(f"✅ id字段序列: {sequence[0]}")
        else:
            print("❌ id字段没有关联的序列")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查表结构失败: {e}")
        traceback.print_exc()
        return False

def fix_id_sequence():
    """修复id字段的序列"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔧 开始修复id字段序列...")
        
        # 1. 检查当前序列值
        cursor.execute("""
            SELECT last_value, is_called 
            FROM stock_news_id_seq;
        """)
        
        current_seq = cursor.fetchone()
        if current_seq:
            print(f"当前序列值: {current_seq[0]}, 已调用: {current_seq[1]}")
        
        # 2. 获取表中最大的id值
        cursor.execute("""
            SELECT COALESCE(MAX(id), 0) FROM stock_news;
        """)
        
        max_id = cursor.fetchone()[0]
        print(f"表中最大id值: {max_id}")
        
        # 3. 重置序列到正确的值
        if max_id > 0:
            cursor.execute(f"""
                SELECT setval('stock_news_id_seq', {max_id}, true);
            """)
            print(f"✅ 序列已重置到 {max_id}")
        else:
            cursor.execute("""
                SELECT setval('stock_news_id_seq', 1, false);
            """)
            print("✅ 序列已重置到 1")
        
        # 4. 验证序列修复
        cursor.execute("""
            SELECT nextval('stock_news_id_seq');
        """)
        
        next_val = cursor.fetchone()[0]
        print(f"下一个序列值: {next_val}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ id字段序列修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复序列失败: {e}")
        traceback.print_exc()
        return False

def test_insert():
    """测试插入功能"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🧪 测试插入功能...")
        
        # 测试插入一条数据
        test_data = {
            'stock_code': 'TEST001',
            'title': '测试新闻标题',
            'content': '测试新闻内容',
            'keywords': '测试',
            'publish_time': datetime.now(),
            'source': '测试来源',
            'url': 'http://test.com',
            'summary': '测试摘要',
            'type': 'test',
            'rating': '',
            'target_price': '',
            'created_at': datetime.now()
        }
        
        cursor.execute("""
            INSERT INTO stock_news 
            (stock_code, title, content, keywords, publish_time, source, url, summary, type, rating, target_price, created_at)
            VALUES (%(stock_code)s, %(title)s, %(content)s, %(keywords)s, %(publish_time)s, %(source)s, %(url)s, %(summary)s, %(type)s, %(rating)s, %(target_price)s, %(created_at)s)
            RETURNING id;
        """, test_data)
        
        new_id = cursor.fetchone()[0]
        print(f"✅ 测试插入成功，新记录id: {new_id}")
        
        # 清理测试数据
        cursor.execute("DELETE FROM stock_news WHERE stock_code = 'TEST001'")
        print("🧹 测试数据已清理")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 测试插入失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始修复stock_news表id字段问题...")
    print("=" * 50)
    
    # 1. 测试连接
    if not test_connection():
        return False
    
    print()
    
    # 2. 检查表结构
    if not check_table_structure():
        return False
    
    print()
    
    # 3. 修复序列
    if not fix_id_sequence():
        return False
    
    print()
    
    # 4. 测试插入
    if not test_insert():
        return False
    
    print()
    print("🎉 所有修复完成！stock_news表现在应该可以正常工作了。")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 程序异常: {e}")
        traceback.print_exc()
        sys.exit(1)
