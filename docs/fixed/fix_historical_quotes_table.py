#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 historical_quotes 表主键和索引
解决生产环境缺少主键约束的问题
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
            logger.error("❌ historical_quotes表不存在！")
            return False
        
        # 检查约束
        result = session.execute(text("""
            SELECT conname, contype, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = 'historical_quotes'::regclass;
        """))
        
        constraints = result.fetchall()
        logger.info("🔒 当前约束:")
        for constraint in constraints:
            logger.info(f"  - {constraint[0]}: {constraint[1]} - {constraint[2]}")
        
        # 检查索引
        result = session.execute(text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'historical_quotes';
        """))
        
        indexes = result.fetchall()
        logger.info("📊 当前索引:")
        for index in indexes:
            logger.info(f"  - {index[0]}: {index[1]}")
        
        # 检查是否有主键约束
        has_primary_key = any(c[1] == 'p' for c in constraints)
        logger.info(f"🔑 是否有主键约束: {has_primary_key}")
        
        return has_primary_key
        
    except Exception as e:
        logger.error(f"❌ 检查表结构失败: {e}")
        return False
    finally:
        session.close()

def fix_table_structure():
    """修复表结构"""
    logger.info("🔧 修复historical_quotes表结构...")
    
    session = SessionLocal()
    try:
        # 1. 删除重复数据（基于code和date）
        logger.info("🗑️  删除重复数据...")
        
        # 查找重复数据
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
            
            # 删除重复数据，保留每组的第一条
            session.execute(text("""
                DELETE FROM historical_quotes 
                WHERE ctid NOT IN (
                    SELECT MIN(ctid) 
                    FROM historical_quotes 
                    GROUP BY code, date
                )
            """))
            logger.info("✅ 重复数据删除完成")
        
        # 2. 删除可能有问题的约束（SQLite迁移过来的）
        logger.info("🔧 删除旧约束...")
        
        # 删除可能存在的旧主键约束
        session.execute(text("""
            ALTER TABLE historical_quotes DROP CONSTRAINT IF EXISTS idx_16466_sqlite_autoindex_historical_quotes_1;
        """))
        session.execute(text("""
            ALTER TABLE historical_quotes DROP CONSTRAINT IF EXISTS historical_quotes_pkey;
        """))
        
        # 3. 添加主键约束
        logger.info("🔑 添加主键约束...")
        
        # 检查是否已经有主键约束
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM pg_constraint 
            WHERE conrelid = 'historical_quotes'::regclass 
            AND contype = 'p'
        """))
        
        if result.scalar() == 0:
            session.execute(text("""
                ALTER TABLE historical_quotes ADD CONSTRAINT historical_quotes_pkey PRIMARY KEY (code, date);
            """))
            logger.info("✅ 主键约束添加成功")
        else:
            logger.info("ℹ️  主键约束已存在")
        
        # 4. 创建索引
        logger.info("📊 创建索引...")
        
        # 检查并创建code索引
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE tablename = 'historical_quotes' 
            AND indexname = 'idx_historical_quotes_code'
        """))
        
        if result.scalar() == 0:
            session.execute(text("""
                CREATE INDEX idx_historical_quotes_code ON historical_quotes(code);
            """))
            logger.info("✅ code索引创建成功")
        
        # 检查并创建date索引
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE tablename = 'historical_quotes' 
            AND indexname = 'idx_historical_quotes_date'
        """))
        
        if result.scalar() == 0:
            session.execute(text("""
                CREATE INDEX idx_historical_quotes_date ON historical_quotes(date);
            """))
            logger.info("✅ date索引创建成功")
        
        # 检查并创建collected_date索引
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE tablename = 'historical_quotes' 
            AND indexname = 'idx_historical_quotes_collected_date'
        """))
        
        if result.scalar() == 0:
            session.execute(text("""
                CREATE INDEX idx_historical_quotes_collected_date ON historical_quotes(collected_date);
            """))
            logger.info("✅ collected_date索引创建成功")
        
        # 5. 更新表统计信息
        session.execute(text("ANALYZE historical_quotes"))
        logger.info("✅ 表统计信息更新完成")
        
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
    """如果表不存在则创建表"""
    logger.info("🏗️  检查并创建historical_quotes表...")
    
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
            logger.info("📋 创建historical_quotes表...")
            session.execute(text("""
                CREATE TABLE historical_quotes (
                    code VARCHAR(20) NOT NULL,
                    ts_code VARCHAR(20),
                    name VARCHAR(100),
                    market VARCHAR(20),
                    date VARCHAR(8) NOT NULL,
                    open DECIMAL(10,2),
                    close DECIMAL(10,2),
                    high DECIMAL(10,2),
                    low DECIMAL(10,2),
                    pre_close DECIMAL(10,2),
                    volume BIGINT,
                    amount DECIMAL(15,2),
                    amplitude DECIMAL(8,2),
                    change_percent DECIMAL(8,2),
                    change DECIMAL(10,2),
                    turnover_rate DECIMAL(8,2),
                    collected_source VARCHAR(50),
                    collected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (code, date)
                );
            """))
            
            # 创建索引
            session.execute(text("""
                CREATE INDEX idx_historical_quotes_code ON historical_quotes(code);
            """))
            session.execute(text("""
                CREATE INDEX idx_historical_quotes_date ON historical_quotes(date);
            """))
            session.execute(text("""
                CREATE INDEX idx_historical_quotes_collected_date ON historical_quotes(collected_date);
            """))
            
            logger.info("✅ historical_quotes表创建成功")
        else:
            logger.info("ℹ️  historical_quotes表已存在")
        
        session.commit()
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
            'market': 'SZ',
            'date': '20250801',
            'open': 10.50,
            'high': 10.80,
            'low': 10.20,
            'close': 10.60,
            'volume': 1000000,
            'amount': 10600000,
            'change_percent': 2.5,
            'collected_source': 'test'
        }
        
        # 测试ON CONFLICT插入
        session.execute(text("""
            INSERT INTO historical_quotes (
                code, name, market, date, open, high, low, close, 
                volume, amount, change_percent, collected_source
            ) VALUES (
                :code, :name, :market, :date, :open, :high, :low, :close,
                :volume, :amount, :change_percent, :collected_source
            ) ON CONFLICT (code, date) DO UPDATE SET
                name = EXCLUDED.name,
                market = EXCLUDED.market,
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume,
                amount = EXCLUDED.amount,
                change_percent = EXCLUDED.change_percent,
                collected_source = EXCLUDED.collected_source
        """), test_data)
        
        session.commit()
        logger.info("✅ ON CONFLICT插入测试成功")
        
        # 清理测试数据
        session.execute(text("DELETE FROM historical_quotes WHERE code = '000001' AND date = '20250801'"))
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
    logger.info("🚀 开始修复historical_quotes表...")
    
    # 1. 检查表结构
    has_primary_key = check_table_structure()
    
    # 2. 如果表不存在，创建表
    if not has_primary_key:
        if not create_table_if_not_exists():
            logger.error("❌ 创建表失败")
            return
    
    # 3. 修复表结构
    if not fix_table_structure():
        logger.error("❌ 修复表结构失败")
        return
    
    # 4. 再次检查表结构
    check_table_structure()
    
    # 5. 测试插入操作
    if not test_insert():
        logger.error("❌ 插入测试失败")
        return
    
    logger.info("""
🎉 修复完成！

📊 修复内容:
1. ✅ 检查并删除重复数据
2. ✅ 删除旧约束（SQLite迁移遗留）
3. ✅ 添加主键约束 (code, date)
4. ✅ 创建性能优化索引
5. ✅ 更新表统计信息
6. ✅ 测试ON CONFLICT插入操作

🔧 创建的索引:
- idx_historical_quotes_code: 股票代码索引
- idx_historical_quotes_date: 日期索引  
- idx_historical_quotes_collected_date: 采集时间索引

📝 生产环境建议:
1. 定期监控索引使用情况
2. 定期清理历史数据
3. 监控插入性能
4. 考虑分区表优化大数据量
    """)

if __name__ == "__main__":
    main() 