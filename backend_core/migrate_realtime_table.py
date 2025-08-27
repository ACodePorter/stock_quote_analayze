#!/usr/bin/env python3
"""
数据库迁移脚本：为stock_realtime_quote表添加trade_date字段
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime
import time

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def migrate_realtime_table():
    """迁移实时数据表结构"""
    logger = logging.getLogger(__name__)
    logger.info("开始迁移stock_realtime_quote表结构...")
    
    try:
        # 添加项目根目录到Python路径
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from backend_core.database.db import SessionLocal
        from sqlalchemy import text
        
        session = SessionLocal()
        
        try:
            # 检查表是否存在
            result = session.execute(text('''
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'stock_realtime_quote'
                )
            '''))
            
            table_exists = result.fetchone()[0]
            
            if not table_exists:
                logger.info("stock_realtime_quote表不存在，创建新表...")
                
                # 创建新表
                session.execute(text('''
                    CREATE TABLE stock_realtime_quote (
                        code TEXT,
                        trade_date TEXT,
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
                        update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY(code, trade_date)
                    )
                '''))
                
                logger.info("✓ 成功创建stock_realtime_quote表")
                
            else:
                logger.info("stock_realtime_quote表已存在，检查是否需要迁移...")
                
                # 检查是否已有trade_date字段
                result = session.execute(text('''
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'stock_realtime_quote' 
                    AND column_name = 'trade_date'
                '''))
                
                has_trade_date = result.fetchone() is not None
                
                if not has_trade_date:
                    logger.info("需要添加trade_date字段...")
                    
                    # 备份现有数据
                    logger.info("备份现有数据...")
                    backup_data = session.execute(text('SELECT * FROM stock_realtime_quote')).fetchall()
                    logger.info(f"备份了 {len(backup_data)} 条数据")
                    
                    # 创建临时表
                    session.execute(text('''
                        CREATE TABLE stock_realtime_quote_temp AS 
                        SELECT * FROM stock_realtime_quote
                    '''))
                    
                    # 删除原表
                    session.execute(text('DROP TABLE stock_realtime_quote'))
                    
                    # 创建新表结构
                    session.execute(text('''
                        CREATE TABLE stock_realtime_quote (
                            code TEXT,
                            trade_date TEXT,
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
                            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY(code, trade_date)
                        )
                    '''))
                    
                    # 恢复数据，为每条记录添加当前日期作为trade_date
                    current_date = datetime.now().strftime('%Y-%m-%d')
                    logger.info(f"恢复数据，使用 {current_date} 作为交易日期...")
                    
                    for row in backup_data:
                        # 假设row的结构，根据实际情况调整
                        session.execute(text('''
                            INSERT INTO stock_realtime_quote (
                                code, trade_date, name, current_price, change_percent,
                                volume, amount, high, low, open, pre_close,
                                turnover_rate, pe_dynamic, total_market_value,
                                pb_ratio, circulating_market_value, update_time
                            ) VALUES (
                                :code, :trade_date, :name, :current_price, :change_percent,
                                :volume, :amount, :high, :low, :open, :pre_close,
                                :turnover_rate, :pe_dynamic, :total_market_value,
                                :pb_ratio, :circulating_market_value, :update_time
                            )
                        '''), {
                            'code': row[0], 'trade_date': current_date, 'name': row[1],
                            'current_price': row[2], 'change_percent': row[3],
                            'volume': row[4], 'amount': row[5], 'high': row[6],
                            'low': row[7], 'open': row[8], 'pre_close': row[9],
                            'turnover_rate': row[10], 'pe_dynamic': row[11],
                            'total_market_value': row[12], 'pb_ratio': row[13],
                            'circulating_market_value': row[14], 'update_time': row[15]
                        })
                    
                    # 删除临时表
                    session.execute(text('DROP TABLE stock_realtime_quote_temp'))
                    
                    logger.info("✓ 成功迁移表结构并恢复数据")
                    
                else:
                    logger.info("✓ trade_date字段已存在，无需迁移")
            
            # 创建索引
            logger.info("创建索引...")
            try:
                session.execute(text('''
                    CREATE INDEX IF NOT EXISTS idx_realtime_code_date 
                    ON stock_realtime_quote(code, trade_date)
                '''))
                logger.info("✓ 成功创建索引")
            except Exception as e:
                logger.warning(f"创建索引时出现警告: {e}")
            
            session.commit()
            logger.info("✓ 表结构迁移完成")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"迁移过程中发生异常: {e}")
            return False
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"迁移失败: {e}")
        return False

def main():
    """主函数"""
    logger = setup_logging()
    
    try:
        success = migrate_realtime_table()
        
        if success:
            logger.info("\n" + "="*60)
            logger.info("数据库迁移完成！")
            logger.info("="*60)
            
            logger.info("\n📋 迁移内容:")
            logger.info("1. 为stock_realtime_quote表添加trade_date字段")
            logger.info("2. 设置(code, trade_date)为主键")
            logger.info("3. 创建相应的索引")
            logger.info("4. 保留现有数据")
            
            logger.info("\n🚀 下一步:")
            logger.info("1. 运行实时数据采集器，数据会自动包含交易日期")
            logger.info("2. 运行历史换手率采集器，从实时数据表获取换手率")
            
        else:
            logger.error("迁移失败，请检查错误信息")
            
    except Exception as e:
        logger.error(f"主程序执行异常: {e}")

if __name__ == "__main__":
    main()
