"""
AKShare历史换手率数据采集器（新方案）
从stock_realtime_quote表获取换手率数据，补充到historical_quotes表
"""

import pandas as pd
from typing import Optional, Dict, Any
from pathlib import Path
import logging
from datetime import datetime, timedelta
import time

from .base import AKShareCollector
from backend_core.database.db import SessionLocal
from sqlalchemy import text

class HistoricalTurnoverRateCollector(AKShareCollector):
    """历史换手率数据采集器（从实时数据表获取）"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化采集器
        
        Args:
            config: 配置字典，如果为None则使用默认配置
        """
        super().__init__(config)
        self.db_file = Path(self.config.get('db_file', 'database/stock_analysis.db'))
        
    def _get_turnover_rate_from_realtime(self, code: str, trade_date: str) -> Optional[float]:
        """
        从实时数据表获取指定股票和日期的换手率
        
        Args:
            code: 股票代码
            trade_date: 交易日期 (YYYY-MM-DD)
            
        Returns:
            Optional[float]: 换手率数据，如果获取失败则返回None
        """
        try:
            session = SessionLocal()
            
            # 查询实时数据表中的换手率
            result = session.execute(text('''
                SELECT turnover_rate 
                FROM stock_realtime_quote 
                WHERE code = :code AND trade_date = :trade_date
            '''), {'code': code, 'trade_date': trade_date})
            
            row = result.fetchone()
            if row and row[0] is not None:
                return float(row[0])
            
            return None
            
        except Exception as e:
            self.logger.error(f"从实时数据表获取股票 {code} 在 {trade_date} 的换手率失败: {e}")
            return None
        finally:
            session.close()
    
    def collect_turnover_rate_for_date(self, date_str: str) -> bool:
        """
        为指定日期采集所有股票的历史换手率数据
        
        Args:
            date_str: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            bool: 是否成功
        """
        try:
            self.logger.info(f"开始采集 {date_str} 的历史换手率数据...")
            
            session = SessionLocal()
            try:
                # 查询该日期已有的股票数据，但缺少换手率
                result = session.execute(text('''
                    SELECT DISTINCT code, name 
                    FROM historical_quotes 
                    WHERE date = :date AND (turnover_rate IS NULL OR turnover_rate = 0)
                '''), {'date': date_str})
                
                stocks_to_update = result.fetchall()
                
                if not stocks_to_update:
                    self.logger.info(f"{date_str} 的所有股票换手率数据已完整，无需更新")
                    return True
                
                self.logger.info(f"需要更新换手率数据的股票数量: {len(stocks_to_update)}")
                
                success_count = 0
                fail_count = 0
                
                for stock in stocks_to_update:
                    code = stock[0]
                    name = stock[1]
                    
                    try:
                        # 从实时数据表获取换手率
                        turnover_rate = self._get_turnover_rate_from_realtime(code, date_str)
                        
                        if turnover_rate is not None:
                            # 更新数据库中的换手率
                            update_result = session.execute(text('''
                                UPDATE historical_quotes 
                                SET turnover_rate = :turnover_rate 
                                WHERE code = :code AND date = :date
                            '''), {
                                'turnover_rate': turnover_rate,
                                'code': code,
                                'date': date_str
                            })
                            
                            if update_result.rowcount > 0:
                                success_count += 1
                                self.logger.debug(f"成功更新股票 {code}({name}) 在 {date_str} 的换手率: {turnover_rate}")
                            else:
                                fail_count += 1
                                self.logger.warning(f"更新股票 {code}({name}) 换手率失败，未找到匹配记录")
                        else:
                            fail_count += 1
                            self.logger.warning(f"股票 {code}({name}) 在 {date_str} 的换手率数据在实时表中不存在")
                            
                    except Exception as e:
                        fail_count += 1
                        self.logger.error(f"处理股票 {code}({name}) 换手率数据时发生异常: {e}")
                    
                    # 添加延迟，避免请求过于频繁
                    time.sleep(0.01)
                
                session.commit()
                self.logger.info(f"{date_str} 换手率数据采集完成，成功: {success_count}, 失败: {fail_count}")
                
                return True
                
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"采集 {date_str} 历史换手率数据时发生异常: {e}")
            return False
    
    def collect_turnover_rate_for_period(self, start_date: str, end_date: str) -> bool:
        """
        为指定时间段采集历史换手率数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            bool: 是否成功
        """
        try:
            self.logger.info(f"开始采集 {start_date} 到 {end_date} 的历史换手率数据...")
            
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            current_dt = start_dt
            total_success = 0
            total_fail = 0
            
            while current_dt <= end_dt:
                current_date_str = current_dt.strftime('%Y-%m-%d')
                
                # 跳过周末
                if current_dt.weekday() < 5:  # 0-4 表示周一到周五
                    if self.collect_turnover_rate_for_date(current_date_str):
                        total_success += 1
                    else:
                        total_fail += 1
                
                current_dt += timedelta(days=1)
                
                # 添加延迟，避免请求过于频繁
                time.sleep(0.1)
            
            self.logger.info(f"时间段 {start_date} 到 {end_date} 换手率数据采集完成，成功日期: {total_success}, 失败日期: {total_fail}")
            return total_fail == 0
            
        except Exception as e:
            self.logger.error(f"采集时间段 {start_date} 到 {end_date} 历史换手率数据时发生异常: {e}")
            return False
    
    def collect_missing_turnover_rate(self, days_back: int = 30) -> bool:
        """
        采集最近N天缺失的换手率数据
        
        Args:
            days_back: 往前追溯的天数
            
        Returns:
            bool: 是否成功
        """
        try:
            self.logger.info(f"开始采集最近 {days_back} 天缺失的换手率数据...")
            
            # 使用真实的过去日期，避免使用未来日期
            end_date = datetime.now()
            # 确保结束日期是过去的工作日
            while end_date.weekday() >= 5:  # 跳过周末
                end_date -= timedelta(days=1)
            
            # 如果系统时间异常（未来日期），使用固定的过去日期
            if end_date.year > 2024:
                self.logger.warning("检测到系统时间异常，使用固定的过去日期范围")
                end_date = datetime(2024, 8, 20)  # 使用2024年8月20日作为结束日期
            
            start_date = end_date - timedelta(days=days_back)
            
            self.logger.info(f"采集日期范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
            
            # 验证日期范围是否有效
            if start_date >= end_date:
                self.logger.error("日期范围无效，开始日期必须早于结束日期")
                return False
            
            return self.collect_turnover_rate_for_period(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
        except Exception as e:
            self.logger.error(f"采集缺失换手率数据时发生异常: {e}")
            return False
    
    def run(self):
        """运行采集器"""
        try:
            self.logger.info("历史换手率数据采集器启动...")
            
            # 默认采集最近30天缺失的数据
            success = self.collect_missing_turnover_rate(30)
            
            if success:
                self.logger.info("历史换手率数据采集完成")
            else:
                self.logger.warning("历史换手率数据采集部分失败")
                
        except Exception as e:
            self.logger.error(f"历史换手率数据采集器运行异常: {e}")
        finally:
            self.logger.info("历史换手率数据采集器退出")


if __name__ == "__main__":
    # 测试代码
    collector = HistoricalTurnoverRateCollector()
    collector.run()
