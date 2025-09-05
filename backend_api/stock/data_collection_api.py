#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史数据采集API服务
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import akshare as ak
import pandas as pd
import time
import random

from backend_api.database import get_db
from backend_api.models import DataCollectionRequest, DataCollectionResponse, DataCollectionStatus
from sqlalchemy import text

router = APIRouter(prefix="/api/data-collection", tags=["数据采集"])

# 全局变量存储采集任务状态
collection_tasks = {}
task_lock = threading.Lock()
# 全局变量控制单任务执行
current_task_id = None
task_execution_lock = threading.Lock()

logger = logging.getLogger(__name__)

class AkshareDataCollector:
    """akshare数据采集器"""
    
    def __init__(self, db_session: Session):
        self.session = db_session
        self.collected_count = 0
        self.skipped_count = 0
        self.failed_count = 0
        self.failed_stocks = []
        
    def get_stock_list(self, only_uncompleted: bool = False) -> List[Dict[str, str]]:
        """从stock_basic_info表获取股票列表"""
        try:
            if only_uncompleted:
                # 只返回未完成全量采集的股票
                result = self.session.execute(text("""
                    SELECT code, name, full_collection_completed, full_collection_date
                    FROM stock_basic_info 
                    WHERE full_collection_completed = FALSE OR full_collection_completed IS NULL
                    ORDER BY code
                """))
            else:
                # 返回所有股票，包含全量采集状态
                result = self.session.execute(text("""
                    SELECT code, name, full_collection_completed, full_collection_date
                    FROM stock_basic_info 
                    ORDER BY code
                """))
            
            stocks = []
            for row in result.fetchall():
                stocks.append({
                    'code': str(row[0]),  # 确保code是字符串
                    'name': row[1] if row[1] else '',
                    'full_collection_completed': bool(row[2]) if row[2] is not None else False,
                    'full_collection_date': row[3].isoformat() if row[3] else None
                })
            
            logger.info(f"从数据库获取到 {len(stocks)} 只股票")
            return stocks
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []
    
    def check_existing_data(self, stock_code: str, start_date: str, end_date: str) -> List[str]:
        """检查指定股票在日期范围内已存在的数据日期"""
        try:
            result = self.session.execute(text("""
                SELECT date 
                FROM historical_quotes 
                WHERE code = :stock_code 
                AND date >= :start_date 
                AND date <= :end_date
                ORDER BY date
            """), {
                'stock_code': stock_code,
                'start_date': start_date,
                'end_date': end_date
            })
            
            existing_dates = [row[0] for row in result.fetchall()]
            return existing_dates
            
        except Exception as e:
            logger.error(f"检查股票 {stock_code} 已存在数据失败: {e}")
            return []
    
    def collect_single_stock_data(self, stock_code: str, stock_name: str, start_date: str, end_date: str) -> bool:
        """采集单只股票的历史数据"""
        try:
            # 检查已存在的数据
            existing_dates = self.check_existing_data(stock_code, start_date, end_date)
            if existing_dates:
                logger.debug(f"股票 {stock_code} 在 {start_date} 到 {end_date} 期间已有 {len(existing_dates)} 天数据")
            
            # 使用akshare获取历史数据
            logger.info(f"开始采集股票 {stock_code} 的历史数据...")
            
            # 添加重试机制
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # 使用akshare获取历史数据
                    # 日期格式为yyyymmdd，akshare要求start_date和end_date为"yyyymmdd"格式
                    df = ak.stock_zh_a_hist(
                        symbol=stock_code,
                        period='daily',
                        start_date=pd.to_datetime(start_date).strftime('%Y%m%d'),
                        end_date=pd.to_datetime(end_date).strftime('%Y%m%d'),
                        adjust=""  # 不复权
                    )
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2 + random.uniform(0, 1)
                        logger.warning(f"股票 {stock_code} 第 {attempt + 1} 次采集失败，{wait_time:.1f}秒后重试: {e}")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"股票 {stock_code} 采集失败，已重试 {max_retries} 次: {e}")
                        self.failed_count += 1
                        self.failed_stocks.append(f"{stock_code}: {str(e)}")
                        return False
            
            if df.empty:
                logger.warning(f"股票 {stock_code} 在指定日期范围内没有数据")
                return True
            
            logger.info(f"股票 {stock_code} 采集到 {len(df)} 条数据")
            
            # 处理数据并插入数据库
            success_count = 0
            skip_count = 0
            
            for _, row in df.iterrows():
                try:
                    # 转换日期格式
                    trade_date = pd.to_datetime(row['日期']).strftime('%Y-%m-%d')
                    
                    # 检查是否已存在
                    if trade_date in existing_dates:
                        skip_count += 1
                        continue
                    
                    # 准备插入数据
                    data = {
                        'code': stock_code,
                        'ts_code': f"{stock_code}.SZ" if stock_code.startswith('0') else f"{stock_code}.SH",
                        'name': stock_name,  # 从stock_basic_info表获取
                        'market': 'SZ' if stock_code.startswith('0') else 'SH',
                        'date': trade_date,
                        'open': float(row['开盘']) if pd.notna(row['开盘']) else None,
                        'high': float(row['最高']) if pd.notna(row['最高']) else None,
                        'low': float(row['最低']) if pd.notna(row['最低']) else None,
                        'close': float(row['收盘']) if pd.notna(row['收盘']) else None,
                        'pre_close': None,  # akshare没有提供前收盘价，设为None
                        'volume': float(row['成交量']) if pd.notna(row['成交量']) else None,
                        'amount': float(row['成交额']) if pd.notna(row['成交额']) else None,
                        'change_percent': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else None,
                        'change': float(row['涨跌额']) if pd.notna(row['涨跌额']) else None,
                        'amplitude': float(row['振幅']) if pd.notna(row['振幅']) else None,
                        'turnover_rate': float(row['换手率']) if pd.notna(row['换手率']) else None,
                        'collected_source': 'akshare',
                        'collected_date': datetime.now().isoformat()
                    }
                    
                    # 插入数据
                    self.session.execute(text("""
                        INSERT INTO historical_quotes
                        (code, ts_code, name, market, date, open, high, low, close, pre_close, 
                         volume, amount, change_percent, change, amplitude, turnover_rate, 
                         collected_source, collected_date)
                        VALUES (:code, :ts_code, :name, :market, :date, :open, :high, :low, :close, :pre_close,
                                :volume, :amount, :change_percent, :change, :amplitude, :turnover_rate,
                                :collected_source, :collected_date)
                    """), data)
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"处理股票 {stock_code} 日期 {trade_date} 数据时出错: {e}")
                    continue
            
            # 提交事务
            self.session.commit()
            
            self.collected_count += success_count
            self.skipped_count += skip_count
            
            logger.info(f"股票 {stock_code} 处理完成: 新增 {success_count} 条，跳过 {skip_count} 条")
            
            # 更新该股票的全量采集标志
            self._update_full_collection_flag(stock_code, start_date, end_date)
            
            # 添加随机延迟，避免请求过于频繁
            time.sleep(random.uniform(0.5, 1.5))
            
            return True
            
        except Exception as e:
            logger.error(f"采集股票 {stock_code} 历史数据失败: {e}")
            self.failed_count += 1
            self.failed_stocks.append(f"{stock_code}: {str(e)}")
            return False
    
    def _update_full_collection_flag(self, stock_code: str, start_date: str, end_date: str):
        """更新股票的全量采集标志"""
        try:
            # 更新全量采集标志
            self.session.execute(text("""
                UPDATE stock_basic_info 
                SET full_collection_completed = TRUE,
                    full_collection_date = CURRENT_TIMESTAMP,
                    full_collection_start_date = :start_date,
                    full_collection_end_date = :end_date
                WHERE code = :stock_code
            """), {
                'stock_code': stock_code,
                'start_date': start_date,
                'end_date': end_date
            })
            
            self.session.commit()
            logger.info(f"已更新股票 {stock_code} 的全量采集标志")
            
        except Exception as e:
            logger.error(f"更新股票 {stock_code} 全量采集标志失败: {e}")
            # 不抛出异常，避免影响主流程
    
    def collect_historical_data(self, start_date: str, end_date: str, stock_codes: Optional[List[str]] = None, full_collection_mode: bool = False) -> Dict[str, any]:
        """批量采集历史行情数据"""
        try:
            logger.info(f"开始批量采集历史行情数据: {start_date} 到 {end_date}")
            
            # 获取股票列表
            if stock_codes:
                stocks = []
                for code in stock_codes:
                    result = self.session.execute(text("""
                        SELECT code, name FROM stock_basic_info WHERE code = :code
                    """), {'code': code})
                    row = result.fetchone()
                    if row:
                        stocks.append({'code': str(row[0]), 'name': row[1] if row[1] else ''})
                    else:
                        logger.warning(f"股票代码 {code} 在stock_basic_info表中不存在")
            else:
                # 根据模式决定获取哪些股票
                if full_collection_mode:
                    # 全量采集模式：只获取未完成全量采集的股票
                    stocks = self.get_stock_list(only_uncompleted=True)
                    logger.info(f"全量采集模式：获取到 {len(stocks)} 只未完成全量采集的股票")
                else:
                    # 普通模式：获取所有股票
                    stocks = self.get_stock_list()
            
            if not stocks:
                logger.error("没有找到需要采集的股票")
                return {
                    'total': 0,
                    'success': 0,
                    'failed': 0,
                    'collected': 0,
                    'skipped': 0,
                    'failed_details': []
                }
            
            logger.info(f"准备采集 {len(stocks)} 只股票的历史数据")
            
            # 重置计数器
            self.collected_count = 0
            self.skipped_count = 0
            self.failed_count = 0
            self.failed_stocks = []
            
            # 批量采集
            success_count = 0
            for i, stock in enumerate(stocks, 1):
                logger.info(f"进度: {i}/{len(stocks)} - 采集股票 {stock['code']} ({stock['name']})")
                
                if self.collect_single_stock_data(stock['code'], stock['name'], start_date, end_date):
                    success_count += 1
                time.sleep(20)  # 每次采集后休眠20秒
                
                # 每处理10只股票输出一次进度
                if i % 10 == 0:
                    logger.info(f"已处理 {i}/{len(stocks)} 只股票，成功 {success_count} 只")
            
            # 记录采集日志
            self._log_collection_result(start_date, end_date, len(stocks), success_count)
            
            result = {
                'total': len(stocks),
                'success': success_count,
                'failed': self.failed_count,
                'collected': self.collected_count,
                'skipped': self.skipped_count,
                'failed_details': self.failed_stocks
            }
            
            logger.info(f"批量采集完成:")
            logger.info(f"  - 总计股票: {result['total']}")
            logger.info(f"  - 成功采集: {result['success']}")
            logger.info(f"  - 采集失败: {result['failed']}")
            logger.info(f"  - 新增数据: {result['collected']} 条")
            logger.info(f"  - 跳过数据: {result['skipped']} 条")
            
            return result
            
        except Exception as e:
            logger.error(f"批量采集历史数据失败: {e}")
            return {
                'total': 0,
                'success': 0,
                'failed': 1,
                'collected': 0,
                'skipped': 0,
                'failed_details': [str(e)]
            }
    
    def _log_collection_result(self, start_date: str, end_date: str, total_stocks: int, success_stocks: int):
        """记录采集结果到日志表"""
        try:
            self.session.execute(text("""
                INSERT INTO historical_collect_operation_logs 
                (operation_type, operation_desc, affected_rows, status, error_message)
                VALUES (:operation_type, :operation_desc, :affected_rows, :status, :error_message)
            """), {
                'operation_type': 'akshare_historical_collect',
                'operation_desc': f'采集日期范围: {start_date} 到 {end_date}\n总计股票: {total_stocks}\n成功采集: {success_stocks}\n新增数据: {self.collected_count}\n跳过数据: {self.skipped_count}',
                'affected_rows': self.collected_count,
                'status': 'success' if self.failed_count == 0 else 'partial_success',
                'error_message': '\n'.join(self.failed_stocks) if self.failed_stocks else None
            })
            self.session.commit()
            
        except Exception as e:
            logger.error(f"记录采集日志失败: {e}")

