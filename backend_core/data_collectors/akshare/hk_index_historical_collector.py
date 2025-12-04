"""
港股指数历史行情数据采集器
每日休市后，将当天的实时行情数据转存到历史行情表
"""
import logging
from datetime import datetime
from pathlib import Path
from backend_core.config.config import DATA_COLLECTORS
from backend_core.database.db import SessionLocal
from sqlalchemy import text

class HKIndexHistoricalCollector:
    """港股指数历史行情数据采集器"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = DATA_COLLECTORS['akshare']['db_file']
        self.db_file = Path(db_path)
        self.logger = logging.getLogger('HKIndexHistoricalCollector')
        # 确保数据库目录存在
        self.db_file.parent.mkdir(parents=True, exist_ok=True)

    def collect_daily_to_historical(self, trade_date=None):
        """
        将指定日期的实时行情数据转存到历史行情表
        
        Args:
            trade_date: 交易日期，格式：YYYY-MM-DD，默认为当天
            
        Returns:
            dict: 包含成功和失败数量的字典
        """
        session = None
        try:
            session = SessionLocal()
            
            # 如果没有指定日期，使用当天日期
            if trade_date is None:
                trade_date = datetime.now().strftime('%Y-%m-%d')
            
            self.logger.info(f'开始采集港股指数历史行情数据，日期: {trade_date}')
            
            # 1. 查询指定日期的实时行情数据
            query_sql = text('''
                SELECT 
                    code, 
                    name, 
                    trade_date as date,
                    open, 
                    high, 
                    low, 
                    price as close,
                    pre_close,
                    volume, 
                    amount,
                    change,
                    pct_chg,
                    update_time
                FROM hk_index_realtime_quotes
                WHERE trade_date = :trade_date
                ORDER BY code
            ''')
            
            result = session.execute(query_sql, {'trade_date': trade_date})
            realtime_data = result.fetchall()
            
            if not realtime_data:
                self.logger.warning(f'未找到日期 {trade_date} 的实时行情数据')
                return {
                    'success': 0,
                    'failed': 0,
                    'skipped': 0,
                    'message': f'未找到日期 {trade_date} 的实时行情数据'
                }
            
            self.logger.info(f'查询到 {len(realtime_data)} 条实时行情数据')
            
            # 2. 转存到历史行情表
            success_count = 0
            failed_count = 0
            skipped_count = 0
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            for row in realtime_data:
                try:
                    # 使用 ON CONFLICT 实现 upsert
                    insert_sql = text('''
                        INSERT INTO hk_index_historical_quotes (
                            code, name, date, open, high, low, close,
                            volume, amount, change, pct_chg,
                            collected_source, collected_date
                        ) VALUES (
                            :code, :name, :date, :open, :high, :low, :close,
                            :volume, :amount, :change, :pct_chg,
                            :collected_source, :collected_date
                        )
                        ON CONFLICT (code, date) DO UPDATE SET
                            name = EXCLUDED.name,
                            open = EXCLUDED.open,
                            high = EXCLUDED.high,
                            low = EXCLUDED.low,
                            close = EXCLUDED.close,
                            volume = EXCLUDED.volume,
                            amount = EXCLUDED.amount,
                            change = EXCLUDED.change,
                            pct_chg = EXCLUDED.pct_chg,
                            collected_source = EXCLUDED.collected_source,
                            collected_date = EXCLUDED.collected_date
                    ''')
                    
                    session.execute(insert_sql, {
                        'code': row.code,
                        'name': row.name,
                        'date': row.date,
                        'open': row.open,
                        'high': row.high,
                        'low': row.low,
                        'close': row.close,
                        'volume': row.volume,
                        'amount': row.amount,
                        'change': row.change,
                        'pct_chg': row.pct_chg,
                        'collected_source': 'realtime_quotes',
                        'collected_date': current_time
                    })
                    success_count += 1
                    
                except Exception as e:
                    self.logger.error(f"转存指数 {row.code} 失败: {str(e)}")
                    failed_count += 1
                    continue
            
            # 3. 记录操作日志
            try:
                log_sql = text('''
                    INSERT INTO hk_index_collect_operation_logs 
                    (operation_type, operation_desc, affected_rows, status, error_message, created_at)
                    VALUES (
                        :operation_type, :operation_desc, :affected_rows, :status, :error_message, CURRENT_TIMESTAMP
                    )
                ''')
                
                session.execute(log_sql, {
                    'operation_type': 'hk_index_historical_collect',
                    'operation_desc': f'转存日期 {trade_date} 的实时行情到历史行情表',
                    'affected_rows': success_count,
                    'status': 'success' if failed_count == 0 else 'partial_success',
                    'error_message': f'失败{failed_count}条' if failed_count > 0 else None
                })
                
                session.commit()
                
                self.logger.info(f'港股指数历史行情数据采集完成: 成功{success_count}条, 失败{failed_count}条')
                
                return {
                    'success': success_count,
                    'failed': failed_count,
                    'skipped': skipped_count,
                    'trade_date': trade_date,
                    'message': f'成功转存{success_count}条历史行情数据'
                }
                
            except Exception as log_error:
                self.logger.error(f"记录操作日志失败: {str(log_error)}")
                session.rollback()
                raise
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"采集历史行情数据时出错: {error_msg}", exc_info=True)
            
            # 记录错误日志
            try:
                if session is not None:
                    session.rollback()
                    error_log_sql = text('''
                        INSERT INTO hk_index_collect_operation_logs 
                        (operation_type, operation_desc, affected_rows, status, error_message, created_at)
                        VALUES (
                            :operation_type, :operation_desc, :affected_rows, :status, :error_message, CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    session.execute(error_log_sql, {
                        'operation_type': 'hk_index_historical_collect',
                        'operation_desc': f'转存日期 {trade_date} 的历史行情数据失败',
                        'affected_rows': 0,
                        'status': 'error',
                        'error_message': error_msg[:500]
                    })
                    session.commit()
            except Exception as log_error:
                self.logger.error(f"记录错误日志失败: {str(log_error)}")
            finally:
                if session is not None:
                    session.close()
            
            return {
                'success': 0,
                'failed': 0,
                'skipped': 0,
                'error': error_msg,
                'message': f'采集失败: {error_msg}'
            }

    def collect_date_range(self, start_date, end_date):
        """
        批量采集指定日期范围的历史行情数据
        
        Args:
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            
        Returns:
            dict: 包含总体统计信息的字典
        """
        from datetime import datetime, timedelta
        
        self.logger.info(f'开始批量采集历史行情数据: {start_date} 至 {end_date}')
        
        total_success = 0
        total_failed = 0
        total_skipped = 0
        processed_dates = []
        
        # 解析日期
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current_date <= end_date_obj:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # 跳过周末
            if current_date.weekday() in (5, 6):
                self.logger.info(f'跳过周末: {date_str}')
                current_date += timedelta(days=1)
                continue
            
            # 采集当天数据
            result = self.collect_daily_to_historical(date_str)
            
            total_success += result.get('success', 0)
            total_failed += result.get('failed', 0)
            total_skipped += result.get('skipped', 0)
            processed_dates.append(date_str)
            
            # 移动到下一天
            current_date += timedelta(days=1)
        
        self.logger.info(f'批量采集完成: 处理{len(processed_dates)}个交易日, 成功{total_success}条, 失败{total_failed}条')
        
        return {
            'total_success': total_success,
            'total_failed': total_failed,
            'total_skipped': total_skipped,
            'processed_dates': processed_dates,
            'message': f'批量采集完成: 成功{total_success}条, 失败{total_failed}条'
        }


if __name__ == '__main__':
    # 测试采集器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    collector = HKIndexHistoricalCollector()
    
    # 测试采集当天数据
    print("=" * 60)
    print("测试采集当天历史行情数据")
    print("=" * 60)
    
    result = collector.collect_daily_to_historical()
    print(f"\n结果: {result}")
    
    if result.get('success', 0) > 0:
        print(f"\n✓ 成功转存 {result['success']} 条历史行情数据")
    else:
        print(f"\n✗ 采集失败: {result.get('message', '未知错误')}")
