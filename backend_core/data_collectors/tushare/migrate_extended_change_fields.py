#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 为historical_quotes表添加10天和60天涨幅字段
"""

import logging
from sqlalchemy import text
from backend_core.database.db import SessionLocal

logger = logging.getLogger(__name__)

def migrate_historical_quotes_table():
    """
    为historical_quotes表添加10天和60天涨幅字段
    """
    session = SessionLocal()
    try:
        logger.info("开始迁移historical_quotes表，添加10天和60天涨幅字段...")
        
        # 检查字段是否已存在
        result = session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'historical_quotes' 
            AND column_name IN ('ten_day_change_percent', 'sixty_day_change_percent')
        """))
        
        existing_columns = [row[0] for row in result.fetchall()]
        
        # 添加10天涨幅字段
        if 'ten_day_change_percent' not in existing_columns:
            logger.info("添加ten_day_change_percent字段...")
            session.execute(text("""
                ALTER TABLE historical_quotes 
                ADD COLUMN ten_day_change_percent REAL
            """))
            logger.info("ten_day_change_percent字段添加成功")
        else:
            logger.info("ten_day_change_percent字段已存在，跳过")
        
        # 添加60天涨幅字段
        if 'sixty_day_change_percent' not in existing_columns:
            logger.info("添加sixty_day_change_percent字段...")
            session.execute(text("""
                ALTER TABLE historical_quotes 
                ADD COLUMN sixty_day_change_percent REAL
            """))
            logger.info("sixty_day_change_percent字段添加成功")
        else:
            logger.info("sixty_day_change_percent字段已存在，跳过")
        
        # 检查five_day_change_percent字段是否存在
        result = session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'historical_quotes' 
            AND column_name = 'five_day_change_percent'
        """))
        
        if not result.fetchone():
            logger.info("添加five_day_change_percent字段...")
            session.execute(text("""
                ALTER TABLE historical_quotes 
                ADD COLUMN five_day_change_percent REAL
            """))
            logger.info("five_day_change_percent字段添加成功")
        else:
            logger.info("five_day_change_percent字段已存在，跳过")
        
        session.commit()
        logger.info("historical_quotes表迁移完成")
        
        # 验证字段是否添加成功
        result = session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'historical_quotes' 
            AND column_name IN ('five_day_change_percent', 'ten_day_change_percent', 'sixty_day_change_percent')
            ORDER BY column_name
        """))
        
        added_columns = [row[0] for row in result.fetchall()]
        logger.info(f"验证结果：已添加的字段: {added_columns}")
        
        return True
        
    except Exception as e:
        logger.error(f"迁移historical_quotes表失败: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    success = migrate_historical_quotes_table()
    if success:
        print("数据库迁移成功完成！")
    else:
        print("数据库迁移失败！")
