#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展 historical_quotes 表结构
添加累计升跌%、5天升跌%和备注字段
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend_core.database.db import SessionLocal, engine
from sqlalchemy import text
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_current_structure():
    """检查当前表结构"""
    logger.info("🔍 检查当前historical_quotes表结构...")
    
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
        
        # 检查当前列结构
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'historical_quotes' 
            ORDER BY ordinal_position;
        """))
        
        columns = result.fetchall()
        logger.info("📋 当前表结构:")
        for col in columns:
            logger.info(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 检查表结构失败: {e}")
        return False
    finally:
        session.close()

def extend_table_structure():
    """扩展表结构"""
    logger.info("🏗️  开始扩展表结构...")
    
    session = SessionLocal()
    try:
        # 1. 添加累计升跌%字段
        logger.info("📊 添加累计升跌%字段...")
        session.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'historical_quotes' 
                    AND column_name = 'cumulative_change_percent'
                ) THEN
                    ALTER TABLE historical_quotes ADD COLUMN cumulative_change_percent DECIMAL(8,2);
                    RAISE NOTICE '累计升跌%%字段添加成功';
                ELSE
                    RAISE NOTICE '累计升跌%%字段已存在';
                END IF;
            END $$;
        """))
        
        # 2. 添加5天升跌%字段
        logger.info("📊 添加5天升跌%字段...")
        session.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'historical_quotes' 
                    AND column_name = 'five_day_change_percent'
                ) THEN
                    ALTER TABLE historical_quotes ADD COLUMN five_day_change_percent DECIMAL(8,2);
                    RAISE NOTICE '5天升跌%%字段添加成功';
                ELSE
                    RAISE NOTICE '5天升跌%%字段已存在';
                END IF;
            END $$;
        """))
        
        # 3. 添加备注字段
        logger.info("📝 添加备注字段...")
        session.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'historical_quotes' 
                    AND column_name = 'remarks'
                ) THEN
                    ALTER TABLE historical_quotes ADD COLUMN remarks TEXT;
                    RAISE NOTICE '备注字段添加成功';
                ELSE
                    RAISE NOTICE '备注字段已存在';
                END IF;
            END $$;
        """))
        
        session.commit()
        logger.info("✅ 表结构扩展完成")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ 扩展表结构失败: {e}")
        return False
    finally:
        session.close()

def create_trading_notes_table():
    """创建交易备注表"""
    logger.info("📋 创建trading_notes表...")
    
    session = SessionLocal()
    try:
        # 创建trading_notes表
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS trading_notes (
                id SERIAL PRIMARY KEY,
                stock_code VARCHAR(20) NOT NULL,
                trade_date DATE NOT NULL,
                notes TEXT,
                strategy_type VARCHAR(50),
                risk_level VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(50),
                UNIQUE(stock_code, trade_date)
            );
        """))
        
        # 创建索引
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_trading_notes_stock_code ON trading_notes(stock_code);
        """))
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_trading_notes_trade_date ON trading_notes(trade_date);
        """))
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_trading_notes_strategy_type ON trading_notes(strategy_type);
        """))
        
        session.commit()
        logger.info("✅ trading_notes表创建完成")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ 创建trading_notes表失败: {e}")
        return False
    finally:
        session.close()

