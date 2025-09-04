#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析扩展涨跌幅计算失败的原因
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend_core.database.db import SessionLocal
from sqlalchemy import text
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_extended_change_failures():
    """分析扩展涨跌幅计算失败的原因"""
    logger.info("🔍 开始分析扩展涨跌幅计算失败的原因...")
    
    session = SessionLocal()
    try:
        # 1. 检查目标日期的数据情况
        target_date = "2025-09-03"
        logger.info(f"📊 分析日期: {target_date}")
        
        # 检查该日期的总记录数
        result = session.execute(text("""
            SELECT COUNT(*) as total_records
            FROM historical_quotes 
            WHERE date = :target_date
        """), {"target_date": target_date})
        
        total_records = result.scalar()
        logger.info(f"📈 日期 {target_date} 的总记录数: {total_records}")
        
        # 2. 检查需要计算的股票数量
        result = session.execute(text("""
            SELECT COUNT(DISTINCT code) as need_calc_count
            FROM historical_quotes 
            WHERE date = :target_date 
            AND (five_day_change_percent IS NULL 
                 OR ten_day_change_percent IS NULL 
                 OR sixty_day_change_percent IS NULL)
        """), {"target_date": target_date})
        
        need_calc_count = result.scalar()
        logger.info(f"🔢 需要计算扩展涨跌幅的股票数量: {need_calc_count}")
        
        # 3. 检查已计算的数量
        result = session.execute(text("""
            SELECT COUNT(DISTINCT code) as calculated_count
            FROM historical_quotes 
            WHERE date = :target_date 
            AND five_day_change_percent IS NOT NULL 
            AND ten_day_change_percent IS NOT NULL 
            AND sixty_day_change_percent IS NOT NULL
        """), {"target_date": target_date})
        
        calculated_count = result.scalar()
        logger.info(f"✅ 已计算扩展涨跌幅的股票数量: {calculated_count}")
        
        # 4. 分析失败的具体原因 - 检查历史数据不足的情况
        logger.info("🔍 分析失败原因...")
        
        # 获取需要计算但失败的股票列表
        result = session.execute(text("""
            SELECT DISTINCT code 
            FROM historical_quotes 
            WHERE date = :target_date 
            AND (five_day_change_percent IS NULL 
                 OR ten_day_change_percent IS NULL 
                 OR sixty_day_change_percent IS NULL)
            ORDER BY code
            LIMIT 10
        """), {"target_date": target_date})
        
        failed_stocks = [row[0] for row in result.fetchall()]
        logger.info(f"📋 前10个失败的股票代码: {failed_stocks}")
        
        # 5. 详细分析几个失败的股票
        for stock_code in failed_stocks[:5]:  # 只分析前5个
            analyze_single_stock(session, stock_code, target_date)
        
        # 6. 统计历史数据不足的情况
        result = session.execute(text("""
            SELECT 
                COUNT(*) as insufficient_data_count,
                COUNT(CASE WHEN data_count < 61 THEN 1 END) as less_than_61_days,
                COUNT(CASE WHEN data_count < 10 THEN 1 END) as less_than_10_days,
                COUNT(CASE WHEN data_count < 5 THEN 1 END) as less_than_5_days
            FROM (
                SELECT 
                    code,
                    COUNT(*) as data_count
                FROM historical_quotes 
                WHERE code IN (
                    SELECT DISTINCT code 
                    FROM historical_quotes 
                    WHERE date = :target_date 
                    AND (five_day_change_percent IS NULL 
                         OR ten_day_change_percent IS NULL 
                         OR sixty_day_change_percent IS NULL)
                )
                AND date <= :target_date
                GROUP BY code
            ) subquery
        """), {"target_date": target_date})
        
        stats = result.fetchone()
        logger.info(f"📊 历史数据统计:")
        logger.info(f"  - 数据不足的股票总数: {stats[0]}")
        logger.info(f"  - 少于61天数据的股票: {stats[1]}")
        logger.info(f"  - 少于10天数据的股票: {stats[2]}")
        logger.info(f"  - 少于5天数据的股票: {stats[3]}")
        
        # 7. 检查数据质量问题
        result = session.execute(text("""
            SELECT 
                COUNT(*) as invalid_close_count
            FROM historical_quotes 
            WHERE date = :target_date 
            AND (close IS NULL OR close <= 0)
        """), {"target_date": target_date})
        
        invalid_close_count = result.scalar()
        logger.info(f"❌ 收盘价无效的记录数: {invalid_close_count}")
        
        # 8. 检查数据连续性
        result = session.execute(text("""
            SELECT 
                code,
                COUNT(*) as data_count,
                MIN(date) as earliest_date,
                MAX(date) as latest_date
            FROM historical_quotes 
            WHERE code IN (
                SELECT DISTINCT code 
                FROM historical_quotes 
                WHERE date = :target_date 
                AND (five_day_change_percent IS NULL 
                     OR ten_day_change_percent IS NULL 
                     OR sixty_day_change_percent IS NULL)
            )
            AND date <= :target_date
            GROUP BY code
            HAVING COUNT(*) < 61
            ORDER BY data_count ASC
            LIMIT 5
        """), {"target_date": target_date})
        
        insufficient_data_stocks = result.fetchall()
        logger.info(f"📉 数据不足的股票详情（前5个）:")
        for stock in insufficient_data_stocks:
            logger.info(f"  - {stock[0]}: {stock[1]}天数据 ({stock[2]} 到 {stock[3]})")
        
    except Exception as e:
        logger.error(f"❌ 分析过程中发生错误: {e}")
    finally:
        session.close()