@router.post("/historical", response_model=DataCollectionResponse)
async def start_historical_collection(
    request: DataCollectionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """启动历史数据采集任务"""
    global current_task_id
    try:
        # 验证日期格式
        try:
            datetime.strptime(request.start_date, '%Y-%m-%d')
            datetime.strptime(request.end_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD 格式")
        
        # 检查是否有其他任务正在运行
        with task_execution_lock:
            if current_task_id is not None:
                raise HTTPException(status_code=400, detail="已有采集任务正在运行，请等待完成后再启动新任务")
        
        # 生成任务ID
        task_id = f"historical_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{threading.get_ident()}"
        
        # 初始化任务状态
        with task_lock:
            collection_tasks[task_id] = {
                "status": "running",
                "progress": 0,
                "total_stocks": 0,
                "processed_stocks": 0,
                "success_count": 0,
                "failed_count": 0,
                "collected_count": 0,
                "skipped_count": 0,
                "start_time": datetime.now(),
                "end_time": None,
                "error_message": None,
                "failed_details": []
            }
        
        # 设置当前任务ID
        with task_execution_lock:
            current_task_id = task_id
        
        # 启动后台任务
        background_tasks.add_task(
            run_historical_collection_task,
            task_id,
            request.start_date,
            request.end_date,
            request.stock_codes,
            request.test_mode,
            request.full_collection_mode
        )
        
        logger.info(f"启动历史数据采集任务: {task_id}")
        
        return DataCollectionResponse(
            task_id=task_id,
            status="started",
            message="历史数据采集任务已启动",
            start_date=request.start_date,
            end_date=request.end_date,
            stock_codes=request.stock_codes,
            test_mode=request.test_mode,
            full_collection_mode=request.full_collection_mode
        )
        
    except Exception as e:
        logger.error(f"启动历史数据采集任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动采集任务失败: {str(e)}")

def run_historical_collection_task(
    task_id: str,
    start_date: str,
    end_date: str,
    stock_codes: Optional[List[str]] = None,
    test_mode: bool = False,
    full_collection_mode: bool = False
):
    """运行历史数据采集任务（后台任务）"""
    global current_task_id
    try:
        logger.info(f"开始执行历史数据采集任务: {task_id}")
        
        # 创建数据库会话
        from backend_api.database import SessionLocal
        db = SessionLocal()
        
        try:
            # 创建采集器
            collector = AkshareDataCollector(db)
            
            # 获取股票列表
            if test_mode:
                logger.info("测试模式：只采集前5只股票")
                stocks = collector.get_stock_list()[:5]
                stock_codes = [stock['code'] for stock in stocks]
            
            # 更新任务状态
            with task_lock:
                if task_id in collection_tasks:
                    collection_tasks[task_id]["total_stocks"] = len(stock_codes) if stock_codes else len(collector.get_stock_list())
            
            # 执行采集
            result = collector.collect_historical_data(start_date, end_date, stock_codes, full_collection_mode)
            
            # 更新任务状态
            with task_lock:
                if task_id in collection_tasks:
                    collection_tasks[task_id].update({
                        "status": "completed",
                        "progress": 100,
                        "processed_stocks": result["total"],
                        "success_count": result["success"],
                        "failed_count": result["failed"],
                        "collected_count": result["collected"],
                        "skipped_count": result["skipped"],
                        "end_time": datetime.now(),
                        "failed_details": result["failed_details"]
                    })
            
            logger.info(f"历史数据采集任务完成: {task_id}")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"历史数据采集任务执行失败: {task_id}, 错误: {e}")
        
        # 更新任务状态为失败
        with task_lock:
            if task_id in collection_tasks:
                collection_tasks[task_id].update({
                    "status": "failed",
                    "end_time": datetime.now(),
                    "error_message": str(e)
                })
    finally:
        # 清除当前任务ID
        with task_execution_lock:
            if current_task_id == task_id:
                current_task_id = None
                logger.info(f"已清除当前任务ID: {task_id}")

@router.get("/status/{task_id}", response_model=DataCollectionStatus)
async def get_collection_status(task_id: str):
    """获取采集任务状态"""
    try:
        with task_lock:
            if task_id not in collection_tasks:
                raise HTTPException(status_code=404, detail="任务不存在")
            
            task_info = collection_tasks[task_id]
            
            # 计算进度
            progress = task_info["progress"]
            if task_info["total_stocks"] > 0:
                progress = min(100, int((task_info["processed_stocks"] / task_info["total_stocks"]) * 100))
            
            return DataCollectionStatus(
                task_id=task_id,
                status=task_info["status"],
                progress=progress,
                total_stocks=task_info["total_stocks"],
                processed_stocks=task_info["processed_stocks"],
                success_count=task_info["success_count"],
                failed_count=task_info["failed_count"],
                collected_count=task_info["collected_count"],
                skipped_count=task_info["skipped_count"],
                start_time=task_info["start_time"],
                end_time=task_info["end_time"],
                error_message=task_info["error_message"],
                failed_details=task_info["failed_details"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务状态失败: {task_id}, 错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")

@router.get("/tasks", response_model=List[DataCollectionStatus])
async def list_collection_tasks():
    """获取所有采集任务列表"""
    try:
        with task_lock:
            tasks = []
            for task_id, task_info in collection_tasks.items():
                # 计算进度
                progress = task_info["progress"]
                if task_info["total_stocks"] > 0:
                    progress = min(100, int((task_info["processed_stocks"] / task_info["total_stocks"]) * 100))
                
                tasks.append(DataCollectionStatus(
                    task_id=task_id,
                    status=task_info["status"],
                    progress=progress,
                    total_stocks=task_info["total_stocks"],
                    processed_stocks=task_info["processed_stocks"],
                    success_count=task_info["success_count"],
                    failed_count=task_info["failed_count"],
                    collected_count=task_info["collected_count"],
                    skipped_count=task_info["skipped_count"],
                    start_time=task_info["start_time"],
                    end_time=task_info["end_time"],
                    error_message=task_info["error_message"],
                    failed_details=task_info["failed_details"]
                ))
            
            # 按开始时间倒序排列
            tasks.sort(key=lambda x: x.start_time, reverse=True)
            
            return tasks
            
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")

@router.delete("/tasks/{task_id}")
async def cancel_collection_task(task_id: str):
    """取消采集任务"""
    try:
        with task_lock:
            if task_id not in collection_tasks:
                raise HTTPException(status_code=404, detail="任务不存在")
            
            task_info = collection_tasks[task_id]
            if task_info["status"] in ["completed", "failed"]:
                raise HTTPException(status_code=400, detail="任务已完成或失败，无法取消")
            
            # 标记任务为取消状态
            collection_tasks[task_id]["status"] = "cancelled"
            collection_tasks[task_id]["end_time"] = datetime.now()
            
            # 如果是当前运行的任务，清除当前任务ID
            with task_execution_lock:
                if current_task_id == task_id:
                    current_task_id = None
            
            logger.info(f"取消历史数据采集任务: {task_id}")
            
            return {"message": "任务已取消", "task_id": task_id}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消任务失败: {task_id}, 错误: {e}")
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")

@router.get("/stock-list")
async def get_stock_list(db: Session = Depends(get_db), only_uncompleted: bool = False):
    """获取股票列表"""
    try:
        collector = AkshareDataCollector(db)
        stocks = collector.get_stock_list(only_uncompleted=only_uncompleted)
        
        return {
            "total": len(stocks),
            "stocks": stocks[:100],  # 只返回前100只股票用于显示
            "only_uncompleted": only_uncompleted
        }
        
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取股票列表失败: {str(e)}")

@router.get("/current-task")
async def get_current_task():
    """获取当前运行的任务信息"""
    try:
        with task_execution_lock:
            if current_task_id is None:
                return {"current_task": None}
            
            with task_lock:
                if current_task_id in collection_tasks:
                    task_info = collection_tasks[current_task_id]
                    return {
                        "current_task": {
                            "task_id": current_task_id,
                            "status": task_info["status"],
                            "start_time": task_info["start_time"]
                        }
                    }
                else:
                    return {"current_task": None}
                    
    except Exception as e:
        logger.error(f"获取当前任务信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取当前任务信息失败: {str(e)}")
