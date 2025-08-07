#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 stock_realtime_quote 表结构
参考 stock_basic_info 的主外键约束处理和检查
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend_core.database.db import SessionLocal, engine
from sqlalchemy import text
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_table_structure():
    """检查表结构"""
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
        logger.info("📋 当前表结构:")
        for col in columns:
            logger.info(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # 检查约束
        result = session.execute(text("""
            SELECT conname, contype, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = 'stock_realtime_quote'::regclass;
        """))
        
        constraints = result.fetchall()
        logger.info("🔒 当前约束:")
        for constraint in constraints:
            logger.info(f"  - {constraint[0]}: {constraint[1]} - {constraint[2]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 检查表结构失败: {e}")
        return False
    finally:
        session.close()

def fix_table_structure():
    """修复表结构"""
    logger.info("🔧 修复stock_realtime_quote表结构...")
    
    session = SessionLocal()
    try:
        # 1. 删除可能存在的重复数据
        logger.info("🗑️  删除重复数据...")
        session.execute(text("""
            DELETE FROM stock_realtime_quote a USING stock_realtime_quote b 
            WHERE a.ctid < b.ctid AND a.code = b.code;
        """))
        
        # 2. 删除可能有问题的约束（SQLite迁移过来的）
        logger.info("🔧 删除SQLite迁移的约束...")
        session.execute(text("""
            ALTER TABLE stock_realtime_quote DROP CONSTRAINT IF EXISTS idx_16466_sqlite_autoindex_stock_realtime_quote_1;
        """))
        session.execute(text("""
            ALTER TABLE stock_realtime_quote DROP CONSTRAINT IF EXISTS stock_realtime_quote_code_fkey;
        """))
        
        # 3. 添加标准的主键约束
        logger.info("🔑 添加主键约束...")
        session.execute(text("""
            ALTER TABLE stock_realtime_quote ADD CONSTRAINT stock_realtime_quote_pkey PRIMARY KEY (code);
        """))
        
        # 4. 添加外键约束（如果stock_basic_info表存在）
        logger.info("🔗 检查并添加外键约束...")
        result = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'stock_basic_info'
            );
        """))
        basic_info_exists = result.scalar()
        
        if basic_info_exists:
            # 检查stock_basic_info是否有主键约束
            result = session.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conrelid = 'stock_basic_info'::regclass 
                    AND contype = 'p'
                );
            """))
            basic_info_has_pk = result.scalar()
            
            if basic_info_has_pk:
                session.execute(text("""
                    ALTER TABLE stock_realtime_quote 
                    ADD CONSTRAINT fk_stock_realtime_quote_code 
                    FOREIGN KEY (code) REFERENCES stock_basic_info(code);
                """))
                logger.info("✅ 外键约束添加成功")
            else:
                logger.warning("⚠️  stock_basic_info表缺少主键约束，跳过外键约束添加")
        else:
            logger.warning("⚠️  stock_basic_info表不存在，跳过外键约束添加")
        
        # 5. 创建索引
        logger.info("📊 创建索引...")
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_stock_realtime_quote_update_time 
            ON stock_realtime_quote(update_time);
        """))
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_stock_realtime_quote_name 
            ON stock_realtime_quote(name);
        """))
        
        session.commit()
        logger.info("✅ 表结构修复完成")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ 修复表结构失败: {e}")
        return False
    finally:
        session.close()

