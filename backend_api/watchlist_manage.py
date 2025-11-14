"""
自选股管理API模块
提供自选股管理相关的接口
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import math

from models import (
    Watchlist, WatchlistGroup,
    WatchlistCreate, WatchlistInDB, WatchlistGroupCreate,
    WatchlistGroupInDB, User, StockRealtimeQuote
)
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])

@router.get("", response_model=None)
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取自选股列表（仅从实时行情表读取）"""
    try:
        user_id = current_user.id
        print(f"[watchlist] 请求用户ID: {user_id}")
        watchlist_rows = db.query(Watchlist).filter(
            Watchlist.user_id == user_id
        ).order_by(desc(Watchlist.created_at)).all()
        print(f"[watchlist] 查询到自选股代码: {[row.stock_code for row in watchlist_rows]}")
        if not watchlist_rows:
            print("[watchlist] 用户无自选股，返回空列表")
            return JSONResponse({'success': True, 'data': []})

        codes = [row.stock_code for row in watchlist_rows]
        unique_codes = list(dict.fromkeys(codes))
        names = {row.stock_code: row.stock_name for row in watchlist_rows}
        watchlist = []

        def safe_float(value):
            try:
                if value in [None, '', '-', '--']:
                    return None
                if isinstance(value, str):
                    cleaned = value.replace(',', '').strip()
                    if cleaned in ['', '-', '--']:
                        return None
                    value = cleaned
                result = float(value)
                if isinstance(result, float) and math.isnan(result):
                    return None
                return result
            except (ValueError, TypeError):
                return None

        today = datetime.now().strftime('%Y-%m-%d')
        today_pattern = f"{today}%"
        quotes_today = db.query(StockRealtimeQuote).filter(
            StockRealtimeQuote.code.in_(unique_codes),
            StockRealtimeQuote.trade_date.like(today_pattern)
        ).all()
        print(f"[watchlist] 当日行情数量: {len(quotes_today)}")

        quotes = quotes_today
        target_trade_date = today

        if not quotes:
            latest_trade_date = db.query(func.max(StockRealtimeQuote.trade_date)).scalar()
            if latest_trade_date:
                quotes = db.query(StockRealtimeQuote).filter(
                    StockRealtimeQuote.code.in_(unique_codes),
                    StockRealtimeQuote.trade_date == latest_trade_date
                ).all()
                target_trade_date = latest_trade_date
                print(f"[watchlist] 当日无数据，回退至最新交易日 {latest_trade_date}，行情数量: {len(quotes)}")
            else:
                print("[watchlist] 暂无行情数据，但仍返回自选股记录（行情字段为空）")

        print(f"[watchlist] 使用交易日期: {target_trade_date}，行情数量: {len(quotes)}")
        quote_map = {q.code: q for q in quotes}

        for row in watchlist_rows:
            code = row.stock_code
            q = quote_map.get(code)
            if not q:
                print(f"[watchlist] {code} 无行情数据，但仍返回自选股记录")
            watchlist.append({
                'code': code,
                'name': names.get(code, '') or row.stock_name or code,
                'group_name': row.group_name or 'default',
                'watchlist_id': row.id,
                'current_price': safe_float(getattr(q, 'current_price', None)) if q else None,
                'change_percent': safe_float(getattr(q, 'change_percent', None)) if q else None,
                'volume': safe_float(getattr(q, 'volume', None)) if q else None,
                'amount': safe_float(getattr(q, 'amount', None)) if q else None,
                'high': safe_float(getattr(q, 'high', None)) if q else None,
                'low': safe_float(getattr(q, 'low', None)) if q else None,
                'open': safe_float(getattr(q, 'open', None)) if q else None,
                'pre_close': safe_float(getattr(q, 'pre_close', None)) if q else None,
                'change_amount': (
                    safe_float(getattr(q, 'current_price', None)) - safe_float(getattr(q, 'pre_close', None))
                    if q and safe_float(getattr(q, 'current_price', None)) is not None and safe_float(getattr(q, 'pre_close', None)) is not None
                    else None
                ),
                'turnover_rate': safe_float(getattr(q, 'turnover_rate', None)) if q else None,
                'pe_dynamic': safe_float(getattr(q, 'pe_dynamic', None)) if q else None,
                'total_market_value': safe_float(getattr(q, 'total_market_value', None)) if q else None,
                'pb_ratio': safe_float(getattr(q, 'pb_ratio', None)) if q else None,
                'circulating_market_value': safe_float(getattr(q, 'circulating_market_value', None)) if q else None,
                'update_time': getattr(q, 'update_time', None).isoformat() if q and getattr(q, 'update_time', None) else None
            })
        print(f"[watchlist] 最终返回watchlist条数: {len(watchlist)}")
        if watchlist:
            print(f"[watchlist] 返回示例: {watchlist[0]}")
        return JSONResponse({'success': True, 'data': watchlist})
    except Exception as e:
        print(f"[watchlist] 异常: {str(e)}")
        return JSONResponse({'success': False, 'message': str(e)}, status_code=500)

        quotes = quotes_today
        target_trade_date = today_str

        if not quotes:
            latest_trade_date = db.query(func.max(StockRealtimeQuote.trade_date)).scalar()
            if latest_trade_date:
                quotes = db.query(StockRealtimeQuote).filter(
                    StockRealtimeQuote.code.in_(unique_codes),
                    StockRealtimeQuote.trade_date == latest_trade_date
                ).all()
                target_trade_date = latest_trade_date
                print(f"[watchlist] 当日无数据，回退至最新交易日 {latest_trade_date}，行情数量: {len(quotes)}")
            else:
                print("[watchlist] 暂无行情数据，但仍返回自选股记录（行情字段为空）")

        print(f"[watchlist] 使用交易日期: {target_trade_date}，行情数量: {len(quotes)}")
        quote_map = {q.code: q for q in quotes}

        for row in watchlist_rows:
            code = row.stock_code
            q = quote_map.get(code)
            if not q:
                print(f"[watchlist] {code} 无行情数据，但仍返回自选股记录")
            # 即使没有行情数据，也返回自选股记录
            watchlist.append({
                'code': code,
                'name': names.get(code, '') or row.stock_name or code,
                'group_name': row.group_name or 'default',
                'watchlist_id': row.id,
                'current_price': safe_float(getattr(q, 'current_price', None)) if q else None,
                'change_percent': safe_float(getattr(q, 'change_percent', None)) if q else None,
                'volume': safe_float(getattr(q, 'volume', None)) if q else None,
                'amount': safe_float(getattr(q, 'amount', None)) if q else None,
                'high': safe_float(getattr(q, 'high', None)) if q else None,
                'low': safe_float(getattr(q, 'low', None)) if q else None,
                'open': safe_float(getattr(q, 'open', None)) if q else None,
                'pre_close': safe_float(getattr(q, 'pre_close', None)) if q else None,
                'change_amount': (
                    safe_float(getattr(q, 'current_price', None)) - safe_float(getattr(q, 'pre_close', None))
                    if q and safe_float(getattr(q, 'current_price', None)) is not None and safe_float(getattr(q, 'pre_close', None)) is not None
                    else None
                ),                
                'turnover_rate': safe_float(getattr(q, 'turnover_rate', None)) if q else None,
                'pe_dynamic': safe_float(getattr(q, 'pe_dynamic', None)) if q else None,
                'total_market_value': safe_float(getattr(q, 'total_market_value', None)) if q else None,
                'pb_ratio': safe_float(getattr(q, 'pb_ratio', None)) if q else None,
                'circulating_market_value': safe_float(getattr(q, 'circulating_market_value', None)) if q else None,
                'update_time': getattr(q, 'update_time', None).isoformat() if q and getattr(q, 'update_time', None) else None
            })
        print(f"[watchlist] 最终返回watchlist条数: {len(watchlist)}")
        if watchlist:
            print(f"[watchlist] 返回示例: {watchlist[0]}")
        return JSONResponse({'success': True, 'data': watchlist})
    except Exception as e:
        print(f"[watchlist] 异常: {str(e)}")
        return JSONResponse({'success': False, 'message': str(e)}, status_code=500)

