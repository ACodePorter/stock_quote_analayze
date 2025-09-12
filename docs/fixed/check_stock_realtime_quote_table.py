#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 stock_realtime_quote 表结构和约束
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend_core.database.db import SessionLocal, engine
from sqlalchemy import text, inspect
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_stock_realtime_quote_table():
    """检查stock_realtime_quote表结构"""
    logger.info("🔍 检查stock_realtime_quote表结构...")
    
    session = SessionLocal()
    try:
        # 检查表是否存在
        result = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'stock_realtime_quote'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            logger.warning("⚠️  stock_realtime_quote表不存在！")
            return False
        
        # 检查表结构
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'stock_realtime_quote' 
            ORDER BY ordinal_position;
        """))
        
        columns = result.fetchall()
        logger.info("📋 stock_realtime_quote表结构:")
        for col in columns:
            logger.info(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # 检查约束
        result = session.execute(text("""
            SELECT conname, contype, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = 'stock_realtime_quote'::regclass;
        """))
        
        constraints = result.fetchall()
        logger.info("🔒 stock_realtime_quote表约束:")
        for constraint in constraints:
            logger.info(f"  - {constraint[0]}: {constraint[1]} - {constraint[2]}")
        
        # 检查是否有主键约束
        has_primary_key = any(c[1] == 'p' for c in constraints)
        logger.info(f"🔑 是否有主键约束: {has_primary_key}")
        
        # 检查是否有外键约束
        has_foreign_key = any(c[1] == 'f' for c in constraints)
        logger.info(f"🔗 是否有外键约束: {has_foreign_key}")
        
        # 检查索引
        result = session.execute(text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'stock_realtime_quote';
        """))
        
        indexes = result.fetchall()
        logger.info("📊 stock_realtime_quote表索引:")
        for index in indexes:
            logger.info(f"  - {index[0]}: {index[1]}")
        
        return has_primary_key, has_foreign_key
        
    except Exception as e:
        logger.error(f"❌ 检查表结构失败: {e}")
        return False, False
    finally:
        session.close()

def check_stock_basic_info_table():
    """检查stock_basic_info表结构（用于外键引用）"""
    logger.info("🔍 检查stock_basic_info表结构（外键引用）...")
    
    session = SessionLocal()
    try:
        # 检查表是否存在
        result = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'stock_basic_info'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            logger.warning("⚠️  stock_basic_info表不存在！")
            return False
        
        # 检查约束
        result = session.execute(text("""
            SELECT conname, contype, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = 'stock_basic_info'::regclass;
        """))
        
        constraints = result.fetchall()
        logger.info("🔒 stock_basic_info表约束:")
        for constraint in constraints:
            logger.info(f"  - {constraint[0]}: {constraint[1]} - {constraint[2]}")
        
        # 检查是否有主键约束
        has_primary_key = any(c[1] == 'p' for c in constraints)
        logger.info(f"🔑 stock_basic_info是否有主键约束: {has_primary_key}")
        
        return has_primary_key
        
    except Exception as e:
        logger.error(f"❌ 检查stock_basic_info表结构失败: {e}")
        return False
    finally:
        session.close()

def main():
    """主函数"""
    logger.info("🚀 开始检查stock_realtime_quote表...")
    
    # 检查stock_realtime_quote表
    has_pk, has_fk = check_stock_realtime_quote_table()
    
    # 检查stock_basic_info表
    basic_info_has_pk = check_stock_basic_info_table()
    
    # 总结
    logger.info("""
📊 检查结果总结:

stock_realtime_quote表:
- 主键约束: {}
- 外键约束: {}

stock_basic_info表:
- 主键约束: {}

🔧 建议:
1. 如果缺少主键约束，需要添加: ALTER TABLE stock_realtime_quote ADD CONSTRAINT stock_realtime_quote_pkey PRIMARY KEY (code);
2. 如果缺少外键约束，需要添加: ALTER TABLE stock_realtime_quote ADD CONSTRAINT fk_stock_realtime_quote_code FOREIGN KEY (code) REFERENCES stock_basic_info(code);
3. 建议创建索引: CREATE INDEX IF NOT EXISTS idx_stock_realtime_quote_update_time ON stock_realtime_quote(update_time);
    """.format(has_pk, has_fk, basic_info_has_pk))
    
    logger.info("✅ 检查完成")

if __name__ == "__main__":
    main() 