def create_view_and_functions():
    """创建视图和函数"""
    logger.info("🔧 创建视图和函数...")
    
    session = SessionLocal()
    try:
        # 创建视图 - 修复类型不匹配问题
        session.execute(text("""
            CREATE OR REPLACE VIEW historical_quotes_with_notes AS
            SELECT 
                h.*,
                COALESCE(tn.notes, '') as user_notes,
                COALESCE(tn.strategy_type, '') as strategy_type,
                COALESCE(tn.risk_level, '') as risk_level,
                COALESCE(tn.created_by, '') as notes_creator,
                tn.created_at as notes_created_at,
                tn.updated_at as notes_updated_at
            FROM historical_quotes h
            LEFT JOIN trading_notes tn ON h.code = tn.stock_code AND h.date::date = tn.trade_date;
        """))
        
        # 创建触发器函数
        session.execute(text("""
            CREATE OR REPLACE FUNCTION update_trading_notes_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))
        
        # 创建触发器
        session.execute(text("""
            DROP TRIGGER IF EXISTS trigger_update_trading_notes_updated_at ON trading_notes;
            CREATE TRIGGER trigger_update_trading_notes_updated_at
                BEFORE UPDATE ON trading_notes
                FOR EACH ROW
                EXECUTE FUNCTION update_trading_notes_updated_at();
        """))
        
        session.commit()
        logger.info("✅ 视图和函数创建完成")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ 创建视图和函数失败: {e}")
        return False
    finally:
        session.close()

def insert_test_data():
    """插入测试数据"""
    logger.info("🧪 插入测试数据...")
    
    session = SessionLocal()
    try:
        # 插入测试备注数据
        session.execute(text("""
            INSERT INTO trading_notes (stock_code, trade_date, notes, strategy_type, risk_level, created_by)
            VALUES 
                ('000001', '2025-08-01', '放量上涨，明天如果过7元就卖掉', '卖出信号', '中', 'wangxw1'),
                ('000001', '2025-08-02', '放量上涨', '观察', '低', 'wangxw1'),
                ('000001', '2025-08-03', '缩量下跌，跌到7元以下的时候可以买入一点', '买入信号', '中', 'wangxw1')
            ON CONFLICT (stock_code, trade_date) DO UPDATE SET
                notes = EXCLUDED.notes,
                strategy_type = EXCLUDED.strategy_type,
                risk_level = EXCLUDED.risk_level,
                updated_at = CURRENT_TIMESTAMP;
        """))
        
        session.commit()
        logger.info("✅ 测试数据插入完成")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ 插入测试数据失败: {e}")
        return False
    finally:
        session.close()

def verify_extension():
    """验证扩展结果"""
    logger.info("🔍 验证扩展结果...")
    
    session = SessionLocal()
    try:
        # 检查扩展后的表结构
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'historical_quotes' 
            ORDER BY ordinal_position;
        """))
        
        columns = result.fetchall()
        logger.info("📋 扩展后表结构:")
        for col in columns:
            logger.info(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # 检查trading_notes表
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'trading_notes' 
            ORDER BY ordinal_position;
        """))
        
        columns = result.fetchall()
        logger.info("📋 trading_notes表结构:")
        for col in columns:
            logger.info(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # 测试视图查询
        result = session.execute(text("""
            SELECT 
                code, 
                date, 
                user_notes, 
                strategy_type, 
                risk_level
            FROM historical_quotes_with_notes 
            WHERE code = '000001' 
            ORDER BY date DESC 
            LIMIT 3;
        """))
        
        rows = result.fetchall()
        logger.info("🔍 测试视图查询结果:")
        for row in rows:
            logger.info(f"  - {row[0]} {row[1]}: {row[2]} ({row[3]}, {row[4]})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 验证扩展结果失败: {e}")
        return False
    finally:
        session.close()

def main():
    """主函数"""
    logger.info("🚀 开始执行historical_quotes表结构扩展...")
    
    try:
        # 步骤1: 检查当前结构
        if not check_current_structure():
            logger.error("❌ 检查当前结构失败，终止执行")
            return False
        
        # 步骤2: 扩展表结构
        if not extend_table_structure():
            logger.error("❌ 扩展表结构失败，终止执行")
            return False
        
        # 步骤3: 创建trading_notes表
        if not create_trading_notes_table():
            logger.error("❌ 创建trading_notes表失败，终止执行")
            return False
        
        # 步骤4: 创建视图和函数
        if not create_view_and_functions():
            logger.error("❌ 创建视图和函数失败，终止执行")
            return False
        
        # 步骤5: 插入测试数据
        if not insert_test_data():
            logger.error("❌ 插入测试数据失败，终止执行")
            return False
        
        # 步骤6: 验证扩展结果
        if not verify_extension():
            logger.error("❌ 验证扩展结果失败，终止执行")
            return False
        
        logger.info("🎉 historical_quotes表结构扩展完成！")
        logger.info("📊 新增字段:")
        logger.info("  - cumulative_change_percent: 累计升跌%")
        logger.info("  - five_day_change_percent: 5天升跌%")
        logger.info("  - remarks: 备注")
        logger.info("📋 新增功能:")
        logger.info("  - trading_notes表: 交易备注管理")
        logger.info("  - historical_quotes_with_notes视图: 合并显示")
        logger.info("  - calculate_cumulative_change函数: 计算累计升跌%")
        logger.info("  - calculate_five_day_change函数: 计算5天升跌%")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 执行过程中发生异常: {e}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 表结构扩展成功完成！")
        sys.exit(0)
    else:
        print("\n❌ 表结构扩展失败！")
        sys.exit(1)
