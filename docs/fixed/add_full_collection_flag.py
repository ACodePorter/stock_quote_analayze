#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 stock_basic_info 表添加全量采集标志字段
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend_core.database.db import SessionLocal
from sqlalchemy import text
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_full_collection_fields():
    """为stock_basic_info表添加全量采集标志字段"""
    session = SessionLocal()
    try:
        logger.info("开始为stock_basic_info表添加全量采集标志字段...")
        
        # 1. 检查当前表结构
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'stock_basic_info' 
            ORDER BY ordinal_position;
        """))
        
        columns = result.fetchall()
        logger.info("当前表结构:")
        for col in columns:
            logger.info(f"  {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # 2. 添加全量采集标志字段
        logger.info("添加全量采集标志字段...")
        
        # 添加完成标志字段
        session.execute(text("""
            ALTER TABLE stock_basic_info 
            ADD COLUMN IF NOT EXISTS full_collection_completed BOOLEAN DEFAULT FALSE
        """))
        
        # 添加完成时间字段
        session.execute(text("""
            ALTER TABLE stock_basic_info 
            ADD COLUMN IF NOT EXISTS full_collection_date TIMESTAMP
        """))
        
        # 添加开始日期字段
        session.execute(text("""
            ALTER TABLE stock_basic_info 
            ADD COLUMN IF NOT EXISTS full_collection_start_date DATE
        """))
        
        # 添加结束日期字段
        session.execute(text("""
            ALTER TABLE stock_basic_info 
            ADD COLUMN IF NOT EXISTS full_collection_end_date DATE
        """))
        
        # 3. 创建索引
        logger.info("创建索引...")
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_stock_basic_info_full_collection_completed 
            ON stock_basic_info(full_collection_completed)
        """))
        
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_stock_basic_info_full_collection_date 
            ON stock_basic_info(full_collection_date)
        """))
        
        session.commit()
        logger.info("字段添加成功！")
        
        # 4. 验证字段添加结果
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'stock_basic_info' 
            ORDER BY ordinal_position;
        """))
        
        columns = result.fetchall()
        logger.info("更新后的表结构:")
        for col in columns:
            logger.info(f"  {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # 5. 显示当前全量采集状态统计
        result = session.execute(text("""
            SELECT 
                full_collection_completed,
                COUNT(*) as stock_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM stock_basic_info), 2) as percentage
            FROM stock_basic_info 
            GROUP BY full_collection_completed 
            ORDER BY full_collection_completed;
        """))
        
        stats = result.fetchall()
        logger.info("当前全量采集状态统计:")
        for stat in stats:
            completed = "已完成" if stat[0] else "未完成"
            logger.info(f"  {completed}: {stat[1]} 只股票 ({stat[2]}%)")
        
        return True
        
    except Exception as e:
        logger.error(f"添加字段失败: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = add_full_collection_fields()
    if success:
        logger.info("✅ 数据库迁移完成！")
    else:
        logger.error("❌ 数据库迁移失败！")
