"""
行情数据API路由
提供股票、指数、行业板块的实时行情数据查询服务
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, case
from datetime import datetime, timedelta
import logging
import math
import pandas as pd

from database import get_db
from models import (
    StockRealtimeQuote,
    IndexRealtimeQuotes,
    IndustryBoardRealtimeQuotes
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quotes", tags=["quotes"])

# 响应模型
class QuotesResponse:
    def __init__(self, success: bool, data: List[Dict], total: int, page: int, page_size: int, message: str = ""):
        self.success = success
        self.data = data
        self.total = total
        self.page = page
        self.page_size = page_size
        self.message = message

    def dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "message": self.message
        }

class StatsResponse:
    def __init__(self, success: bool, data: Dict, message: str = ""):
        self.success = success
        self.data = data
        self.message = message

    def dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message
        }

def safe_float(value) -> Optional[float]:
    """安全地将值转换为浮点数"""
    try:
        if value is None:
            return None
        # 移除pandas依赖，直接检查
        if isinstance(value, (int, float)):
            # 检查是否为nan或inf
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                return None
            return float(value)
        elif isinstance(value, str) and value.strip():
            # 检查字符串是否为nan或inf
            if value.lower() in ['nan', 'inf', '-inf', 'infinity', '-infinity']:
                return None
            return float(value)
        else:
            return None
    except (ValueError, TypeError) as e:
        logger.warning(f"safe_float转换失败: {value} ({type(value)}) - {str(e)}")
        return None

def safe_datetime(value) -> Optional[str]:
    """安全地处理时间字段"""
    try:
        if value is None:
            return None
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        elif isinstance(value, str):
            return value
        else:
            return str(value)
    except Exception as e:
        logger.warning(f"safe_datetime转换失败: {value} ({type(value)}) - {str(e)}")
        return None

def format_quotes_data(data: List[Any], data_type: str) -> List[Dict]:
    """格式化行情数据"""
    formatted_data = []
    
    for item in data:
        if data_type == "stocks":
            formatted_item = {
                "code": item.code,
                "name": item.name,
                "current_price": safe_float(item.current_price),
                "change_percent": safe_float(item.change_percent),
                "volume": safe_float(item.volume),
                "amount": safe_float(item.amount),
                "high": safe_float(item.high),
                "low": safe_float(item.low),
                "open": safe_float(item.open),
                "pre_close": safe_float(item.pre_close),
                "turnover_rate": safe_float(item.turnover_rate),
                "pe_dynamic": safe_float(item.pe_dynamic),
                "total_market_value": safe_float(item.total_market_value),
                "pb_ratio": safe_float(item.pb_ratio),
                "circulating_market_value": safe_float(item.circulating_market_value),
                "update_time": safe_datetime(item.update_time)
            }
        elif data_type == "indices":
            formatted_item = {
                "code": item.code,
                "name": item.name,
                "price": safe_float(item.price),
                "change": safe_float(item.change),
                "pct_chg": safe_float(item.pct_chg),
                "high": safe_float(item.high),
                "low": safe_float(item.low),
                "open": safe_float(item.open),
                "pre_close": safe_float(item.pre_close),
                "volume": safe_float(item.volume),
                "amount": safe_float(item.amount),
                "amplitude": safe_float(item.amplitude),
                "turnover": safe_float(item.turnover),
                "pe": safe_float(item.pe),
                "volume_ratio": safe_float(item.volume_ratio),
                "update_time": safe_datetime(item.update_time)
            }
        elif data_type == "industries":
            formatted_item = {
                "name": item.board_name,
                "price": safe_float(item.latest_price),
                "change_percent": safe_float(item.change_percent),
                "change_amount": safe_float(item.change_amount),
                "total_market_value": safe_float(item.total_market_value),
                "volume": safe_float(item.volume),
                "amount": safe_float(item.amount),
                "turnover_rate": safe_float(item.turnover_rate),
                "leading_stock": item.leading_stock_name,
                "leading_stock_change": safe_float(item.leading_stock_change_percent),
                "leading_stock_code": item.leading_stock_code,
                "update_time": safe_datetime(item.update_time)
            }
        else:
            continue
            
        formatted_data.append(formatted_item)
    
    return formatted_data

@router.get("/stocks")
async def get_stock_quotes(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=200, description="每页大小"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    market: Optional[str] = Query(None, description="市场类型"),
    sort_by: Optional[str] = Query("change_percent", description="排序字段")
):
    """获取股票实时行情数据"""
    try:
        db = next(get_db())
        
        # 首先获取最新的交易日期
        latest_date_result = pd.read_sql_query("""
            SELECT MAX(trade_date) as latest_date 
            FROM stock_realtime_quote 
            WHERE change_percent IS NOT NULL AND change_percent != 0
        """, db.bind)
        
        if latest_date_result.empty or latest_date_result.iloc[0]['latest_date'] is None:
            db.close()
            return JSONResponse({'success': False, 'message': '暂无行情数据'}, status_code=404)
        
        latest_trade_date = latest_date_result.iloc[0]['latest_date']
        print(f"📅 使用最新交易日期: {latest_trade_date}")
        
        # 构建查询，按最新交易日期过滤
        query = db.query(StockRealtimeQuote).filter(StockRealtimeQuote.trade_date == latest_trade_date)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                (StockRealtimeQuote.code.contains(keyword)) |
                (StockRealtimeQuote.name.contains(keyword))
            )
        
        # 市场类型过滤
        if market:
            if market == "sh":
                query = query.filter(StockRealtimeQuote.code.startswith('6'))
            elif market == "sz":
                query = query.filter(StockRealtimeQuote.code.startswith('0'))
            elif market == "cy":
                query = query.filter(StockRealtimeQuote.code.startswith('3'))
            elif market == "bj":
                query = query.filter(StockRealtimeQuote.code.startswith('8'))
        
        # 排序 - 使用 case 语句确保 null 值排在最后
        if sort_by == "change_percent":
            query = query.order_by(
                case(
                    (StockRealtimeQuote.change_percent.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.change_percent)
            )
        elif sort_by == "current_price":
            query = query.order_by(
                case(
                    (StockRealtimeQuote.current_price.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.current_price)
            )
        elif sort_by == "high":
            query = query.order_by(
                case(
                    (StockRealtimeQuote.high.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.high)
            )
        elif sort_by == "low":
            query = query.order_by(
                case(
                    (StockRealtimeQuote.low.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.low)
            )
        elif sort_by == "open":
            query = query.order_by(
                case(
                    (StockRealtimeQuote.open.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.open)
            )
        elif sort_by == "pre_close":
            query = query.order_by(
                case(
                    (StockRealtimeQuote.pre_close.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.pre_close)
            )
        elif sort_by == "volume":
            query = query.order_by(
                case(
                    (StockRealtimeQuote.volume.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.volume)
            )
        elif sort_by == "amount":
            query = query.order_by(
                case(
                    (StockRealtimeQuote.amount.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.amount)
            )
        elif sort_by == "turnover_rate":
            query = query.order_by(
                case(
                    (StockRealtimeQuote.turnover_rate.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.turnover_rate)
            )
        elif sort_by == "pe_dynamic":
            query = query.order_by(
                case(
                    (StockRealtimeQuote.pe_dynamic.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.pe_dynamic)
            )
        elif sort_by == "total_market_value":
            query = query.order_by(
                case(
                    (StockRealtimeQuote.total_market_value.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.total_market_value)
            )
        elif sort_by == "pb_ratio":
            query = query.order_by(
                case(
                    (StockRealtimeQuote.pb_ratio.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.pb_ratio)
            )
        elif sort_by == "circulating_market_value":
            query = query.order_by(
                case(
                    (StockRealtimeQuote.circulating_market_value.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.circulating_market_value)
            )
        else:
            query = query.order_by(
                case(
                    (StockRealtimeQuote.update_time.is_(None), 0),
                    else_=1
                ).desc(),
                desc(StockRealtimeQuote.update_time)
            )
        
        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        data = query.offset(offset).limit(page_size).all()
        
        # 格式化数据
        formatted_data = format_quotes_data(data, "stocks")
        
        response = QuotesResponse(
            success=True,
            data=formatted_data,
            total=total,
            page=page,
            page_size=page_size
        )
        
        return response.dict()
        
    except Exception as e:
        logger.error(f"获取股票行情数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取股票行情数据失败: {str(e)}"
        )
    finally:
        db.close()

@router.get("/indices")
async def get_index_quotes(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: Optional[str] = Query("pct_chg", description="排序字段")
):
    """获取指数实时行情数据"""
    try:
        db = next(get_db())
        
        # 构建查询
        query = db.query(IndexRealtimeQuotes)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                (IndexRealtimeQuotes.code.contains(keyword)) |
                (IndexRealtimeQuotes.name.contains(keyword))
            )
        
        # 排序 - 移除SQL排序，统一使用Python排序确保所有空值都排在最后
        
        # 分页和排序 - 统一使用Python排序确保所有空值都排在最后
        all_data = query.all()
        
        # 根据排序字段进行Python排序，确保null值排在最后
        if sort_by == "pct_chg":
            all_data.sort(key=lambda x: (x.pct_chg is None, x.pct_chg or 0), reverse=True)
        elif sort_by == "price":
            all_data.sort(key=lambda x: (x.price is None, x.price or 0), reverse=True)
        elif sort_by == "change":
            all_data.sort(key=lambda x: (x.change is None, x.change or 0), reverse=True)
        elif sort_by == "high":
            all_data.sort(key=lambda x: (x.high is None, x.high or 0), reverse=True)
        elif sort_by == "low":
            all_data.sort(key=lambda x: (x.low is None, x.low or 0), reverse=True)
        elif sort_by == "open":
            all_data.sort(key=lambda x: (x.open is None, x.open or 0), reverse=True)
        elif sort_by == "pre_close":
            all_data.sort(key=lambda x: (x.pre_close is None, x.pre_close or 0), reverse=True)
        elif sort_by == "volume":
            all_data.sort(key=lambda x: (x.volume is None, x.volume or 0), reverse=True)
        elif sort_by == "amount":
            all_data.sort(key=lambda x: (x.amount is None, x.amount or 0), reverse=True)
        elif sort_by == "amplitude":
            all_data.sort(key=lambda x: (x.amplitude is None, x.amplitude or 0), reverse=True)
        elif sort_by == "turnover":
            all_data.sort(key=lambda x: (x.turnover is None, x.turnover or 0), reverse=True)
        elif sort_by == "pe":
            all_data.sort(key=lambda x: (x.pe is None, x.pe or 0), reverse=True)
        elif sort_by == "volume_ratio":
            all_data.sort(key=lambda x: (x.volume_ratio is None, x.volume_ratio or 0), reverse=True)
        else:
            # 默认按更新时间排序
            all_data.sort(key=lambda x: (x.update_time is None, x.update_time or datetime.min), reverse=True)
        
        total = len(all_data)
        start = (page - 1) * page_size
        end = start + page_size
        data = all_data[start:end]
        
        # 格式化数据
        formatted_data = format_quotes_data(data, "indices")
        
        response = QuotesResponse(
            success=True,
            data=formatted_data,
            total=total,
            page=page,
            page_size=page_size
        )
        
        return response.dict()
        
    except Exception as e:
        logger.error(f"获取指数行情数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取指数行情数据失败: {str(e)}"
        )
    finally:
        db.close()

@router.get("/industries")
async def get_industry_quotes(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: Optional[str] = Query("change_percent", description="排序字段")
):
    """获取行业板块实时行情数据"""
    try:
        db = next(get_db())
        
        # 构建查询
        query = db.query(IndustryBoardRealtimeQuotes)
        
        # 关键词搜索
        if keyword:
            query = query.filter(IndustryBoardRealtimeQuotes.name.contains(keyword))
        
        # 排序 - 使用 case 语句确保 null 值排在最后
        if sort_by == "change_percent":
            query = query.order_by(
                case(
                    (IndustryBoardRealtimeQuotes.change_percent.is_(None), 0),
                    else_=1
                ).desc(),
                desc(IndustryBoardRealtimeQuotes.change_percent)
            )
        elif sort_by == "amount":
            query = query.order_by(
                case(
                    (IndustryBoardRealtimeQuotes.amount.is_(None), 0),
                    else_=1
                ).desc(),
                desc(IndustryBoardRealtimeQuotes.amount)
            )
        elif sort_by == "turnover_rate":
            query = query.order_by(
                case(
                    (IndustryBoardRealtimeQuotes.turnover_rate.is_(None), 0),
                    else_=1
                ).desc(),
                desc(IndustryBoardRealtimeQuotes.turnover_rate)
            )
        else:
            query = query.order_by(
                case(
                    (IndustryBoardRealtimeQuotes.update_time.is_(None), 0),
                    else_=1
                ).desc(),
                desc(IndustryBoardRealtimeQuotes.update_time)
            )
        
        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        data = query.offset(offset).limit(page_size).all()
        
        # 格式化数据
        formatted_data = format_quotes_data(data, "industries")
        
        response = QuotesResponse(
            success=True,
            data=formatted_data,
            total=total,
            page=page,
            page_size=page_size
        )
        
        return response.dict()
        
    except Exception as e:
        logger.error(f"获取行业板块行情数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取行业板块行情数据失败: {str(e)}"
        )
    finally:
        db.close()

@router.get("/stats")
async def get_quotes_stats():
    """获取行情数据统计信息"""
    try:
        db = next(get_db())
        
        # 统计各表数据量
        total_stocks = db.query(func.count(StockRealtimeQuote.code)).scalar() or 0
        total_indices = db.query(func.count(IndexRealtimeQuotes.code)).scalar() or 0
        total_industries = db.query(func.count(IndustryBoardRealtimeQuotes.board_name)).scalar() or 0
        
        # 获取最后更新时间
        last_stock_update = db.query(func.max(StockRealtimeQuote.update_time)).scalar()
        last_index_update = db.query(func.max(IndexRealtimeQuotes.update_time)).scalar()
        last_industry_update = db.query(func.max(IndustryBoardRealtimeQuotes.update_time)).scalar()
        
        # 取最新的更新时间
        update_times = []
        if last_stock_update and isinstance(last_stock_update, datetime):
            update_times.append(last_stock_update)
        if last_index_update and isinstance(last_index_update, datetime):
            update_times.append(last_index_update)
        if last_industry_update and isinstance(last_industry_update, datetime):
            update_times.append(last_industry_update)
        
        last_update_time = max(update_times) if update_times else datetime.now()
        
        stats_data = {
            "totalStocks": total_stocks,
            "totalIndices": total_indices,
            "totalIndustries": total_industries,
            "lastUpdateTime": last_update_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_update_time, datetime) else str(last_update_time)
        }
        
        response = StatsResponse(
            success=True,
            data=stats_data
        )
        
        return response.dict()
        
    except Exception as e:
        logger.error(f"获取行情数据统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取行情数据统计失败: {str(e)}"
        )
    finally:
        db.close()

@router.post("/refresh")
async def refresh_quotes():
    """刷新所有行情数据"""
    try:
        # TODO: 实现数据刷新逻辑
        # 这里可以调用数据采集服务来更新行情数据
        
        return {
            "success": True,
            "message": "行情数据刷新任务已启动"
        }
        
    except Exception as e:
        logger.error(f"刷新行情数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新行情数据失败: {str(e)}"
        )
