"""
测试脚本：从tushare历史采集接口获取2025-12-10的全量数据，
然后遍历数据，取ts_code字段数值中小数点前的值作为code，
更新stock_basic_info表中market字段，market字段的值取自于ts_code字段数值的最后两位。
"""
import tushare as ts
import pandas as pd
from backend_core.database.db import SessionLocal
from sqlalchemy import text
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

def extract_code_from_ts_code(ts_code: str) -> str:
    """
    从ts_code中提取code（小数点前的部分）
    例如: "000001.SZ" -> "000001"
    """
    if not ts_code:
        return ""
    return ts_code.split(".")[0] if "." in ts_code else ts_code

def extract_market_from_ts_code(ts_code: str) -> str:
    """
    从ts_code中提取market（小数点后的部分，即最后两位）
    例如: "000001.SZ" -> "SZ", "600000.SH" -> "SH"
    """
    if not ts_code:
        return ""
    if "." in ts_code:
        return ts_code.split(".")[1]
    return ""

def update_stock_basic_info_market():
    """
    从tushare历史采集接口获取2025-12-10的全量数据，
    然后更新stock_basic_info表中的market字段
    """
    # 设置tushare token
    ts.set_token('9701deb356e76d8d9918d797aff060ce90bd1a24339866c02444014f')
    pro = ts.pro_api()
    
    # 目标日期：2025-12-10
    date_str = "20251210"
    
    logger.info(f"开始从tushare获取 {date_str} 的历史行情数据...")
    
    try:
        # 获取历史行情数据
        df = pro.daily(trade_date=date_str)
        logger.info(f"成功获取 {len(df)} 条历史行情数据")
        
        if df.empty:
            logger.warning("获取的数据为空")
            return
        
        # 打印前几条数据用于验证
        logger.info(f"数据列名: {list(df.columns)}")
        if len(df) > 0:
            logger.info(f"前3条数据示例:")
            print(df.head(3))
        
        # 连接数据库
        session = SessionLocal()
        
        # 检查stock_basic_info表是否有market字段，如果没有则添加
        try:
            # 尝试查询market字段
            session.execute(text("SELECT market FROM stock_basic_info LIMIT 1"))
            logger.info("stock_basic_info表已存在market字段")
        except Exception as e:
            # 如果字段不存在，添加market字段
            logger.info("stock_basic_info表不存在market字段，正在添加...")
            try:
                session.execute(text("""
                    ALTER TABLE stock_basic_info 
                    ADD COLUMN market TEXT
                """))
                session.commit()
                logger.info("成功添加market字段")
            except Exception as add_error:
                logger.error(f"添加market字段失败: {add_error}")
                session.rollback()
                # 如果是PostgreSQL，使用DO块
                try:
                    session.execute(text("""
                        DO $$ 
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_name='stock_basic_info' 
                                AND column_name='market'
                            ) THEN
                                ALTER TABLE stock_basic_info ADD COLUMN market TEXT;
                            END IF;
                        END $$;
                    """))
                    session.commit()
                    logger.info("成功添加market字段（使用PostgreSQL语法）")
                except Exception as pg_error:
                    logger.error(f"使用PostgreSQL语法添加market字段也失败: {pg_error}")
                    session.rollback()
        
        # 统计变量
        success_count = 0
        fail_count = 0
        not_found_count = 0
        
        # 遍历数据，更新market字段
        logger.info("开始遍历数据并更新market字段...")
        for idx, row in df.iterrows():
            try:
                ts_code = row.get('ts_code', '')
                if not ts_code:
                    logger.warning(f"第 {idx+1} 行数据没有ts_code字段，跳过")
                    fail_count += 1
                    continue
                
                # 提取code和market
                code = extract_code_from_ts_code(ts_code)
                market = extract_market_from_ts_code(ts_code)
                
                if not code:
                    logger.warning(f"无法从ts_code '{ts_code}' 提取code，跳过")
                    fail_count += 1
                    continue
                
                if not market:
                    logger.warning(f"无法从ts_code '{ts_code}' 提取market，跳过")
                    fail_count += 1
                    continue
                
                # 获取股票名称（如果有的话）
                stock_name = row.get('name', '') or ''
                
                # 更新stock_basic_info表中的market字段
                try:
                    # 先尝试更新现有记录
                    result = session.execute(
                        text("""
                            UPDATE stock_basic_info 
                            SET market = :market 
                            WHERE code = :code
                        """),
                        {'code': code, 'market': market}
                    )
                    
                    if result.rowcount > 0:
                        success_count += 1
                        if success_count % 100 == 0:
                            logger.info(f"已更新 {success_count} 条记录，当前处理: {code} -> {market}")
                    else:
                        # 如果记录不存在，尝试插入新记录
                        try:
                            # 使用INSERT ... ON CONFLICT DO UPDATE语法
                            session.execute(
                                text("""
                                    INSERT INTO stock_basic_info (code, name, market)
                                    VALUES (:code, :name, :market)
                                    ON CONFLICT (code) DO UPDATE SET market = EXCLUDED.market
                                """),
                                {'code': code, 'name': stock_name if stock_name else code, 'market': market}
                            )
                            success_count += 1
                            logger.debug(f"插入新记录: {code} -> {market} (name: {stock_name if stock_name else code})")
                        except Exception as insert_error:
                            logger.warning(f"股票代码 {code} 在stock_basic_info表中不存在，且插入失败: {insert_error}")
                            not_found_count += 1
                        
                except Exception as update_error:
                    logger.error(f"更新股票代码 {code} 的market字段失败: {update_error}")
                    fail_count += 1
                    session.rollback()
                    continue
                
                # 每100条记录提交一次
                if success_count % 100 == 0 and success_count > 0:
                    session.commit()
                    logger.info(f"已提交 {success_count} 条更新")
                    
            except Exception as row_error:
                logger.error(f"处理第 {idx+1} 行数据时出错: {row_error}")
                fail_count += 1
                continue
        
        # 最后提交剩余的更新
        session.commit()
        
        logger.info("=" * 60)
        logger.info("更新完成！")
        logger.info(f"成功更新: {success_count} 条")
        logger.info(f"未找到记录: {not_found_count} 条")
        logger.info(f"失败: {fail_count} 条")
        logger.info(f"总计处理: {len(df)} 条")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"获取或处理数据时出错: {e}", exc_info=True)
        raise
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    update_stock_basic_info_market()

