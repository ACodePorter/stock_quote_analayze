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

