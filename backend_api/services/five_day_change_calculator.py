#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5天升跌%计算服务
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Optional
import logging

from models import HistoricalQuotes

logger = logging.getLogger(__name__)

class FiveDayChangeCalculator:
    """5天升跌%计算器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_single_stock(self, stock_code: str) -> bool:
        """
        计算单只股票的5天升跌%
        
        Args:
            stock_code: 股票代码
            
        Returns:
            bool: 计算是否成功
        """
        try:
            logger.info(f"开始计算股票 {stock_code} 的5天升跌%")
            
            # 获取股票的历史数据，按日期排序
            quotes = self.db.query(HistoricalQuotes).filter(
                HistoricalQuotes.code == stock_code
            ).order_by(HistoricalQuotes.date).all()
            
            if len(quotes) < 6:
                logger.warning(f"股票 {stock_code} 数据不足5天，无法计算")
                return False
            
            # 从第6天开始计算5天升跌%
            updated_count = 0
            for i in range(5, len(quotes)):
                current_quote = quotes[i]
                prev_quote = quotes[i-5]  # 5天前的数据
                
                if current_quote.close and prev_quote.close and prev_quote.close > 0:
                    five_day_change = ((current_quote.close - prev_quote.close) / prev_quote.close) * 100
                    current_quote.five_day_change_percent = round(five_day_change, 2)
                    updated_count += 1
            
            self.db.commit()
            logger.info(f"股票 {stock_code} 的5天升跌%计算完成，更新了 {updated_count} 条记录")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"计算股票 {stock_code} 的5天升跌%失败: {e}")
            return False
    
    def calculate_multiple_stocks(self, stock_codes: List[str]) -> Dict[str, bool]:
        """
        计算多只股票的5天升跌%
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            Dict[str, bool]: 每只股票的计算结果
        """
        results = {}
        for stock_code in stock_codes:
            results[stock_code] = self.calculate_single_stock(stock_code)
        return results
    
    def calculate_all_stocks(self) -> Dict[str, int]:
        """
        计算所有股票的5天升跌%
        
        Returns:
            Dict[str, int]: 计算统计结果
        """
        try:
            # 获取所有股票代码
            stock_codes = self.db.query(HistoricalQuotes.code).distinct().all()
            stock_codes = [code[0] for code in stock_codes]
            
            logger.info(f"开始批量计算 {len(stock_codes)} 只股票的5天升跌%")
            
            success_count = 0
            failed_count = 0
            
            for stock_code in stock_codes:
                if self.calculate_single_stock(stock_code):
                    success_count += 1
                else:
                    failed_count += 1
                
                # 每处理10只股票输出一次进度
                if (success_count + failed_count) % 10 == 0:
                    logger.info(f"进度: {success_count + failed_count}/{len(stock_codes)}")
            
            logger.info(f"批量计算完成，成功: {success_count}，失败: {failed_count}")
            
            return {
                "total": len(stock_codes),
                "success": success_count,
                "failed": failed_count
            }
            
        except Exception as e:
            logger.error(f"批量计算失败: {e}")
            return {"total": 0, "success": 0, "failed": 0}
    
    def calculate_by_date_range(self, stock_code: str, start_date: str, end_date: str) -> bool:
        """
        计算指定日期范围内的5天升跌%
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            bool: 计算是否成功
        """
        try:
            logger.info(f"计算股票 {stock_code} 在 {start_date} 到 {end_date} 期间的5天升跌%")
            
            # 获取指定日期范围的历史数据
            quotes = self.db.query(HistoricalQuotes).filter(
                HistoricalQuotes.code == stock_code,
                HistoricalQuotes.date >= start_date,
                HistoricalQuotes.date <= end_date
            ).order_by(HistoricalQuotes.date).all()
            
            if len(quotes) < 6:
                logger.warning(f"股票 {stock_code} 在指定日期范围内数据不足5天")
                return False
            
            # 计算5天升跌%
            updated_count = 0
            for i in range(5, len(quotes)):
                current_quote = quotes[i]
                prev_quote = quotes[i-5]
                
                if current_quote.close and prev_quote.close and prev_quote.close > 0:
                    five_day_change = ((current_quote.close - prev_quote.close) / prev_quote.close) * 100
                    current_quote.five_day_change_percent = round(five_day_change, 2)
                    updated_count += 1
            
            self.db.commit()
            logger.info(f"股票 {stock_code} 在指定日期范围内的5天升跌%计算完成，更新了 {updated_count} 条记录")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"计算股票 {stock_code} 在指定日期范围内的5天升跌%失败: {e}")
            return False
    
    def get_calculation_status(self, stock_code: str) -> Dict[str, any]:
        """
        获取股票的5天升跌%计算状态
        
        Args:
            stock_code: 股票代码
            
        Returns:
            Dict: 计算状态信息
        """
        try:
            # 获取股票的总记录数和已计算记录数
            total_count = self.db.query(HistoricalQuotes).filter(
                HistoricalQuotes.code == stock_code
            ).count()
            
            calculated_count = self.db.query(HistoricalQuotes).filter(
                HistoricalQuotes.code == stock_code,
                HistoricalQuotes.five_day_change_percent.isnot(None)
            ).count()
            
            # 获取最新的计算记录
            latest_calculated = self.db.query(HistoricalQuotes).filter(
                HistoricalQuotes.code == stock_code,
                HistoricalQuotes.five_day_change_percent.isnot(None)
            ).order_by(HistoricalQuotes.date.desc()).first()
            
            return {
                "stock_code": stock_code,
                "total_records": total_count,
                "calculated_records": calculated_count,
                "calculation_rate": round(calculated_count / total_count * 100, 2) if total_count > 0 else 0,
                "latest_calculated_date": latest_calculated.date if latest_calculated else None,
                "latest_five_day_change": latest_calculated.five_day_change_percent if latest_calculated else None
            }
            
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 的计算状态失败: {e}")
            return {"stock_code": stock_code, "error": str(e)}
    
    def validate_calculation(self, stock_code: str, date: str) -> Dict[str, any]:
        """
        验证指定日期的5天升跌%计算是否正确
        
        Args:
            stock_code: 股票代码
            date: 日期 (YYYY-MM-DD)
            
        Returns:
            Dict: 验证结果
        """
        try:
            # 获取指定日期的记录
            current_quote = self.db.query(HistoricalQuotes).filter(
                HistoricalQuotes.code == stock_code,
                HistoricalQuotes.date == date
            ).first()
            
            if not current_quote:
                return {"valid": False, "error": "指定日期的记录不存在"}
            
            if current_quote.five_day_change_percent is None:
                return {"valid": False, "error": "该日期的5天升跌%未计算"}
            
            # 获取5天前的记录
            from datetime import datetime, timedelta
            current_date = datetime.strptime(date, "%Y-%m-%d").date()
            
            # 查找5天前的记录（考虑交易日）
            prev_quotes = self.db.query(HistoricalQuotes).filter(
                HistoricalQuotes.code == stock_code,
                HistoricalQuotes.date < current_date
            ).order_by(HistoricalQuotes.date.desc()).limit(10).all()
            
            # 找到第5个交易日
            if len(prev_quotes) < 5:
                return {"valid": False, "error": "历史数据不足5天"}
            
            prev_quote = prev_quotes[4]  # 第5个交易日
            
            # 手动计算验证
            if prev_quote.close and prev_quote.close > 0:
                expected_change = ((current_quote.close - prev_quote.close) / prev_quote.close) * 100
                expected_change = round(expected_change, 2)
                
                is_valid = abs(current_quote.five_day_change_percent - expected_change) < 0.01
                
                return {
                    "valid": is_valid,
                    "current_value": current_quote.five_day_change_percent,
                    "expected_value": expected_change,
                    "difference": round(current_quote.five_day_change_percent - expected_change, 4),
                    "current_close": current_quote.close,
                    "prev_close": prev_quote.close,
                    "prev_date": prev_quote.date
                }
            else:
                return {"valid": False, "error": "5天前的收盘价无效"}
                
        except Exception as e:
            logger.error(f"验证股票 {stock_code} 在 {date} 的5天升跌%失败: {e}")
            return {"valid": False, "error": str(e)}