@router.get("/groups", response_model=List[WatchlistGroupInDB])
async def get_watchlist_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的自选股分组列表"""
    groups = db.query(WatchlistGroup).filter(
        WatchlistGroup.user_id == current_user.id
    ).order_by(desc(WatchlistGroup.created_at)).all()
    return groups

@router.post("", response_model=None)
async def add_to_watchlist(
    watchlist: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加股票到自选股"""
    try:
        user_id = current_user.id
        print(f"[watchlist] 添加自选股请求 - 用户ID: {user_id}, 股票代码: {watchlist.stock_code}, 股票名称: {watchlist.stock_name}, 分组: {watchlist.group_name}")
        
        # 检查是否已存在
        existing = db.query(Watchlist).filter(
            Watchlist.user_id == user_id,
            Watchlist.stock_code == watchlist.stock_code,
            Watchlist.group_name == watchlist.group_name
        ).first()
        
        if existing:
            print(f"[watchlist] 股票已存在于自选股列表中")
            return JSONResponse(
                {'success': False, 'message': '该股票已在自选股列表中'},
                status_code=400
            )
        
        # 创建新的自选股记录
        db_watchlist = Watchlist(
            user_id=user_id,
            stock_code=watchlist.stock_code,
            stock_name=watchlist.stock_name,
            group_name=watchlist.group_name
        )
        db.add(db_watchlist)
        db.commit()
        db.refresh(db_watchlist)
        print(f"[watchlist] 自选股添加成功 - ID: {db_watchlist.id}")
        return JSONResponse({'success': True, 'data': db_watchlist.id})
    except Exception as e:
        print(f"[watchlist] 添加自选股异常: {str(e)}")
        db.rollback()
        return JSONResponse(
            {'success': False, 'message': f'添加失败: {str(e)}'},
            status_code=500
        )

