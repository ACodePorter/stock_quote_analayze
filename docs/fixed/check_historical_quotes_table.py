#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 historical_quotes 表结构和约束
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

def check_historical_quotes_table():
    """检查historical_quotes表结构"""
    logger.info("🔍 检查historical_quotes表结构...")
    
    session = SessionLocal()
    try:
        # 检查表是否存在
        result = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'historical_quotes'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            logger.warning("⚠️  historical_quotes表不存在！")
            return False
        
        # 检查表结构
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'historical_quotes' 
            ORDER BY ordinal_position;
        """))
        
        columns = result.fetchall()
        logger.info("📋 historical_quotes表结构:")
        for col in columns:
            logger.info(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # 检查约束
        result = session.execute(text("""
            SELECT conname, contype, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = 'historical_quotes'::regclass;
        """))
        
        constraints = result.fetchall()
        logger.info("🔒 historical_quotes表约束:")
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
            WHERE tablename = 'historical_quotes';
        """))
        
        indexes = result.fetchall()
        logger.info("📊 historical_quotes表索引:")
        for index in indexes:
            logger.info(f"  - {index[0]}: {index[1]}")
        
        # 检查数据量
        result = session.execute(text("SELECT COUNT(*) FROM historical_quotes"))
        row_count = result.scalar()
        logger.info(f"📊 表数据量: {row_count} 行")
        
        # 检查重复数据
        result = session.execute(text("""
            SELECT code, date, COUNT(*) as count
            FROM historical_quotes 
            GROUP BY code, date 
            HAVING COUNT(*) > 1
            LIMIT 10
        """))
        
        duplicates = result.fetchall()
        if duplicates:
            logger.warning(f"⚠️  发现 {len(duplicates)} 组重复数据:")
            for dup in duplicates:
                logger.warning(f"  - code: {dup[0]}, date: {dup[1]}, count: {dup[2]}")
        else:
            logger.info("✅ 未发现重复数据")
        
        return has_primary_key, has_foreign_key
        
    except Exception as e:
        logger.error(f"❌ 检查表结构失败: {e}")
        return False, False
    finally:
        session.close()

def check_historical_collect_operation_logs_table():
    """检查historical_collect_operation_logs表结构"""
    logger.info("🔍 检查historical_collect_operation_logs表结构...")
    
    session = SessionLocal()
    try:
        # 检查表是否存在
        result = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'historical_collect_operation_logs'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            logger.warning("⚠️  historical_collect_operation_logs表不存在！")
            return False
        
        # 检查表结构
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'historical_collect_operation_logs' 
            ORDER BY ordinal_position;
        """))
        
        columns = result.fetchall()
        logger.info("📋 historical_collect_operation_logs表结构:")
        for col in columns:
            logger.info(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # 检查约束
        result = session.execute(text("""
            SELECT conname, contype, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = 'historical_collect_operation_logs'::regclass;
        """))
        
        constraints = result.fetchall()
        logger.info("🔒 historical_collect_operation_logs表约束:")
        for constraint in constraints:
            logger.info(f"  - {constraint[0]}: {constraint[1]} - {constraint[2]}")
        
        # 检查是否有主键约束
        has_primary_key = any(c[1] == 'p' for c in constraints)
        logger.info(f"🔑 是否有主键约束: {has_primary_key}")
        
        return has_primary_key
        
    except Exception as e:
        logger.error(f"❌ 检查表结构失败: {e}")
        return False
    finally:
        session.close()

def main():
    """主函数"""
    logger.info("🚀 开始检查historical_quotes表...")
    
    # 检查historical_quotes表
    has_pk, has_fk = check_historical_quotes_table()
    
    # 检查historical_collect_operation_logs表
    logs_has_pk = check_historical_collect_operation_logs_table()
    
    # 总结
    logger.info("""
📊 检查结果总结:

historical_quotes表:
- 主键约束: {}
- 外键约束: {}

historical_collect_operation_logs表:
- 主键约束: {}

🔧 建议:
1. 如果historical_quotes缺少主键约束，需要添加: ALTER TABLE historical_quotes ADD CONSTRAINT historical_quotes_pkey PRIMARY KEY (code, date);
2. 如果historical_collect_operation_logs缺少主键约束，需要添加: ALTER TABLE historical_collect_operation_logs ADD CONSTRAINT historical_collect_operation_logs_pkey PRIMARY KEY (id);
3. 建议创建索引: CREATE INDEX IF NOT EXISTS idx_historical_quotes_code ON historical_quotes(code);
4. 建议创建索引: CREATE INDEX IF NOT EXISTS idx_historical_quotes_date ON historical_quotes(date);
    """.format(has_pk, has_fk, logs_has_pk))
    
    logger.info("✅ 检查完成")

if __name__ == "__main__":
    main() 