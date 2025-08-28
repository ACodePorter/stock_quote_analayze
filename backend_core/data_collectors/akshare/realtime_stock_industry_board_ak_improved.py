import akshare as ak
import traceback
from datetime import datetime
import sys
import os
from backend_core.config.config import DATA_COLLECTORS
from backend_core.database.db import SessionLocal
from sqlalchemy import text
import pandas as pd

class ImprovedRealtimeStockIndustryBoardCollector:
    def __init__(self):
        self.db_file = DATA_COLLECTORS['akshare']['db_file']
        self.table_name = 'industry_board_realtime_quotes'
        self.log_table = 'realtime_collect_operation_logs'

    def fetch_data(self):
        """获取行业板块数据，增加调试信息"""
        try:
            print("[采集] 开始调用 ak.stock_board_industry_name_em()...")
            df = ak.stock_board_industry_name_em()
            print(f"[采集] 成功获取数据，形状: {df.shape}")
            
            # 显示列名信息
            print(f"[采集] 列名: {list(df.columns)}")
            
            # 检查关键字段
            key_fields = ["领涨股", "领涨股涨跌幅", "领涨股代码"]
            for field in key_fields:
                if field in df.columns:
                    non_null_count = df[field].notna().sum()
                    total_count = len(df)
                    print(f"[采集] {field}: 存在，非空值 {non_null_count}/{total_count}")
                    
                    # 显示前几个非空值
                    if non_null_count > 0:
                        sample_values = df[df[field].notna()][field].head(3).tolist()
                        print(f"[采集] {field} 示例值: {sample_values}")
                else:
                    print(f"[采集] ❌ {field}: 字段不存在")
            
            # 显示前几行数据用于调试
            print(f"[采集] 前3行数据预览:")
            for i in range(min(3, len(df))):
                row = df.iloc[i]
                print(f"  行{i+1}: {row['板块名称']} - 领涨股: {row.get('领涨股', 'N/A')} ({row.get('领涨股代码', 'N/A')}) {row.get('领涨股涨跌幅', 'N/A')}%")
            
            return df
            
        except Exception as e:
            print(f"[采集] ❌ 获取数据失败: {e}")
            tb = traceback.format_exc()
            print(f"[采集] 错误详情:\n{tb}")
            return None

    def save_to_db(self, df):
        """保存数据到数据库，增加调试信息"""
        if df is None or len(df) == 0:
            print("[采集] ❌ 数据为空，跳过保存")
            return False, "数据为空"
            
        session = SessionLocal()
        try:
            print(f"[采集] 开始保存 {len(df)} 条数据到数据库...")
            
            # 字段映射：中文->英文
            col_map = {
                "板块代码": "board_code",
                "板块名称": "board_name",
                "最新价": "latest_price",
                "涨跌额": "change_amount",
                "涨跌幅": "change_percent",
                "总市值": "total_market_value",
                "成交量": "volume",
                "成交额": "amount",
                "换手率": "turnover_rate",
                "上涨家数": "up_count",
                "下跌家数": "down_count",
                "领涨股": "leading_stock_name",
                "领涨股涨跌幅": "leading_stock_change_percent",
                "领涨股代码": "leading_stock_code"
            }
            
            # 检查哪些字段在数据中存在
            available_fields = [k for k in col_map.keys() if k in df.columns]
            missing_fields = [k for k in col_map.keys() if k not in df.columns]
            
            print(f"[采集] 可用字段: {available_fields}")
            if missing_fields:
                print(f"[采集] ⚠️ 缺失字段: {missing_fields}")
            
            # 只保留映射字段
            now = datetime.now().replace(microsecond=0)
            keep_cols = [k for k in col_map.keys() if k in df.columns]
            df_filtered = df[keep_cols].rename(columns=col_map)
            df_filtered['update_time'] = now
            
            print(f"[采集] 最终保存字段: {list(df_filtered.columns)}")
            
            # 检查领涨股相关字段
            leading_stock_fields = ['leading_stock_name', 'leading_stock_change_percent', 'leading_stock_code']
            for field in leading_stock_fields:
                if field in df_filtered.columns:
                    non_null_count = df_filtered[field].notna().sum()
                    print(f"[采集] {field}: {non_null_count}/{len(df_filtered)} 非空")
                else:
                    print(f"[采集] ❌ {field}: 字段不存在")
            
            columns = list(df_filtered.columns)
            
            # 清空旧数据
            print(f"[采集] 清空旧数据...")
            session.execute(text(f"DELETE FROM {self.table_name}"))
            
            # 插入新数据
            print(f"[采集] 开始插入新数据...")
            inserted_count = 0
            for idx, row in df_filtered.iterrows():
                try:
                    value_dict = {}
                    for col in columns:
                        v = row[col]
                        if hasattr(v, 'item'):
                            v = v.item()
                        if str(type(v)).endswith("Timestamp'>"):
                            v = v.to_pydatetime().isoformat()
                        if col == 'update_time' and not isinstance(v, str):
                            v = v.isoformat()
                        value_dict[col] = v
                    
                    placeholders = ','.join([f':{col}' for col in columns])
                    col_names = ','.join([f'"{col}"' for col in columns])
                    
                    # 构造upsert SQL
                    update_set = ','.join([f'"{col}"=EXCLUDED."{col}"' for col in columns if col not in ('board_code','update_time')])
                    sql = f'INSERT INTO {self.table_name} ({col_names}) VALUES ({placeholders}) ON CONFLICT (board_code, update_time) DO UPDATE SET {update_set}'
                    
                    session.execute(text(sql), value_dict)
                    inserted_count += 1
                    
                    # 每100条显示一次进度
                    if inserted_count % 100 == 0:
                        print(f"[采集] 已插入 {inserted_count} 条数据...")
                        
                except Exception as row_error:
                    print(f"[采集] ❌ 插入第 {idx+1} 行数据失败: {row_error}")
                    print(f"[采集] 问题数据: {row.to_dict()}")
                    continue
            
            session.commit()
            print(f"[采集] ✅ 成功保存 {inserted_count} 条数据")
            return True, None
            
        except Exception as e:
            session.rollback()
            error_msg = f"保存数据失败: {e}"
            print(f"[采集] ❌ {error_msg}")
            tb = traceback.format_exc()
            print(f"[采集] 错误详情:\n{tb}")
            return False, error_msg
        finally:
            session.close()

    def write_log(self, operation_type, operation_desc, affected_rows, status, error_message=None):
        """写入操作日志"""
        session = SessionLocal()
        try:
            now = datetime.now().replace(microsecond=0)
            session.execute(text(f"INSERT INTO {self.log_table} (operation_type, operation_desc, affected_rows, status, error_message, created_at) VALUES (:operation_type, :operation_desc, :affected_rows, :status, :error_message, :created_at)"),
                           {'operation_type': operation_type, 'operation_desc': operation_desc, 'affected_rows': affected_rows, 'status': status, 'error_message': error_message or '', 'created_at': now})
            session.commit()
            print(f"[日志] ✅ 操作日志写入成功: {operation_type} - {status}")
        except Exception as e:
            print(f"[日志] ❌ 写入日志失败: {e}")
        finally:
            session.close()

    def run(self):
        """运行数据采集"""
        try:
            print("=" * 80)
            print("[采集] 🚀 开始采集行业板块实时行情...")
            print(f"[采集] ⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)
            
            # 获取数据
            df = self.fetch_data()
            if df is None:
                raise Exception("获取数据失败")
            
            print(f"[采集] 📊 获取到 {len(df)} 条数据")
            
            # 保存数据
            ok, err = self.save_to_db(df)
            if ok:
                print("[采集] ✅ 数据写入成功")
                self.write_log(
                    operation_type="industry_board_realtime",
                    operation_desc="采集行业板块实时行情",
                    affected_rows=len(df),
                    status="success",
                    error_message=None
                )
            else:
                print(f"[采集] ❌ 数据写入失败: {err}")
                self.write_log(
                    operation_type="industry_board_realtime",
                    operation_desc="采集行业板块实时行情",
                    affected_rows=0,
                    status="fail",
                    error_message=err
                )
                
        except Exception as e:
            tb = traceback.format_exc()
            error_msg = f"采集异常: {e}"
            print(f"[采集] ❌ {error_msg}")
            print(f"[采集] 错误详情:\n{tb}")
            self.write_log(
                operation_type="industry_board_realtime",
                operation_desc="采集行业板块实时行情",
                affected_rows=0,
                status="fail",
                error_message=error_msg + "\n" + tb
            )
        finally:
            print("=" * 80)
            print(f"[采集] 🏁 采集完成，结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)

if __name__ == '__main__':
    collector = ImprovedRealtimeStockIndustryBoardCollector()
    collector.run()