def analyze_single_stock(session, stock_code: str, target_date: str):
    """分析单个股票的计算失败原因"""
    logger.info(f"🔍 分析股票 {stock_code} 的计算失败原因...")
    
    try:
        # 获取该股票的历史数据
        result = session.execute(text("""
            SELECT date, close 
            FROM historical_quotes 
            WHERE code = :stock_code 
            AND date <= :target_date
            ORDER BY date ASC
        """), {
            "stock_code": stock_code,
            "target_date": target_date
        })
        
        quotes = result.fetchall()
        logger.info(f"  📊 股票 {stock_code} 的历史数据条数: {len(quotes)}")
        
        if len(quotes) == 0:
            logger.info(f"  ❌ 股票 {stock_code} 没有历史数据")
            return
        
        # 检查目标日期是否存在
        target_quote = None
        for quote in quotes:
            if quote[0] == target_date:
                target_quote = quote
                break
        
        if not target_quote:
            logger.info(f"  ❌ 股票 {stock_code} 在 {target_date} 没有数据")
            return
        
        # 检查收盘价是否有效
        if not target_quote[1] or target_quote[1] <= 0:
            logger.info(f"  ❌ 股票 {stock_code} 在 {target_date} 的收盘价无效: {target_quote[1]}")
            return
        
        # 检查是否有足够的历史数据
        if len(quotes) < 61:
            logger.info(f"  ❌ 股票 {stock_code} 历史数据不足61天，只有 {len(quotes)} 天")
            return
        
        # 检查5日、10日、60日前是否有有效数据
        target_index = None
        for i, quote in enumerate(quotes):
            if quote[0] == target_date:
                target_index = i
                break
        
        if target_index is None:
            logger.info(f"  ❌ 股票 {stock_code} 无法找到目标日期位置")
            return
        
        # 检查各期数据
        if target_index >= 5:
            prev_5_quote = quotes[target_index - 5]
            if not prev_5_quote[1] or prev_5_quote[1] <= 0:
                logger.info(f"  ❌ 股票 {stock_code} 5日前收盘价无效: {prev_5_quote[1]}")
                return
        
        if target_index >= 10:
            prev_10_quote = quotes[target_index - 10]
            if not prev_10_quote[1] or prev_10_quote[1] <= 0:
                logger.info(f"  ❌ 股票 {stock_code} 10日前收盘价无效: {prev_10_quote[1]}")
                return
        
        if target_index >= 60:
            prev_60_quote = quotes[target_index - 60]
            if not prev_60_quote[1] or prev_60_quote[1] <= 0:
                logger.info(f"  ❌ 股票 {stock_code} 60日前收盘价无效: {prev_60_quote[1]}")
                return
        
        logger.info(f"  ✅ 股票 {stock_code} 数据看起来正常，可能是其他原因导致计算失败")
        
    except Exception as e:
        logger.error(f"  ❌ 分析股票 {stock_code} 时发生错误: {e}")

def check_database_connection():
    """检查数据库连接"""
    logger.info("🔌 检查数据库连接...")
    
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT 1"))
        logger.info("✅ 数据库连接正常")
        return True
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    logger.info("🚀 开始扩展涨跌幅计算失败分析...")
    
    if check_database_connection():
        analyze_extended_change_failures()
    else:
        logger.error("❌ 数据库连接失败，无法进行分析")
        sys.exit(1)
    
    logger.info("✅ 分析完成")