@router.post("/groups", response_model=WatchlistGroupInDB)
async def create_watchlist_group(
    group: WatchlistGroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建自选股分组"""
    # 检查分组名是否已存在
    existing = db.query(WatchlistGroup).filter(
        WatchlistGroup.user_id == current_user.id,
        WatchlistGroup.group_name == group.group_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该分组名已存在"
        )
    
    # 创建新的分组
    db_group = WatchlistGroup(
        user_id=current_user.id,
        group_name=group.group_name
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@router.put("/{watchlist_id}/group")
async def update_watchlist_group(
    watchlist_id: int,
    group_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新自选股的分组"""
    # 检查自选股是否存在
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()
    
    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自选股不存在"
        )
    
    # 检查新分组是否存在
    group = db.query(WatchlistGroup).filter(
        WatchlistGroup.user_id == current_user.id,
        WatchlistGroup.group_name == group_name
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分组不存在"
        )
    
    # 更新分组
    watchlist.group_name = group_name
    db.commit()
    return {"message": "分组更新成功"}

@router.delete("/{watchlist_id}")
async def remove_from_watchlist(
    watchlist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从自选股中删除股票"""
    # 检查自选股是否存在
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()
    
    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自选股不存在"
        )
    
    # 删除自选股
    db.delete(watchlist)
    db.commit()
    return {"message": "删除成功"}


class DeleteByCodeRequest(BaseModel):
    stock_code: str
    user_id: int

@router.post("/delete_by_code")
async def delete_watchlist_by_code(
    req: DeleteByCodeRequest,
    db: Session = Depends(get_db)
):
    stock_code = req.stock_code
    user_id = req.user_id
    print(f"[watchlist] 请求用户ID: {user_id}, 股票代码: {stock_code}")
    """根据股票代码+用户ID删除自选股"""
    # 检查自选股是否存在
    watchlist = db.query(Watchlist).filter(
        Watchlist.user_id == user_id,
        Watchlist.stock_code == stock_code
    ).first()

    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自选股不存在"
        )

    # 删除自选股
    db.delete(watchlist)
    db.commit()
    return JSONResponse({'success': True, 'message': "删除成功"})


@router.delete("/groups/{group_id}")
async def delete_watchlist_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除自选股分组"""
    # 检查分组是否存在
    group = db.query(WatchlistGroup).filter(
        WatchlistGroup.id == group_id,
        WatchlistGroup.user_id == current_user.id
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分组不存在"
        )
    
    # 检查是否为默认分组
    if group.group_name == "default":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除默认分组"
        )
    
    # 将该分组下的自选股移动到默认分组
    db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.group_name == group.group_name
    ).update({"group_name": "default"})
    
    # 删除分组
    db.delete(group)
    db.commit()
    return {"message": "分组删除成功"}
