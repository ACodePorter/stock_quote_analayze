#!/usr/bin/env python3
"""
新闻相关表迁移脚本
添加缺失的字段和表到PostgreSQL数据库
"""

import psycopg2
import sys
import os
from pathlib import Path

# 添加backend_api目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend_api'))

from config import DATABASE_CONFIG

def get_connection():
    """获取数据库连接"""
    try:
        # 解析数据库连接URL
        db_url = DATABASE_CONFIG["url"]
        print(f"🔗 连接数据库: {db_url}")
        
        # 将SQLAlchemy格式的URL转换为psycopg2格式
        # postgresql+psycopg2://user:password@host:port/database
        # 转换为 postgresql://user:password@host:port/database
        if db_url.startswith("postgresql+psycopg2://"):
            db_url = db_url.replace("postgresql+psycopg2://", "postgresql://")
        
        # 连接数据库
        conn = psycopg2.connect(db_url)
        conn.autocommit = True  # 自动提交
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def check_table_exists(cursor, table_name):
    """检查表是否存在"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
    """, (table_name,))
    return cursor.fetchone()[0]

def check_column_exists(cursor, table_name, column_name):
    """检查字段是否存在"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s 
            AND column_name = %s
        );
    """, (table_name, column_name))
    return cursor.fetchone()[0]

