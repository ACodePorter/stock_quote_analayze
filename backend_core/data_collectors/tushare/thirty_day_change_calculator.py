#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
30日涨跌幅计算服务
用于在历史行情数据采集后自动计算30日涨跌幅
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import text

logger = logging.getLogger(__name__)


class ThirtyDayChangeCalculator:
    """30日涨跌幅计算器"""

    def __init__(self, session):
        self.session = session

    def calculate_for_date(self, target_date: str) -> Dict[str, any]:
        """
        为指定日期的所有股票计算30日涨跌幅

        Args:
            target_date: 目标日期 (YYYY-MM-DD)

        Returns:
            Dict: 计算结果统计
        """
        try:
            logger.info("开始为日期 %s 计算30日涨跌幅", target_date)

            stocks = self._get_stocks_for_date(target_date)
            if not stocks:
                logger.info("日期 %s 没有需要计算30日涨跌幅的股票", target_date)
                return {"total": 0, "success": 0, "failed": 0, "details": []}

            success_count = 0
            failed_count = 0
            failed_details: List[str] = []

            for stock_code in stocks:
                try:
                    if self._calculate_single_stock_thirty_day_change(stock_code, target_date):
                        success_count += 1
                        logger.debug("股票 %s 在 %s 的30日涨跌幅计算成功", stock_code, target_date)
                    else:
                        failed_count += 1
                        failed_details.append(f"股票 {stock_code}: 数据不足或计算失败")
                        logger.warning("股票 %s 在 %s 的30日涨跌幅计算失败", stock_code, target_date)
                except Exception as e:
                    failed_count += 1
                    failed_details.append(f"股票 {stock_code}: {str(e)}")
                    logger.error("股票 %s 在 %s 的30日涨跌幅计算异常: %s", stock_code, target_date, e)

            result = {
                "total": len(stocks),
                "success": success_count,
                "failed": failed_count,
                "details": failed_details,
                "date": target_date,
            }

            logger.info(
                "日期 %s 的30日涨跌幅计算完成: 总计 %d, 成功 %d, 失败 %d",
                target_date,
                len(stocks),
                success_count,
                failed_count,
            )
            return result

        except Exception as e:
            logger.error("为日期 %s 计算30日涨跌幅时发生异常: %s", target_date, e)
            return {"total": 0, "success": 0, "failed": 1, "details": [str(e)], "date": target_date}

    def _get_stocks_for_date(self, target_date: str) -> List[str]:
        """
        获取指定日期需要计算30日涨跌幅的股票代码列表
        """
        try:
            result = self.session.execute(
                text(
                    """
                SELECT DISTINCT code
                FROM historical_quotes
                WHERE date = :target_date
                AND thirty_day_change_percent IS NULL
                ORDER BY code
                """
                ),
                {"target_date": target_date},
            )

            stocks = [row[0] for row in result.fetchall()]
            logger.debug("日期 %s 需要计算30日涨跌幅的股票数量: %d", target_date, len(stocks))
            return stocks

        except Exception as e:
            logger.error("获取日期 %s 的股票列表失败: %s", target_date, e)
            return []

    def _calculate_single_stock_thirty_day_change(self, stock_code: str, target_date: str) -> bool:
        """
        计算单只股票在指定日期的30日涨跌幅
        """
        try:
            result = self.session.execute(
                text(
                    """
                SELECT date, close
                FROM historical_quotes
                WHERE code = :stock_code
                AND date <= :target_date
                ORDER BY date ASC
                """
                ),
                {"stock_code": stock_code, "target_date": target_date},
            )

            quotes = result.fetchall()
            if len(quotes) < 31:
                logger.debug("股票 %s 在 %s 的历史数据不足31天，无法计算30日涨跌幅", stock_code, target_date)
                return False

            target_index = None
            for index, quote in enumerate(quotes):
                if quote[0] == target_date:
                    target_index = index
                    break

            if target_index is None or target_index < 30:
                logger.debug("股票 %s 在 %s 的数据位置不满足计算条件", stock_code, target_date)
                return False

            current_quote = quotes[target_index]
            prev_quote = quotes[target_index - 30]

            if not current_quote[1] or not prev_quote[1] or prev_quote[1] <= 0:
                logger.debug("股票 %s 在 %s 的收盘价数据无效", stock_code, target_date)
                return False

            thirty_day_change = ((current_quote[1] - prev_quote[1]) / prev_quote[1]) * 100
            thirty_day_change = round(thirty_day_change, 2)

            self.session.execute(
                text(
                    """
                UPDATE historical_quotes
                SET thirty_day_change_percent = :thirty_day_change
                WHERE code = :stock_code AND date = :target_date
                """
                ),
                {
                    "thirty_day_change": thirty_day_change,
                    "stock_code": stock_code,
                    "target_date": target_date,
                },
            )

            return True

        except Exception as e:
            logger.error("计算股票 %s 在 %s 的30日涨跌幅失败: %s", stock_code, target_date, e)
            return False

    def calculate_batch_for_date_range(self, start_date: str, end_date: str) -> Dict[str, any]:
        """
        批量计算指定日期范围内所有股票的30日涨跌幅
        """
        try:
            logger.info("开始批量计算日期范围 %s 到 %s 的30日涨跌幅", start_date, end_date)

            dates = self._get_date_range(start_date, end_date)

            total_success = 0
            total_failed = 0
            all_details: List[str] = []

            for date in dates:
                result = self.calculate_for_date(date)
                total_success += result["success"]
                total_failed += result["failed"]
                all_details.extend(result["details"])

            return {
                "start_date": start_date,
                "end_date": end_date,
                "total_dates": len(dates),
                "total_success": total_success,
                "total_failed": total_failed,
                "details": all_details,
            }

        except Exception as e:
            logger.error("批量计算日期范围 %s 到 %s 的30日涨跌幅失败: %s", start_date, end_date, e)
            return {
                "start_date": start_date,
                "end_date": end_date,
                "total_dates": 0,
                "total_success": 0,
                "total_failed": 1,
                "details": [str(e)],
            }

    def _get_date_range(self, start_date: str, end_date: str) -> List[str]:
        """获取日期范围内的所有日期列表"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            dates: List[str] = []
            current = start
            while current <= end:
                dates.append(current.strftime("%Y-%m-%d"))
                current += timedelta(days=1)

            return dates

        except Exception as e:
            logger.error("生成日期范围失败: %s", e)
            return []

    def get_calculation_status(self, date: str) -> Dict[str, any]:
        """获取指定日期的30日涨跌幅计算状态"""
        try:
            result = self.session.execute(
                text(
                    """
                SELECT
                    COUNT(*) as total_records,
                    COUNT(thirty_day_change_percent) as calculated_records,
                    COUNT(*) - COUNT(thirty_day_change_percent) as pending_records,
                    ROUND(COUNT(thirty_day_change_percent) * 100.0 / COUNT(*), 2) as completion_rate
                FROM historical_quotes
                WHERE date = :date
                """
                ),
                {"date": date},
            )

            row = result.fetchone()
            if row:
                return {
                    "date": date,
                    "total_records": row[0],
                    "calculated_records": row[1],
                    "pending_records": row[2],
                    "completion_rate": row[3],
                }

            return {
                "date": date,
                "total_records": 0,
                "calculated_records": 0,
                "pending_records": 0,
                "completion_rate": 0,
            }

        except Exception as e:
            logger.error("获取日期 %s 的30日涨跌幅计算状态失败: %s", date, e)
            return {
                "date": date,
                "total_records": 0,
                "calculated_records": 0,
                "pending_records": 0,
                "completion_rate": 0,
                "error": str(e),
            }

