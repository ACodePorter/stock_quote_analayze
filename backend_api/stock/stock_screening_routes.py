"""
选股策略API路由
提供创业板中线选股策略接口
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from database import get_db
from stock.stock_screening import StockScreeningStrategy
from stock.high_tight_flag_strategy import HighTightFlagStrategy
from stock.keep_increasing_strategy import KeepIncreasingStrategy
from stock.long_lower_shadow_strategy import LongLowerShadowStrategy

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/screening", tags=["screening"])


@router.get("/cyb-midline-strategy")
async def get_cyb_midline_strategy(
    months: int = Query(4, ge=3, le=4, description="查询月数（3-4个月）"),
    db: Session = Depends(get_db)
):
    """
    创业板中线选股策略
    
    策略条件：
    1. 第一个涨停（涨幅>=9.8%）
    2. 第一次回调不跌穿涨停底部
    3. 第二次上涨突破第一个涨停高点
    4. 中间有向上跳空和揉搓线
    5. 当前均线多头排列（MA5>MA10>MA20）
    
    Args:
        months: 查询月数，默认4个月
        db: 数据库会话
    
    Returns:
        符合条件的股票列表
    """
    try:
        logger.info(f"开始执行创业板中线选股策略，查询月数: {months}")
        
        # 执行选股策略
        results = StockScreeningStrategy.screening_cyb_midline_strategy(db, months=months)
        
        logger.info(f"选股策略执行完成，找到 {len(results)} 只符合条件的股票")
        
        return JSONResponse({
            "success": True,
            "data": results,
            "total": len(results),
            "search_date": datetime.now().strftime("%Y-%m-%d"),
            "months": months,
            "strategy_name": "创业板中线选股策略"
        })
        
    except Exception as e:
        logger.error(f"执行选股策略失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"选股策略执行失败: {str(e)}"
        )


@router.get("/parking-apron-strategy")
async def get_parking_apron_strategy(
    db: Session = Depends(get_db)
):
    """
    停机坪选股策略
    
    策略条件：
    1. 最近15日有涨幅大于9.5%，且必须是放量上涨
    2. 紧接的下个交易日必须高开，收盘价必须上涨，且与开盘价不能大于等于相差3%
    3. 接下2、3个交易日必须高开，收盘价必须上涨，且与开盘价不能大于等于相差3%，且每天涨跌幅在5%间
    
    Args:
        db: 数据库会话
    
    Returns:
        符合条件的股票列表
    """
    try:
        logger.info("开始执行停机坪选股策略")
        
        # 执行选股策略
        results = StockScreeningStrategy.screening_parking_apron_strategy(db)
        
        logger.info(f"停机坪选股策略执行完成，找到 {len(results)} 只符合条件的股票")
        
        return JSONResponse({
            "success": True,
            "data": results,
            "total": len(results),
            "search_date": datetime.now().strftime("%Y-%m-%d"),
            "strategy_name": "停机坪"
        })
        
    except Exception as e:
        logger.error(f"执行停机坪选股策略失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"停机坪选股策略执行失败: {str(e)}"
        )


@router.get("/backtrace-ma250-strategy")
async def get_backtrace_ma250_strategy(
    db: Session = Depends(get_db)
):
    """
    回踩年线选股策略
    
    策略条件：
    1. 时间段：前段=最近60交易日最高收盘价之前交易日(长度>0)，后段=最高价当日及后面的交易日
    2. 前段由年线(250日)以下向上突破
    3. 后段必须在年线以上运行，且后段最低价日与最高价日相差必须在10-50日间
    4. 回踩伴随缩量：最高价日交易量/后段最低价日交易量>2,后段最低价/最高价<0.8
    
    Args:
        db: 数据库会话
    
    Returns:
        符合条件的股票列表
    """
    try:
        logger.info("开始执行回踩年线选股策略")
        
        # 执行选股策略
        results = StockScreeningStrategy.screening_backtrace_ma250_strategy(db)
        
        logger.info(f"回踩年线选股策略执行完成，找到 {len(results)} 只符合条件的股票")
        
        return JSONResponse({
            "success": True,
            "data": results,
            "total": len(results),
            "search_date": datetime.now().strftime("%Y-%m-%d"),
            "strategy_name": "回踩年线"
        })
        
    except Exception as e:
        logger.error(f"执行回踩年线选股策略失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"回踩年线选股策略执行失败: {str(e)}"
        )


@router.get("/high-tight-flag-strategy")
async def get_high_tight_flag_strategy(
    db: Session = Depends(get_db)
):
    """
    高而窄的旗形选股策略
    
    策略条件：
    1. 必须至少上市交易60日
    2. 当日收盘价/之前24~10日的最低价>=1.9
    3. 之前24~10日必须连续两天涨幅大于等于9.5%
    
    Args:
        db: 数据库会话
    
    Returns:
        符合条件的股票列表
    """
    try:
        logger.info("开始执行高而窄的旗形选股策略")
        
        # 执行选股策略
        results = HighTightFlagStrategy.screening_high_tight_flag_strategy(db)
        
        logger.info(f"高而窄的旗形选股策略执行完成，找到 {len(results)} 只符合条件的股票")
        
        return JSONResponse({
            "success": True,
            "data": results,
            "total": len(results),
            "search_date": datetime.now().strftime("%Y-%m-%d"),
            "strategy_name": "高而窄的旗形"
        })
        
    except Exception as e:
        logger.error(f"执行高而窄的旗形选股策略失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"高而窄的旗形选股策略执行失败: {str(e)}"
        )


@router.get("/keep-increasing-strategy")
async def get_keep_increasing_strategy(
    db: Session = Depends(get_db)
):
    """
    持续上涨（MA30向上）选股策略
    
    策略条件：
    1. 均线多头：30日前的30日均线 < 20日前的30日均线 < 10日前的30日均线 < 当日的30日均线
    2. 涨幅要求：(当日的30日均线 / 30日前的30日均线) > 1.2
    
    Args:
        db: 数据库会话
    
    Returns:
        符合条件的股票列表
    """
    try:
        logger.info("开始执行持续上涨（MA30向上）选股策略")
        
        # 执行选股策略
        results = KeepIncreasingStrategy.screening_keep_increasing_strategy(db)
        
        logger.info(f"持续上涨（MA30向上）选股策略执行完成，找到 {len(results)} 只符合条件的股票")
        
        return JSONResponse({
            "success": True,
            "data": results,
            "total": len(results),
            "search_date": datetime.now().strftime("%Y-%m-%d"),
            "strategy_name": "持续上涨（MA30向上）"
        })
        
    except Exception as e:
        logger.error(f"执行持续上涨（MA30向上）选股策略失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"持续上涨（MA30向上）选股策略执行失败: {str(e)}"
        )


@router.get("/long-lower-shadow-strategy")
async def get_long_lower_shadow_strategy(
    db: Session = Depends(get_db)
):
    """
    长下影阳线选股策略
    
    策略条件:
    1. 下跌趋势: 当前价格 < 60日前价格
    2. 长下影阳线: 最近7个交易日内出现
       - 收盘价 > 开盘价 (阳线)
       - 下影线长度 >= 实体长度的2倍
    
    Args:
        db: 数据库会话
    
    Returns:
        符合条件的股票列表
    """
    try:
        logger.info("开始执行长下影阳线选股策略")
        
        # 执行选股策略
        results = LongLowerShadowStrategy.screening_long_lower_shadow_strategy(db)
        
        logger.info(f"长下影阳线选股策略执行完成，找到 {len(results)} 只符合条件的股票")
        
        return JSONResponse({
            "success": True,
            "data": results,
            "total": len(results),
            "search_date": datetime.now().strftime("%Y-%m-%d"),
            "strategy_name": "长下影阳线"
        })
        
    except Exception as e:
        logger.error(f"执行长下影阳线选股策略失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"长下影阳线选股策略执行失败: {str(e)}"
        )