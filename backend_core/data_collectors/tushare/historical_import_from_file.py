import tushare as ts
import pandas as pd
from typing import Optional, Dict, Any
from pathlib import Path
import logging
# 日志配置建议：如主入口未配置请加如下代码
# logging.basicConfig(filename='your_log_file.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', encoding='utf-8')
from .base import TushareCollector
import datetime
from backend_core.database.db import SessionLocal
from sqlalchemy import text
import re

class HistoricalQuoteImportFromFileCollector(TushareCollector):
    """历史行情数据采集器"""
    def _safe_value(self, val: Any) -> Optional[float]:
        return None if pd.isna(val) else float(val)
    def extract_code_from_ts_code(self, ts_code: str) -> str:
        return ts_code.split(".")[0] if ts_code else ""
    
    def collect_historical_quotes(self, date_str: str) -> bool:
        session = SessionLocal()  # 新建 session
        try:
            input_params = {'date': date_str}
            collect_date = datetime.date.today().isoformat()
            success_count = 0
            fail_count = 0
            fail_detail = []
            # 从本地文件采集历史行情数据
            file_path = Path(f'backend_core/data/daily_{date_str}.txt')
            if not file_path.exists():
                self.logger.error(f"历史行情数据文件不存在: {file_path}")
                return False
            # 兼容CSV和SQL两种格式
            use_sql_mode = False
            try:
                df = pd.read_csv(file_path, dtype=str)
                use_sql_mode = False
            except Exception as e:
                self.logger.warning(f"读取为CSV失败，尝试SQL模式: {e}")
                use_sql_mode = True
            if not use_sql_mode:
                self.logger.info("采集到 %d 条历史行情数据", len(df))
                row_iter = (row.to_dict() for _, row in df.iterrows())
            else:
                def parse_sql_line_to_dict(sql_line):
                    import re
                    import csv
                    try:
                        # 1. 提取字段名部分
                        field_match = re.search(r'\((.*?)\)\s*VALUES', sql_line, re.DOTALL)
                        value_match = re.search(r'VALUES\s*\((.*?)\)\s*;?$', sql_line, re.DOTALL)
                        if not field_match or not value_match:
                            self.logger.error(f"SQL解析失败: {sql_line}")
                            return None
                        fields_raw = field_match.group(1)
                        values_raw = value_match.group(1)
                        # 2. 字段名处理
                        fields = [f.strip().strip('`').strip() for f in fields_raw.split(',')]
                        # 3. 用csv模块分割值，支持带引号和逗号
                        try:
                            values = next(csv.reader([values_raw], quotechar="'", skipinitialspace=True))
                        except Exception as e:
                            self.logger.error(f"值分割失败: {values_raw}, 错误: {e}, SQL: {sql_line}")
                            return None
                        values = [v.strip().strip("'") for v in values]
                        if len(fields) != len(values):
                            self.logger.error(f"字段数与值数不一致，fields={fields}, values={values}, SQL: {sql_line}")
                            return None
                        row = dict(zip(fields, values))
                        # 兼容所有可能的 key 变体，全部转小写去空格
                        row_norm = {k.strip().lower(): v for k, v in row.items()}
                        # 兼容 ts_code 变体
                        if 'ts_code' not in row_norm:
                            for k in row_norm:
                                if 'ts_code' in k:
                                    row_norm['ts_code'] = row_norm[k]
                                    break
                        return row_norm
                    except Exception as e:
                        self.logger.error(f"parse_sql_line_to_dict 解析异常: {e}, SQL: {sql_line}")
                        return None
                with open(file_path, encoding='utf-8') as f:
                    sql_content = f.read()
                sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip().startswith('REPLACE INTO')]
                self.logger.info(f"采集到 {len(sql_statements)} 条历史行情SQL数据")
                row_iter = (parse_sql_line_to_dict(stmt) for stmt in sql_statements)
            try:
                for row in row_iter:
                    if not row:
                        continue
                    print(f"row keys: {list(row.keys())}")
                    self.logger.warning(f"row keys: {list(row.keys())}")
                    print(f"row: {row}")
                    self.logger.warning(f"row: {row}")
                    ts_code = row.get('ts_code') or row.get(' ts_code') or row.get('`ts_code`')
                    if not ts_code:
                        self.logger.error(f"row中找不到ts_code字段: {row}")
                        continue
                    code = self.extract_code_from_ts_code(ts_code)
                    try:
                        ts_code = ts_code
                        result = session.execute(
                            text('SELECT name FROM stock_basic_info WHERE code = :code'),
                            {'code': code}
                        ).fetchone()
                        name = result[0] if result and result[0] else ''
                        market = row.get('market', '')
                        total_share = None
                        try:
                            result_share = session.execute(
                                text('SELECT total_share FROM stock_basic_info WHERE code = :code'),
                                {'code': code}
                            ).fetchone()
                            if result_share and result_share[0]:
                                total_share = float(result_share[0])
                        except Exception as e:
                            self.logger.warning(f"获取总股本失败: {e}")
                            total_share = None
                        volume = self._safe_value(row.get('vol'))
                        pre_close = self._safe_value(row.get('pre_close'))
                        high = self._safe_value(row.get('high'))
                        low = self._safe_value(row.get('low'))
                        turnover_rate = None
                        if total_share and volume is not None and total_share > 0:
                            turnover_rate = volume / total_share * 100
                        amplitude = None
                        if pre_close and pre_close > 0 and high is not None and low is not None:
                            amplitude = (high - low) / pre_close * 100
                        data = {
                            'code': code,
                            'ts_code': ts_code,
                            'name': name,
                            'market': market,
                            'date': datetime.datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d"),
                            'collected_source': 'tushare',
                            'collected_date': datetime.datetime.now().isoformat(),
                            'open': self._safe_value(row.get('open')),
                            'high': high,
                            'low': low,
                            'close': self._safe_value(row.get('close')),
                            'volume': volume,
                            'amount': self._safe_value(row.get('amount')) * 1000 if self._safe_value(row.get('amount')) is not None else None,
                            'change_percent': self._safe_value(row.get('pct_chg')),
                            'pre_close': pre_close,
                            'change': self._safe_value(row.get('change')),
                            'turnover_rate': turnover_rate,
                            'amplitude': amplitude
                        }
                        max_retries = 3
                        retry_count = 0
                        while retry_count < max_retries:
                            try:
                                session.execute(text('''
                                    INSERT INTO stock_basic_info (code, name)
                                    VALUES (:code, :name)
                                    ON CONFLICT (code) DO NOTHING
                                '''), {'code': data['code'], 'name': data['name']})
                                session.execute(text('''
                                    INSERT INTO historical_quotes
                                    (code, ts_code, name, market, collected_source, collected_date, date, open, high, low, close, volume, amount, change_percent, pre_close, change, amplitude, turnover_rate)
                                    VALUES (:code, :ts_code, :name, :market, :collected_source, :collected_date, :date, :open, :high, :low, :close, :volume, :amount, :change_percent, :pre_close, :change, :amplitude, :turnover_rate)
                                    ON CONFLICT (code, date) DO UPDATE SET
                                        ts_code = EXCLUDED.ts_code,
                                        name = EXCLUDED.name,
                                        market = EXCLUDED.market,
                                        collected_source = EXCLUDED.collected_source,
                                        collected_date = EXCLUDED.collected_date,
                                        open = EXCLUDED.open,
                                        high = EXCLUDED.high,
                                        low = EXCLUDED.low,
                                        close = EXCLUDED.close,
                                        volume = EXCLUDED.volume,
                                        amount = EXCLUDED.amount,
                                        change_percent = EXCLUDED.change_percent,
                                        pre_close = EXCLUDED.pre_close,
                                        amplitude = EXCLUDED.amplitude,
                                        turnover_rate = EXCLUDED.turnover_rate,
                                        change = EXCLUDED.change
                                '''), data)
                                if success_count % 100 == 0:
                                    session.commit()
                                    self.logger.info(f"已处理 {success_count} 条记录，提交事务")
                                success_count += 1
                                break
                            except Exception as insert_error:
                                if "DeadlockDetected" in str(insert_error):
                                    retry_count += 1
                                    self.logger.warning(f"检测到死锁，第 {retry_count} 次重试: {insert_error}")
                                    session.rollback()
                                    import time
                                    time.sleep(0.1 * retry_count)
                                    continue
                                else:
                                    raise insert_error
                        if retry_count >= max_retries:
                            fail_count += 1
                            fail_detail.append(f"股票 {code} 插入失败，重试 {max_retries} 次后仍然死锁")
                            self.logger.error(f"股票 {code} 插入失败，重试 {max_retries} 次后仍然死锁")
                            continue
                    except Exception as row_e:
                        fail_count += 1
                        fail_detail.append(str(row_e))
                        self.logger.error(f"采集单条数据失败: {row_e}")
                        continue
            except Exception as e:
                self.logger.error(f"遍历历史行情数据时发生异常: {e}")
                import sys
                sys.exit(1)
            # 记录采集日志（汇总信息）
            session.execute(text('''
                INSERT INTO historical_collect_operation_logs 
                (operation_type, operation_desc, affected_rows, status, error_message)
                VALUES (:operation_type, :operation_desc, :affected_rows, :status, :error_message)
            '''), {
                'operation_type': 'historical_quote_collect',
                'operation_desc': f'采集日期: {collect_date}\n输入参数: {input_params}\n成功记录数: {success_count}\n失败记录数: {fail_count}',
                'affected_rows': success_count,
                'status': 'success' if fail_count == 0 else 'partial_success',
                'error_message': '\n'.join(fail_detail) if fail_count > 0 else None
            })
            session.commit()
            self.logger.info(f"全部历史行情数据采集并入库完成，成功: {success_count}，失败: {fail_count}")
            return True
        except Exception as e:
            error_msg = str(e)
            self.logger.error("采集或入库时出错: %s", error_msg, exc_info=True)
            try:
                session.execute(text('''
                    INSERT INTO historical_collect_operation_logs 
                    (operation_type, operation_desc, affected_rows, status, error_message)
                    VALUES (:operation_type, :operation_desc, :affected_rows, :status, :error_message)
                '''), {
                    'operation_type': 'historical_quote_collect',
                    'operation_desc': f'采集日期: {datetime.date.today().isoformat()}\n输入参数: {input_params if "input_params" in locals() else ""}',
                    'affected_rows': 0,
                    'status': 'error',
                    'error_message': error_msg
                })
                session.commit()
            except Exception as log_error:
                self.logger.error("记录错误日志失败: %s", str(log_error))
            return False
        finally:
            session.close()