def create_table_if_not_exists():
    """如果表不存在，创建表"""
    logger.info("🏗️  检查是否需要创建表...")
    
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
            logger.info("📋 创建stock_realtime_quote表...")
            session.execute(text("""
                CREATE TABLE stock_realtime_quote (
                    code TEXT PRIMARY KEY,
                    name TEXT,
                    current_price REAL,
                    change_percent REAL,
                    volume REAL,
                    amount REAL,
                    high REAL,
                    low REAL,
                    open REAL,
                    pre_close REAL,
                    turnover_rate REAL,
                    pe_dynamic REAL,
                    total_market_value REAL,
                    pb_ratio REAL,
                    circulating_market_value REAL,
                    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # 创建索引
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_stock_realtime_quote_update_time 
                ON stock_realtime_quote(update_time);
            """))
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_stock_realtime_quote_name 
                ON stock_realtime_quote(name);
            """))
            
            session.commit()
            logger.info("✅ 表创建完成")
            return True
        else:
            logger.info("✅ 表已存在")
            return True
            
    except Exception as e:
        session.rollback()
        logger.error(f"❌ 创建表失败: {e}")
        return False
    finally:
        session.close()

def test_insert():
    """测试插入操作"""
    logger.info("🧪 测试插入操作...")
    
    session = SessionLocal()
    try:
        # 测试数据
        test_data = {
            'code': '000001',
            'name': '平安银行',
            'current_price': 10.50,
            'change_percent': 2.5,
            'volume': 1000000,
            'amount': 10500000,
            'high': 10.80,
            'low': 10.20,
            'open': 10.30,
            'pre_close': 10.25,
            'turnover_rate': 1.2,
            'pe_dynamic': 15.5,
            'total_market_value': 1000000000,
            'pb_ratio': 1.2,
            'circulating_market_value': 800000000,
            'update_time': '2025-08-01 16:30:00'
        }
        
        # 测试ON CONFLICT插入
        session.execute(text("""
            INSERT INTO stock_realtime_quote (
                code, name, current_price, change_percent, volume, amount,
                high, low, open, pre_close, turnover_rate, pe_dynamic,
                total_market_value, pb_ratio, circulating_market_value, update_time
            ) VALUES (
                :code, :name, :current_price, :change_percent, :volume, :amount,
                :high, :low, :open, :pre_close, :turnover_rate, :pe_dynamic,
                :total_market_value, :pb_ratio, :circulating_market_value, :update_time
            ) ON CONFLICT (code) DO UPDATE SET
                name = EXCLUDED.name,
                current_price = EXCLUDED.current_price,
                change_percent = EXCLUDED.change_percent,
                volume = EXCLUDED.volume,
                amount = EXCLUDED.amount,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                open = EXCLUDED.open,
                pre_close = EXCLUDED.pre_close,
                turnover_rate = EXCLUDED.turnover_rate,
                pe_dynamic = EXCLUDED.pe_dynamic,
                total_market_value = EXCLUDED.total_market_value,
                pb_ratio = EXCLUDED.pb_ratio,
                circulating_market_value = EXCLUDED.circulating_market_value,
                update_time = EXCLUDED.update_time
        """), test_data)
        
        session.commit()
        logger.info("✅ ON CONFLICT插入测试成功")
        
        # 清理测试数据
        session.execute(text("DELETE FROM stock_realtime_quote WHERE code = '000001'"))
        session.commit()
        logger.info("🧹 测试数据清理完成")
        
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ 测试插入失败: {e}")
        return False
    finally:
        session.close()

def main():
    """主函数"""
    logger.info("🚀 开始修复stock_realtime_quote表...")
    
    # 1. 检查表结构
    if not check_table_structure():
        logger.error("❌ 表结构检查失败")
        return
    
    # 2. 确保表存在
    if not create_table_if_not_exists():
        logger.error("❌ 表创建失败")
        return
    
    # 3. 修复表结构
    if not fix_table_structure():
        logger.error("❌ 表结构修复失败")
        return
    
    # 4. 测试插入
    if not test_insert():
        logger.error("❌ 插入测试失败")
        return
    
    logger.info("""
🎉 修复完成！

📊 修复内容:
1. ✅ 检查并修复主键约束
2. ✅ 检查并修复外键约束（如果stock_basic_info表存在）
3. ✅ 创建必要的索引
4. ✅ 测试ON CONFLICT插入操作

🔧 如果生产环境仍有问题，请检查:
1. 数据类型是否匹配
2. 外键引用的表是否存在
3. 事务隔离级别设置
    """)

if __name__ == "__main__":
    main() 