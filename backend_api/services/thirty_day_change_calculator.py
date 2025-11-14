#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
30天涨跌%计算服务
"""

import logging
from typing import Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from models import HistoricalQuotes

logger = logging.getLogger(__name__)


class ThirtyDayChangeCalculator:
    """30天涨跌%计算器"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_single_stock(self, stock_code: str) -> bool:
        """计算单只股票的30天涨跌%"""
        try:
            logger.info("开始计算股票 %s 的30天涨跌%%", stock_code)

            quotes = (
                self.db.query(HistoricalQuotes)
                .filter(HistoricalQuotes.code == stock_code)
                .order_by(HistoricalQuotes.date)
                .all()
            )

            if len(quotes) < 31:
                logger.warning("股票 %s 数据不足30天，无法计算", stock_code)
                return False

            updated_count = 0
            for i in range(30, len(quotes)):
                current_quote = quotes[i]
                prev_quote = quotes[i - 30]

                if current_quote.close and prev_quote.close and prev_quote.close > 0:
                    thirty_day_change = ((current_quote.close - prev_quote.close) / prev_quote.close) * 100
                    current_quote.thirty_day_change_percent = round(thirty_day_change, 2)
                    updated_count += 1

            self.db.commit()
            logger.info("股票 %s 的30天涨跌%%计算完成，更新了 %d 条记录", stock_code, updated_count)
            return True

        except Exception as e:
            self.db.rollback()
            logger.error("计算股票 %s 的30天涨跌%%失败: %s", stock_code, e)
            return False

    def calculate_multiple_stocks(self, stock_codes: List[str]) -> Dict[str, bool]:
        """计算多只股票的30天涨跌%"""
        results: Dict[str, bool] = {}
        for stock_code in stock_codes:
            results[stock_code] = self.calculate_single_stock(stock_code)
        return results

    def calculate_all_stocks(self) -> Dict[str, int]:
        """计算所有股票的30天涨跌%"""
        try:
            stock_codes = [code[0] for code in self.db.query(HistoricalQuotes.code).distinct().all()]
            logger.info("开始批量计算 %d 只股票的30天涨跌%%", len(stock_codes))

            success_count = 0
            failed_count = 0

            for stock_code in stock_codes:
                if self.calculate_single_stock(stock_code):
                    success_count += 1
                else:
                    failed_count += 1

                if (success_count + failed_count) % 10 == 0:
                    logger.info("进度: %d/%d", success_count + failed_count, len(stock_codes))

            logger.info("批量计算完成，成功: %d，失败: %d", success_count, failed_count)
            return {"total": len(stock_codes), "success": success_count, "failed": failed_count}

        except Exception as e:
            logger.error("批量计算失败: %s", e)
            return {"total": 0, "success": 0, "failed": 0}

    def calculate_by_date_range(self, stock_code: str, start_date: str, end_date: str) -> bool:
        """计算指定日期范围内的30天涨跌%"""
        try:
            logger.info("计算股票 %s 在 %s 到 %s 期间的30天涨跌%%", stock_code, start_date, end_date)

            quotes = (
                self.db.query(HistoricalQuotes)
                .filter(
                    HistoricalQuotes.code == stock_code,
                    HistoricalQuotes.date >= start_date,
                    HistoricalQuotes.date <= end_date,
                )
                .order_by(HistoricalQuotes.date)
                .all()
            )

            if len(quotes) < 31:
                logger.warning("股票 %s 在指定日期范围内数据不足30天", stock_code)
                return False

            updated_count = 0
            for i in range(30, len(quotes)):
                current_quote = quotes[i]
                prev_quote = quotes[i - 30]

                if current_quote.close and prev_quote.close and prev_quote.close > 0:
                    thirty_day_change = ((current_quote.close - prev_quote.close) / prev_quote.close) * 100
                    current_quote.thirty_day_change_percent = round(thirty_day_change, 2)
                    updated_count += 1

            self.db.commit()
            logger.info("股票 %s 在指定日期范围内的30天涨跌%%计算完成，更新了 %d 条记录", stock_code, updated_count)
            return True

        except Exception as e:
            self.db.rollback()
            logger.error("计算股票 %s 在指定日期范围内的30天涨跌%%失败: %s", stock_code, e)
            return False

    def get_calculation_status(self, stock_code: str) -> Dict[str, Optional[float]]:
        """获取股票的30天涨跌%计算状态"""
        try:
            total_count = (
                self.db.query(HistoricalQuotes)
                .filter(HistoricalQuotes.code == stock_code)
                .count()
            )

            calculated_count = (
                self.db.query(HistoricalQuotes)
                .filter(
                    HistoricalQuotes.code == stock_code,
                    HistoricalQuotes.thirty_day_change_percent.isnot(None),
                )
                .count()
            )

            latest_calculated = (
                self.db.query(HistoricalQuotes)
                .filter(
                    HistoricalQuotes.code == stock_code,
                    HistoricalQuotes.thirty_day_change_percent.isnot(None),
                )
                .order_by(HistoricalQuotes.date.desc())
                .first()
            )

            return {
                "stock_code": stock_code,
                "total_records": total_count,
                "calculated_records": calculated_count,
                "calculation_rate": round(calculated_count / total_count * 100, 2) if total_count > 0 else 0,
                "latest_calculated_date": latest_calculated.date if latest_calculated else None,
                "latest_thirty_day_change": latest_calculated.thirty_day_change_percent if latest_calculated else None,
            }

        except Exception as e:
            logger.error("获取股票 %s 的30天涨跌%%计算状态失败: %s", stock_code, e)
            return {"stock_code": stock_code, "error": str(e)}

    def validate_calculation(self, stock_code: str, date: str) -> Dict[str, Optional[float]]:
        """验证指定日期的30天涨跌%计算是否正确"""
        try:
            current_quote = (
                self.db.query(HistoricalQuotes)
                .filter(HistoricalQuotes.code == stock_code, HistoricalQuotes.date == date)
                .first()
            )

            if not current_quote:
                return {"valid": False, "error": "指定日期的记录不存在"}

            if current_quote.thirty_day_change_percent is None:
                return {"valid": False, "error": "该日期的30天涨跌%未计算"}

            prev_quotes = (
                self.db.query(HistoricalQuotes)
                .filter(HistoricalQuotes.code == stock_code, HistoricalQuotes.date < date)
                .order_by(HistoricalQuotes.date.desc())
                .limit(40)
                .all()
            )

            if len(prev_quotes) < 30:
                return {"valid": False, "error": "历史数据不足30天"}

            prev_quote = prev_quotes[29]

            if prev_quote.close and prev_quote.close > 0:
                expected_change = ((current_quote.close - prev_quote.close) / prev_quote.close) * 100
                expected_change = round(expected_change, 2)
                is_valid = abs(current_quote.thirty_day_change_percent - expected_change) < 0.01

                return {
                    "valid": is_valid,
                    "current_value": current_quote.thirty_day_change_percent,
                    "expected_value": expected_change,
                    "difference": round(current_quote.thirty_day_change_percent - expected_change, 4),
                    "current_close": current_quote.close,
                    "prev_close": prev_quote.close,
                    "prev_date": prev_quote.date,
                }

            return {"valid": False, "error": "30天前的收盘价无效"}

        except Exception as e:
            logger.error("验证股票 %s 在 %s 的30天涨跌%%失败: %s", stock_code, date, e)
            return {"valid": False, "error": str(e)}

