#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展涨跌幅计算服务
用于在历史行情数据采集后自动计算5日、10日、60日涨跌幅
"""

import logging
from typing import List, Dict, Optional, Tuple
from sqlalchemy import text
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

class ExtendedChangeCalculator:
    """扩展涨跌幅计算器 - 支持5日、10日、60日涨跌幅"""
    
    def __init__(self, session):
        self.session = session
        self.periods = [5, 10, 60]  # 支持的涨跌幅周期
    
    def calculate_for_date(self, target_date: str) -> Dict[str, any]:
        """
        为指定日期的所有股票计算5日、10日、60日涨跌幅
        
        Args:
            target_date: 目标日期 (YYYY-MM-DD)
            
        Returns:
            Dict: 计算结果统计
        """
        try:
            logger.info(f"开始为日期 {target_date} 计算扩展涨跌幅（5日、10日、60日）")
            
            # 获取该日期所有需要计算的股票
            stocks = self._get_stocks_for_date(target_date)
            if not stocks:
                logger.info(f"日期 {target_date} 没有需要计算扩展涨跌幅的股票")
                return {"total": 0, "success": 0, "failed": 0, "details": []}
            
            success_count = 0
            failed_count = 0
            failed_details = []
            
            for stock_code in stocks:
                try:
                    if self._calculate_single_stock_extended_change(stock_code, target_date):
                        success_count += 1
                        logger.debug(f"股票 {stock_code} 在 {target_date} 的扩展涨跌幅计算成功")
                    else:
                        failed_count += 1
                        failed_details.append(f"股票 {stock_code}: 数据不足或计算失败")
                        logger.warning(f"股票 {stock_code} 在 {target_date} 的扩展涨跌幅计算失败")
                except Exception as e:
                    failed_count += 1
                    failed_details.append(f"股票 {stock_code}: {str(e)}")
                    logger.error(f"股票 {stock_code} 在 {target_date} 的扩展涨跌幅计算异常: {e}")
            
            result = {
                "total": len(stocks),
                "success": success_count,
                "failed": failed_count,
                "details": failed_details,
                "date": target_date
            }
            
            logger.info(f"日期 {target_date} 的扩展涨跌幅计算完成: 总计 {len(stocks)}, 成功 {success_count}, 失败 {failed_count}")
            return result
            
        except Exception as e:
            logger.error(f"为日期 {target_date} 计算扩展涨跌幅时发生异常: {e}")
            return {"total": 0, "success": 0, "failed": 1, "details": [str(e)], "date": target_date}
    
    def _get_stocks_for_date(self, target_date: str) -> List[str]:
        """
        获取指定日期需要计算扩展涨跌幅的股票代码列表
        
        Args:
            target_date: 目标日期 (YYYY-MM-DD)
            
        Returns:
            List[str]: 股票代码列表
        """
        try:
            # 查询该日期有数据但任一涨跌幅字段为空的股票
            result = self.session.execute(text("""
                SELECT DISTINCT code 
                FROM historical_quotes 
                WHERE date = :target_date 
                AND (five_day_change_percent IS NULL 
                     OR ten_day_change_percent IS NULL 
                     OR sixty_day_change_percent IS NULL)
                ORDER BY code
            """), {"target_date": target_date})
            
            stocks = [row[0] for row in result.fetchall()]
            logger.debug(f"日期 {target_date} 需要计算扩展涨跌幅的股票数量: {len(stocks)}")
            return stocks
            
        except Exception as e:
            logger.error(f"获取日期 {target_date} 的股票列表失败: {e}")
            return []
    
    def _calculate_single_stock_extended_change(self, stock_code: str, target_date: str) -> bool:
        """
        计算单只股票在指定日期的扩展涨跌幅（5日、10日、60日）
        
        Args:
            stock_code: 股票代码
            target_date: 目标日期 (YYYY-MM-DD)
            
        Returns:
            bool: 计算是否成功
        """
        try:
            # 获取该股票在目标日期及之前的历史数据（至少需要61天数据）
            result = self.session.execute(text("""
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
            
            if len(quotes) < 61:
                logger.debug(f"股票 {stock_code} 在 {target_date} 的历史数据不足61天，无法计算60日涨跌幅")
                return False
            
            # 找到目标日期在数据中的位置
            target_index = None
            for i, quote in enumerate(quotes):
                if quote[0] == target_date:
                    target_index = i
                    break
            
            if target_index is None:
                logger.debug(f"股票 {stock_code} 在 {target_date} 的数据位置不满足计算条件")
                return False
            
            # 计算各期涨跌幅
            current_quote = quotes[target_index]
            current_close = current_quote[1]
            
            if not current_close or current_close <= 0:
                logger.debug(f"股票 {stock_code} 在 {target_date} 的收盘价数据无效")
                return False
            
            change_results = {}
            
            # 计算5日涨跌幅
            if target_index >= 5:
                prev_5_quote = quotes[target_index - 5]
                if prev_5_quote[1] and prev_5_quote[1] > 0:
                    five_day_change = ((current_close - prev_5_quote[1]) / prev_5_quote[1]) * 100
                    change_results['five_day_change_percent'] = round(five_day_change, 2)
                else:
                    change_results['five_day_change_percent'] = None
            else:
                change_results['five_day_change_percent'] = None
            
            # 计算10日涨跌幅
            if target_index >= 10:
                prev_10_quote = quotes[target_index - 10]
                if prev_10_quote[1] and prev_10_quote[1] > 0:
                    ten_day_change = ((current_close - prev_10_quote[1]) / prev_10_quote[1]) * 100
                    change_results['ten_day_change_percent'] = round(ten_day_change, 2)
                else:
                    change_results['ten_day_change_percent'] = None
            else:
                change_results['ten_day_change_percent'] = None
            
            # 计算60日涨跌幅
            if target_index >= 60:
                prev_60_quote = quotes[target_index - 60]
                if prev_60_quote[1] and prev_60_quote[1] > 0:
                    sixty_day_change = ((current_close - prev_60_quote[1]) / prev_60_quote[1]) * 100
                    change_results['sixty_day_change_percent'] = round(sixty_day_change, 2)
                else:
                    change_results['sixty_day_change_percent'] = None
            else:
                change_results['sixty_day_change_percent'] = None
            
            # 更新数据库
            update_sql = """
                UPDATE historical_quotes 
                SET five_day_change_percent = :five_day_change_percent,
                    ten_day_change_percent = :ten_day_change_percent,
                    sixty_day_change_percent = :sixty_day_change_percent
                WHERE code = :stock_code AND date = :target_date
            """
            
            self.session.execute(text(update_sql), {
                "five_day_change_percent": change_results['five_day_change_percent'],
                "ten_day_change_percent": change_results['ten_day_change_percent'],
                "sixty_day_change_percent": change_results['sixty_day_change_percent'],
                "stock_code": stock_code,
                "target_date": target_date
            })
            
            logger.debug(f"股票 {stock_code} 在 {target_date} 的扩展涨跌幅计算完成: 5日={change_results['five_day_change_percent']}%, 10日={change_results['ten_day_change_percent']}%, 60日={change_results['sixty_day_change_percent']}%")
            return True
            
        except Exception as e:
            logger.error(f"计算股票 {stock_code} 在 {target_date} 的扩展涨跌幅失败: {e}")
            return False
    
    def calculate_batch_for_date_range(self, start_date: str, end_date: str) -> Dict[str, any]:
        """
        批量计算指定日期范围内所有股票的扩展涨跌幅
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            Dict: 批量计算结果统计
        """
        try:
            logger.info(f"开始批量计算日期范围 {start_date} 到 {end_date} 的扩展涨跌幅")
            
            # 获取日期范围内的所有日期
            dates = self._get_date_range(start_date, end_date)
            
            total_success = 0
            total_failed = 0
            all_details = []
            
            for date in dates:
                result = self.calculate_for_date(date)
                total_success += result["success"]
                total_failed += result["failed"]
                all_details.extend(result["details"])
            
            batch_result = {
                "start_date": start_date,
                "end_date": end_date,
                "total_dates": len(dates),
                "total_success": total_success,
                "total_failed": total_failed,
                "details": all_details
            }
            
            logger.info(f"批量计算完成: 日期范围 {start_date} 到 {end_date}, 总计成功 {total_success}, 失败 {total_failed}")
            return batch_result
            
        except Exception as e:
            logger.error(f"批量计算日期范围 {start_date} 到 {end_date} 的扩展涨跌幅失败: {e}")
            return {
                "start_date": start_date,
                "end_date": end_date,
                "total_dates": 0,
                "total_success": 0,
                "total_failed": 1,
                "details": [str(e)]
            }
    
    def _get_date_range(self, start_date: str, end_date: str) -> List[str]:
        """
        获取日期范围内的所有日期列表
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            List[str]: 日期列表
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            dates = []
            current = start
            while current <= end:
                dates.append(current.strftime("%Y-%m-%d"))
                current += timedelta(days=1)
            
            return dates
            
        except Exception as e:
            logger.error(f"生成日期范围失败: {e}")
            return []
    
    def get_calculation_status(self, date: str) -> Dict[str, any]:
        """
        获取指定日期的扩展涨跌幅计算状态
        
        Args:
            date: 日期 (YYYY-MM-DD)
            
        Returns:
            Dict: 计算状态信息
        """
        try:
            result = self.session.execute(text("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(five_day_change_percent) as five_day_calculated,
                    COUNT(ten_day_change_percent) as ten_day_calculated,
                    COUNT(sixty_day_change_percent) as sixty_day_calculated,
                    COUNT(*) - COUNT(five_day_change_percent) as five_day_pending,
                    COUNT(*) - COUNT(ten_day_change_percent) as ten_day_pending,
                    COUNT(*) - COUNT(sixty_day_change_percent) as sixty_day_pending,
                    ROUND(COUNT(five_day_change_percent) * 100.0 / COUNT(*), 2) as five_day_completion_rate,
                    ROUND(COUNT(ten_day_change_percent) * 100.0 / COUNT(*), 2) as ten_day_completion_rate,
                    ROUND(COUNT(sixty_day_change_percent) * 100.0 / COUNT(*), 2) as sixty_day_completion_rate
                FROM historical_quotes 
                WHERE date = :date
            """), {"date": date})
            
            row = result.fetchone()
            if row:
                return {
                    "date": date,
                    "total_records": row[0],
                    "five_day": {
                        "calculated": row[1],
                        "pending": row[4],
                        "completion_rate": row[7]
                    },
                    "ten_day": {
                        "calculated": row[2],
                        "pending": row[5],
                        "completion_rate": row[8]
                    },
                    "sixty_day": {
                        "calculated": row[3],
                        "pending": row[6],
                        "completion_rate": row[9]
                    }
                }
            else:
                return {
                    "date": date,
                    "total_records": 0,
                    "five_day": {"calculated": 0, "pending": 0, "completion_rate": 0},
                    "ten_day": {"calculated": 0, "pending": 0, "completion_rate": 0},
                    "sixty_day": {"calculated": 0, "pending": 0, "completion_rate": 0}
                }
                
        except Exception as e:
            logger.error(f"获取日期 {date} 的计算状态失败: {e}")
            return {
                "date": date,
                "total_records": 0,
                "five_day": {"calculated": 0, "pending": 0, "completion_rate": 0},
                "ten_day": {"calculated": 0, "pending": 0, "completion_rate": 0},
                "sixty_day": {"calculated": 0, "pending": 0, "completion_rate": 0},
                "error": str(e)
            }
