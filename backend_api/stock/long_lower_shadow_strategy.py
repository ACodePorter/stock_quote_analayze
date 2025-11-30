"""
长下影阳线选股策略
独立策略文件

策略要求:
1. 下跌趋势: 当前价格 < 60日前价格
2. 长下影阳线: 最近7个交易日内出现
   - 收盘价 > 开盘价 (阳线)
   - 下影线长度 >= 实体长度的2倍
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class LongLowerShadowStrategy:
    """长下影阳线选股策略类"""
    
    @staticmethod
    def check_downtrend(historical_data: List[Dict], threshold: int = 60) -> bool:
        """
        检查是否处于下跌趋势
        
        Args:
            historical_data: 历史数据列表（倒序，最新在前）
            threshold: 检查的天数（默认60天）
        
        Returns:
            是否处于下跌趋势
        """
        if len(historical_data) < threshold:
            return False
        
        # 当前价格
        current_price = float(historical_data[0].get('close', 0))
        # 60日前价格
        price_60_days_ago = float(historical_data[threshold - 1].get('close', 0))
        
        if current_price <= 0 or price_60_days_ago <= 0:
            return False
        
        # 下跌趋势: 当前价格 < 60日前价格
        return current_price < price_60_days_ago
    
    @staticmethod
    def check_long_lower_shadow(day_data: Dict) -> Tuple[bool, Optional[Dict]]:
        """
        检查单日是否为长下影阳线
        
        Args:
            day_data: 单日数据
        
        Returns:
            (是否为长下影阳线, 形态信息)
        """
        open_price = float(day_data.get('open', 0))
        close_price = float(day_data.get('close', 0))
        high_price = float(day_data.get('high', 0))
        low_price = float(day_data.get('low', 0))
        
        # 检查数据有效性
        if open_price <= 0 or close_price <= 0 or high_price <= 0 or low_price <= 0:
            return False, None
        
        # 条件1: 阳线 (收盘价 > 开盘价)
        is_bullish = close_price > open_price
        if not is_bullish:
            return False, None
        
        # 计算实体长度
        body_length = abs(close_price - open_price)
        
        # 计算下影线长度
        lower_shadow = min(open_price, close_price) - low_price
        
        # 计算上影线长度
        upper_shadow = high_price - max(open_price, close_price)
        
        # 条件2: 下影线长度 >= 实体长度的2倍
        is_long_lower_shadow = lower_shadow >= body_length * 2
        
        if not is_long_lower_shadow:
            return False, None
        
        # 返回形态信息
        return True, {
            'date': day_data.get('date'),
            'open': open_price,
            'close': close_price,
            'high': high_price,
            'low': low_price,
            'body_length': body_length,
            'lower_shadow': lower_shadow,
            'upper_shadow': upper_shadow,
            'shadow_body_ratio': lower_shadow / body_length if body_length > 0 else 0
        }
    
    @staticmethod
    def check_long_lower_shadow_conditions(historical_data: List[Dict], 
                                           downtrend_days: int = 60,
                                           recent_days: int = 7) -> Tuple[bool, Optional[Dict]]:
        """
        检查长下影阳线策略条件
        
        策略要求:
        1. 下跌趋势: 当前价格 < 60日前价格
        2. 长下影阳线: 最近7个交易日内出现
        
        Args:
            historical_data: 历史数据列表（倒序，最新在前）
            downtrend_days: 下跌趋势判断天数（默认60天）
            recent_days: 检查长下影阳线的天数（默认7天）
        
        Returns:
            (是否满足条件, 策略信息)
        """
        # 需要至少60个交易日的数据
        if len(historical_data) < downtrend_days:
            return False, None
        
        # 条件1: 检查下跌趋势
        is_downtrend = LongLowerShadowStrategy.check_downtrend(historical_data, downtrend_days)
        if not is_downtrend:
            return False, None
        
        # 条件2: 检查最近7个交易日内是否有长下影阳线
        recent_data = historical_data[:recent_days]
        
        long_lower_shadow_found = False
        pattern_info = None
        
        for day_data in recent_data:
            is_pattern, info = LongLowerShadowStrategy.check_long_lower_shadow(day_data)
            if is_pattern:
                long_lower_shadow_found = True
                pattern_info = info
                break  # 找到第一个符合条件的就返回
        
        if not long_lower_shadow_found:
            return False, None
        
        # 计算下跌幅度
        current_price = float(historical_data[0].get('close', 0))
        price_60_days_ago = float(historical_data[downtrend_days - 1].get('close', 0))
        decline_ratio = (price_60_days_ago - current_price) / price_60_days_ago if price_60_days_ago > 0 else 0
        
        # 所有条件满足
        return True, {
            'pattern_date': pattern_info['date'],
            'pattern_open': pattern_info['open'],
            'pattern_close': pattern_info['close'],
            'pattern_high': pattern_info['high'],
            'pattern_low': pattern_info['low'],
            'body_length': pattern_info['body_length'],
            'lower_shadow': pattern_info['lower_shadow'],
            'upper_shadow': pattern_info['upper_shadow'],
            'shadow_body_ratio': pattern_info['shadow_body_ratio'],
            'current_price': current_price,
            'price_60_days_ago': price_60_days_ago,
            'decline_ratio': decline_ratio
        }
    
    @staticmethod
    def screening_long_lower_shadow_strategy(db: Session) -> List[Dict]:
        """
        长下影阳线选股策略主函数
        
        策略要求:
        1. 下跌趋势: 当前价格 < 60日前价格
        2. 长下影阳线: 最近7个交易日内出现
        
        Args:
            db: 数据库会话
        
        Returns:
            符合条件的股票列表
        """
        results = []
        
        try:
            # 1. 获取全部A股股票列表
            stocks_query = db.execute(text("""
                SELECT DISTINCT code, name 
                FROM stock_basic_info 
                WHERE LENGTH(code) = 6
                ORDER BY code
            """))
            
            stocks = stocks_query.fetchall()
            logger.info(f"找到 {len(stocks)} 只A股股票")
            
            # 2. 计算查询日期范围（至少需要60个交易日的数据）
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=100)  # 往前推100天以确保有足够数据
            
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            logger.info(f"查询日期范围: {start_date_str} 至 {end_date_str}")
            
            # 3. 对每只股票执行选股策略
            for idx, (code, name) in enumerate(stocks):
                if idx % 100 == 0:
                    logger.info(f"处理进度: {idx}/{len(stocks)}")
                
                try:
                    # 获取该股票的历史数据（倒序，最新在前）
                    history_query = db.execute(text("""
                        SELECT code, name, date, open, close, high, low, 
                               change_percent, volume, amount
                        FROM historical_quotes 
                        WHERE code = :code 
                        AND date >= :start_date 
                        AND date <= :end_date
                        ORDER BY date DESC
                    """), {
                        'code': str(code),
                        'start_date': start_date_str,
                        'end_date': end_date_str
                    })
                    
                    history_rows = history_query.fetchall()
                    
                    if len(history_rows) < 60:  # 至少需要60个交易日的数据
                        continue
                    
                    # 转换为字典列表
                    historical_data = []
                    for row in history_rows:
                        date_val = row[2]
                        if hasattr(date_val, 'strftime'):
                            date_str = date_val.strftime('%Y-%m-%d')
                        else:
                            date_str = str(date_val)
                        
                        historical_data.append({
                            'code': row[0],
                            'name': row[1],
                            'date': date_str,
                            'open': float(row[3]) if row[3] else 0.0,
                            'close': float(row[4]) if row[4] else 0.0,
                            'high': float(row[5]) if row[5] else 0.0,
                            'low': float(row[6]) if row[6] else 0.0,
                            'change_percent': float(row[7]) if row[7] else 0.0,
                            'volume': float(row[8]) if row[8] else 0.0,
                            'amount': float(row[9]) if row[9] else 0.0
                        })
                    
                    # 检查长下影阳线策略条件
                    is_valid, strategy_info = LongLowerShadowStrategy.check_long_lower_shadow_conditions(
                        historical_data, downtrend_days=60, recent_days=7
                    )
                    
                    if not is_valid or not strategy_info:
                        continue
                    
                    # 获取当前价格信息
                    current_data = historical_data[0] if historical_data else {}
                    current_price = float(current_data.get('close', 0))
                    current_change_percent = current_data.get('change_percent', 0)
                    
                    # 所有条件满足，加入结果列表
                    result_item = {
                        'code': str(code),
                        'name': name,
                        'current_price': round(current_price, 2),
                        'current_change_percent': round(current_change_percent, 2) if current_change_percent else 0,
                        'pattern_date': strategy_info['pattern_date'],
                        'pattern_close': round(strategy_info['pattern_close'], 2),
                        'lower_shadow': round(strategy_info['lower_shadow'], 2),
                        'body_length': round(strategy_info['body_length'], 2),
                        'shadow_body_ratio': round(strategy_info['shadow_body_ratio'], 2),
                        'decline_ratio': round(strategy_info['decline_ratio'], 4)
                    }
                    
                    results.append(result_item)
                    logger.info(f"找到符合条件的股票: {code} {name}")
                    
                except Exception as e:
                    logger.error(f"处理股票 {code} 时出错: {str(e)}")
                    try:
                        db.rollback()
                    except Exception as rollback_error:
                        logger.warning(f"回滚事务时出错: {str(rollback_error)}")
                    continue
            
            logger.info(f"长下影阳线选股策略执行完成，找到 {len(results)} 只符合条件的股票")
            
        except Exception as e:
            logger.error(f"长下影阳线选股策略执行失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        return results
