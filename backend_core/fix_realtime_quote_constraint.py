#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 stock_realtime_quote 表的约束问题
确保表有 (code, trade_date) 的唯一约束，以支持 ON CONFLICT 语句
"""

import logging
from backend_core.database.db import SessionLocal, engine
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_table_constraints():
    """检查表的约束情况"""
    session = SessionLocal()
    try:
        # 检查表是否存在
        result = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'stock_realtime_quote'
            )
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            logger.error("表 stock_realtime_quote 不存在！")
            return False
        
        logger.info("✓ 表 stock_realtime_quote 存在")
        
        # 检查主键约束
        result = session.execute(text("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_schema = 'public' 
            AND table_name = 'stock_realtime_quote'
            AND constraint_type IN ('PRIMARY KEY', 'UNIQUE')
        """))
        
        constraints = result.fetchall()
        logger.info(f"找到 {len(constraints)} 个主键/唯一约束:")
        for constraint_name, constraint_type in constraints:
            logger.info(f"  - {constraint_name}: {constraint_type}")
            
            # 检查约束的列
            result2 = session.execute(text("""
                SELECT column_name
                FROM information_schema.key_column_usage
                WHERE table_schema = 'public'
                AND table_name = 'stock_realtime_quote'
                AND constraint_name = :constraint_name
                ORDER BY ordinal_position
            """), {"constraint_name": constraint_name})
            
            columns = [row[0] for row in result2.fetchall()]
            logger.info(f"    列: {', '.join(columns)}")
        
        # 检查是否有 (code, trade_date) 的约束
        has_code_trade_date_constraint = False
        for constraint_name, constraint_type in constraints:
            result2 = session.execute(text("""
                SELECT column_name
                FROM information_schema.key_column_usage
                WHERE table_schema = 'public'
                AND table_name = 'stock_realtime_quote'
                AND constraint_name = :constraint_name
                ORDER BY ordinal_position
            """), {"constraint_name": constraint_name})
            
            columns = [row[0] for row in result2.fetchall()]
            if set(columns) == {'code', 'trade_date'}:
                has_code_trade_date_constraint = True
                logger.info(f"✓ 找到 (code, trade_date) 约束: {constraint_name}")
                break
        
        return has_code_trade_date_constraint
        
    except Exception as e:
        logger.error(f"检查约束时出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

def fix_table_constraints():
    """修复表的约束"""
    session = SessionLocal()
    try:
        # 检查表是否存在
        result = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'stock_realtime_quote'
            )
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            logger.error("表 stock_realtime_quote 不存在！请先创建表。")
            return False
        
        # 检查是否已有 (code, trade_date) 的约束
        has_constraint = check_table_constraints()
        
        if has_constraint:
            logger.info("✓ 表已有正确的约束，无需修复")
            return True
        
        logger.info("开始修复表约束...")
        
        # 查找现有的主键约束（可能是单个code）
        result = session.execute(text("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_schema = 'public' 
            AND table_name = 'stock_realtime_quote'
            AND constraint_type = 'PRIMARY KEY'
        """))
        
        existing_pk = result.fetchone()
        if existing_pk:
            pk_name = existing_pk[0]
            logger.info(f"找到现有主键约束: {pk_name}")
            
            # 检查这个主键包含哪些列
            result2 = session.execute(text("""
                SELECT column_name
                FROM information_schema.key_column_usage
                WHERE table_schema = 'public'
                AND table_name = 'stock_realtime_quote'
                AND constraint_name = :constraint_name
                ORDER BY ordinal_position
            """), {"constraint_name": pk_name})
            
            pk_columns = [row[0] for row in result2.fetchall()]
            logger.info(f"现有主键列: {', '.join(pk_columns)}")
            
            # 如果主键不是 (code, trade_date)，需要删除并重建
            if set(pk_columns) != {'code', 'trade_date'}:
                logger.info(f"删除旧的主键约束: {pk_name}")
                session.execute(text(f"ALTER TABLE stock_realtime_quote DROP CONSTRAINT IF EXISTS {pk_name}"))
                session.commit()
        
        # 检查是否有重复数据
        logger.info("检查是否有重复数据...")
        result = session.execute(text("""
            SELECT code, trade_date, COUNT(*) as cnt
            FROM stock_realtime_quote
            GROUP BY code, trade_date
            HAVING COUNT(*) > 1
            LIMIT 10
        """))
        
        duplicates = result.fetchall()
        if duplicates:
            logger.warning(f"发现 {len(duplicates)} 组重复数据（仅显示前10组）:")
            for code, trade_date, cnt in duplicates:
                logger.warning(f"  - code={code}, trade_date={trade_date}, count={cnt}")
            
            # 删除重复数据，保留最新的
            logger.info("删除重复数据，保留最新的记录...")
            session.execute(text("""
                DELETE FROM stock_realtime_quote a
                USING stock_realtime_quote b
                WHERE a.code = b.code 
                AND a.trade_date = b.trade_date
                AND a.update_time < b.update_time
            """))
            session.commit()
            logger.info("✓ 重复数据已清理")
        else:
            logger.info("✓ 没有发现重复数据")
        
        # 添加主键约束
        logger.info("添加主键约束 (code, trade_date)...")
        try:
            session.execute(text("""
                ALTER TABLE stock_realtime_quote
                ADD CONSTRAINT stock_realtime_quote_pkey 
                PRIMARY KEY (code, trade_date)
            """))
            session.commit()
            logger.info("✓ 主键约束添加成功")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                logger.info("主键约束已存在，跳过")
            else:
                logger.error(f"添加主键约束失败: {e}")
                session.rollback()
                return False
        
        # 验证约束
        if check_table_constraints():
            logger.info("✓ 约束修复成功！")
            return True
        else:
            logger.error("✗ 约束修复后验证失败")
            return False
            
    except Exception as e:
        logger.error(f"修复约束时出错: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return False
    finally:
        session.close()

def test_on_conflict():
    """测试 ON CONFLICT 语句是否正常工作"""
    session = SessionLocal()
    try:
        logger.info("测试 ON CONFLICT 语句...")
        
        # 尝试插入一条测试数据
        test_code = "TEST999"
        test_date = "2025-11-30"
        
        # 先插入基础信息（满足外键约束）
        session.execute(text("""
            INSERT INTO stock_basic_info (code, name, create_date)
            VALUES (:code, :name, CURRENT_TIMESTAMP)
            ON CONFLICT (code) DO NOTHING
        """), {"code": test_code, "name": "测试股票"})
        session.commit()
        
        # 先删除测试数据（如果存在）
        session.execute(text("""
            DELETE FROM stock_realtime_quote 
            WHERE code = :code AND trade_date = :trade_date
        """), {"code": test_code, "trade_date": test_date})
        session.commit()
        
        # 插入测试数据
        session.execute(text("""
            INSERT INTO stock_realtime_quote
            (code, trade_date, name, current_price, change_percent, volume, amount,
            high, low, open, pre_close, turnover_rate, pe_dynamic,
            total_market_value, pb_ratio, circulating_market_value,
            update_time)
            VALUES (
                :code, :trade_date, :name, :current_price, :change_percent, :volume, :amount,
                :high, :low, :open, :pre_close, :turnover_rate, :pe_dynamic,
                :total_market_value, :pb_ratio, :circulating_market_value,
                :update_time
            )
            ON CONFLICT (code, trade_date) DO UPDATE SET
                name = EXCLUDED.name,
                current_price = EXCLUDED.current_price,
                update_time = EXCLUDED.update_time
        """), {
            "code": test_code,
            "trade_date": test_date,
            "name": "测试股票",
            "current_price": 10.0,
            "change_percent": 0.0,
            "volume": 1000.0,
            "amount": 10000.0,
            "high": 10.5,
            "low": 9.5,
            "open": 10.0,
            "pre_close": 10.0,
            "turnover_rate": None,
            "pe_dynamic": None,
            "total_market_value": None,
            "pb_ratio": None,
            "circulating_market_value": None,
            "update_time": "2025-11-30 20:00:00"
        })
        session.commit()
        logger.info("✓ 第一次插入成功")
        
        # 再次插入相同的数据（应该触发 ON CONFLICT UPDATE）
        session.execute(text("""
            INSERT INTO stock_realtime_quote
            (code, trade_date, name, current_price, change_percent, volume, amount,
            high, low, open, pre_close, turnover_rate, pe_dynamic,
            total_market_value, pb_ratio, circulating_market_value,
            update_time)
            VALUES (
                :code, :trade_date, :name, :current_price, :change_percent, :volume, :amount,
                :high, :low, :open, :pre_close, :turnover_rate, :pe_dynamic,
                :total_market_value, :pb_ratio, :circulating_market_value,
                :update_time
            )
            ON CONFLICT (code, trade_date) DO UPDATE SET
                name = EXCLUDED.name,
                current_price = EXCLUDED.current_price,
                update_time = EXCLUDED.update_time
        """), {
            "code": test_code,
            "trade_date": test_date,
            "name": "测试股票（已更新）",
            "current_price": 11.0,
            "change_percent": 0.0,
            "volume": 1000.0,
            "amount": 10000.0,
            "high": 10.5,
            "low": 9.5,
            "open": 10.0,
            "pre_close": 10.0,
            "turnover_rate": None,
            "pe_dynamic": None,
            "total_market_value": None,
            "pb_ratio": None,
            "circulating_market_value": None,
            "update_time": "2025-11-30 20:01:00"
        })
        session.commit()
        logger.info("✓ 第二次插入（ON CONFLICT UPDATE）成功")
        
        # 清理测试数据
        session.execute(text("""
            DELETE FROM stock_realtime_quote 
            WHERE code = :code AND trade_date = :trade_date
        """), {"code": test_code, "trade_date": test_date})
        session.execute(text("""
            DELETE FROM stock_basic_info 
            WHERE code = :code
        """), {"code": test_code})
        session.commit()
        logger.info("✓ ON CONFLICT 测试通过！")
        
        return True
        
    except Exception as e:
        logger.error(f"ON CONFLICT 测试失败: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return False
    finally:
        session.close()

def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("修复 stock_realtime_quote 表约束")
    logger.info("=" * 60)
    
    # 检查约束
    logger.info("\n1. 检查表约束...")
    has_constraint = check_table_constraints()
    
    if not has_constraint:
        # 修复约束
        logger.info("\n2. 修复表约束...")
        success = fix_table_constraints()
        
        if not success:
            logger.error("✗ 约束修复失败")
            return 1
    else:
        logger.info("\n2. 表约束正常，跳过修复")
    
    # 测试 ON CONFLICT
    logger.info("\n3. 测试 ON CONFLICT 语句...")
    test_success = test_on_conflict()
    
    if test_success:
        logger.info("\n" + "=" * 60)
        logger.info("✓ 所有检查和测试通过！")
        logger.info("=" * 60)
        return 0
    else:
        logger.error("\n" + "=" * 60)
        logger.error("✗ 测试失败")
        logger.error("=" * 60)
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