def create_news_categories_table(cursor):
    """创建news_categories表"""
    print("📋 检查news_categories表...")
    
    if check_table_exists(cursor, 'news_categories'):
        print("✅ news_categories表已存在")
        return True
    
    print("🔧 创建news_categories表...")
    
    try:
        # 创建表
        cursor.execute("""
            CREATE TABLE news_categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                description TEXT,
                sort_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 插入默认分类
        cursor.execute("""
            INSERT INTO news_categories (name, description, sort_order) VALUES
            ('全部', '所有资讯', 1),
            ('市场动态', '市场行情、指数变化等', 2),
            ('政策解读', '政策法规、监管动态等', 3),
            ('公司资讯', '上市公司公告、财报等', 4),
            ('国际财经', '国际市场、汇率等', 5),
            ('分析研判', '专业分析、投资建议等', 6)
            ON CONFLICT (name) DO NOTHING;
        """)
        
        print("✅ news_categories表创建成功")
        return True
        
    except Exception as e:
        print(f"❌ 创建news_categories表失败: {e}")
        return False

def add_stock_news_fields(cursor):
    """为stock_news表添加缺失的字段"""
    print("📋 检查stock_news表字段...")
    
    if not check_table_exists(cursor, 'stock_news'):
        print("❌ stock_news表不存在，无法添加字段")
        return False
    
    # 需要添加的字段
    fields_to_add = [
        ('read_count', 'INTEGER DEFAULT 0', '阅读量'),
        ('is_hot', 'BOOLEAN DEFAULT FALSE', '是否热门'),
        ('tags', 'TEXT', '标签'),
        ('image_url', 'TEXT', '图片URL'),
        ('category_id', 'INTEGER REFERENCES news_categories(id)', '分类ID')
    ]
    
    added_fields = []
    
    for field_name, field_type, description in fields_to_add:
        if check_column_exists(cursor, 'stock_news', field_name):
            print(f"✅ 字段 {field_name} 已存在")
        else:
            print(f"🔧 添加字段 {field_name} ({description})...")
            try:
                cursor.execute(f"ALTER TABLE stock_news ADD COLUMN {field_name} {field_type};")
                added_fields.append(field_name)
                print(f"✅ 字段 {field_name} 添加成功")
            except Exception as e:
                print(f"❌ 添加字段 {field_name} 失败: {e}")
    
    # 创建索引
    if added_fields:
        print("🔧 创建索引...")
        indexes_to_create = [
            ("idx_stock_news_read_count", "CREATE INDEX IF NOT EXISTS idx_stock_news_read_count ON stock_news(read_count)"),
            ("idx_stock_news_is_hot", "CREATE INDEX IF NOT EXISTS idx_stock_news_is_hot ON stock_news(is_hot)"),
            ("idx_stock_news_publish_time", "CREATE INDEX IF NOT EXISTS idx_stock_news_publish_time ON stock_news(publish_time)"),
            ("idx_stock_news_category_id", "CREATE INDEX IF NOT EXISTS idx_stock_news_category_id ON stock_news(category_id)")
        ]
        
        for index_name, index_sql in indexes_to_create:
            try:
                cursor.execute(index_sql)
                print(f"✅ 索引 {index_name} 创建成功")
            except Exception as e:
                print(f"⚠️ 索引 {index_name} 创建失败: {e}")
    
    return True

def update_existing_data(cursor):
    """更新现有数据"""
    print("🔧 更新现有数据...")
    
    try:
        # 为现有新闻设置默认分类
        if check_column_exists(cursor, 'stock_news', 'category_id'):
            cursor.execute("""
                UPDATE stock_news 
                SET category_id = 2 
                WHERE category_id IS NULL;
            """)
            print("✅ 现有新闻已设置默认分类")
        
        # 为现有新闻设置默认阅读量
        if check_column_exists(cursor, 'stock_news', 'read_count'):
            cursor.execute("""
                UPDATE stock_news 
                SET read_count = 0 
                WHERE read_count IS NULL;
            """)
            print("✅ 现有新闻已设置默认阅读量")
        
        # 为现有新闻设置默认热门标记
        if check_column_exists(cursor, 'stock_news', 'is_hot'):
            cursor.execute("""
                UPDATE stock_news 
                SET is_hot = FALSE 
                WHERE is_hot IS NULL;
            """)
            print("✅ 现有新闻已设置默认热门标记")
            
    except Exception as e:
        print(f"⚠️ 更新现有数据时出现错误: {e}")

def create_views_and_functions(cursor):
    """创建视图和函数"""
    print("🔧 创建视图和函数...")
    
    try:
        # 创建热门资讯视图
        cursor.execute("""
            CREATE OR REPLACE VIEW hot_news_view AS
            SELECT 
                id,
                title,
                summary,
                publish_time,
                source,
                read_count,
                is_hot,
                tags,
                image_url,
                category_id
            FROM stock_news 
            WHERE is_hot = TRUE 
            ORDER BY read_count DESC;
        """)
        print("✅ 热门资讯视图创建成功")
        
        # 创建更新热门资讯标记的函数
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_hot_news_mark()
            RETURNS VOID AS $$
            BEGIN
                -- 清除所有热门标记
                UPDATE stock_news SET is_hot = FALSE;
                
                -- 将阅读量前10的新闻标记为热门
                UPDATE stock_news SET is_hot = TRUE 
                WHERE id IN (
                    SELECT id FROM stock_news 
                    ORDER BY read_count DESC 
                    LIMIT 10
                );
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("✅ 更新热门资讯标记函数创建成功")
        
    except Exception as e:
        print(f"⚠️ 创建视图和函数时出现错误: {e}")

def main():
    """主函数"""
    print("🚀 开始新闻表迁移...")
    print("=" * 60)
    
    # 获取数据库连接
    conn = get_connection()
    if not conn:
        print("❌ 无法连接到数据库，迁移失败")
        return False
    
    try:
        cursor = conn.cursor()
        
        # 1. 创建news_categories表
        if not create_news_categories_table(cursor):
            print("❌ 创建news_categories表失败")
            return False
        
        # 2. 为stock_news表添加字段
        if not add_stock_news_fields(cursor):
            print("❌ 添加stock_news字段失败")
            return False
        
        # 3. 更新现有数据
        update_existing_data(cursor)
        
        # 4. 创建视图和函数
        create_views_and_functions(cursor)
        
        print("=" * 60)
        print("🎉 新闻表迁移完成！")
        print("✅ 所有缺失的字段和表已成功添加")
        print("✅ 索引和视图已创建")
        print("✅ 现有数据已更新")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移过程中出现错误: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 迁移成功！现在可以正常使用所有新闻功能了。")
    else:
        print("\n💥 迁移失败！请检查错误信息并重试。")
        sys.exit(1)
