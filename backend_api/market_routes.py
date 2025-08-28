# backend_api/market_routes.py

from fastapi import APIRouter, Depends
import akshare as ak
from datetime import datetime
from fastapi.responses import JSONResponse
import random
import traceback
import pandas as pd
import numpy as np
import sqlite3
from sqlalchemy.orm import Session
from backend_api.database import get_db
from backend_api.models import IndexRealtimeQuotes, IndustryBoardRealtimeQuotes



router = APIRouter(prefix="/api/market", tags=["market"])

def safe_float(value):
    """安全地将值转换为浮点数，处理 NaN 和无效值"""
    try:
        if pd.isna(value) or value in [None, '', '-']:
            return None
        return float(value)
    except (ValueError, TypeError):
        return None

def row_to_dict(row):
    d = {}
    for c in row.__table__.columns:
        v = getattr(row, c.name)
        if isinstance(v, datetime):
            d[c.name] = v.strftime('%Y-%m-%d %H:%M:%S')
        else:
            d[c.name] = v
    return d

# 获取市场指数数据(修改为从数据库 index_realtime_quotes 表中获取)
@router.get("/indices")
def get_market_indices(db: Session = Depends(get_db)):
    """获取市场指数数据(从数据库 index_realtime_quotes 表中获取)"""
    def map_index_fields(row):
        return {
            "code": row.code,
            "name": row.name,
            "current": row.price,
            "change": row.change,
            "change_percent": row.pct_chg,
            "volume": row.volume,
            "timestamp": row.update_time,
        }
    try:
        index_codes = {
            '上证指数': '000001',
            '深圳成指': '399001',
            '创业板指': '399006',
            '沪深300': '000300',
        }
        indices_data = []
        for name, code in index_codes.items():
            row = db.query(IndexRealtimeQuotes).filter(IndexRealtimeQuotes.code == code).order_by(IndexRealtimeQuotes.update_time.desc()).first()
            if row is None:
                continue
            indices_data.append(map_index_fields(row))
        return JSONResponse({'success': True, 'data': indices_data})
    except Exception as e:
        return JSONResponse({'success': False, 'message': str(e)})

# 获取当日最新板块行情，按涨幅降序排序
@router.get("/industry_board")
def get_industry_board(db: Session = Depends(get_db)):
    """获取当日最新板块行情，按涨幅降序排序（从industry_board_realtime_quotes表读取）"""
    def map_board_fields(row):
        return {
            "board_code": row.board_code,
            "board_name": row.board_name,
            "latest_price": row.latest_price,
            "change_amount": row.change_amount,
            "change_percent": row.change_percent,
            "total_market_value": row.total_market_value,
            "volume": row.volume,
            "amount": row.amount,
            "turnover_rate": row.turnover_rate,
            "leading_stock_name": row.leading_stock_name,
            "leading_stock_code": row.leading_stock_code,
            "leading_stock_change_percent": row.leading_stock_change_percent,
            "update_time": row.update_time,
        }
    try:
        rows = db.query(IndustryBoardRealtimeQuotes).order_by(IndustryBoardRealtimeQuotes.change_percent.desc(), IndustryBoardRealtimeQuotes.update_time.desc()).all()
        data = [row_to_dict(row) for row in rows]
        return JSONResponse({'success': True, 'data': data})
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return JSONResponse({
            'success': False, 'message': '获取板块行情数据失败',
            'error': str(e),
            'traceback': tb
        }, status_code=500)

# 获取行业板块内涨幅领先的股票
@router.get("/industry_board/{board_code}/top_stocks")
def get_industry_board_top_stocks(board_code: str, board_name: str = None, db: Session = Depends(get_db)):
    """获取指定行业板块内涨幅领先的股票（从数据库表获取真实数据）"""
    try:
        # 不再需要akshare，直接从数据库获取数据
        
        # 获取板块内所有股票的实时行情数据
        # 不再使用AKShare获取板块成分股，直接从数据库表获取领涨股信息
        pass
        
        # 不再使用模拟数据
        pass
        
        # 不再使用AKShare获取股票实时数据，直接从数据库表获取
        pass
        
        # 直接从 industry_board_realtime_quotes 表获取领涨股信息
        board_data = db.query(IndustryBoardRealtimeQuotes).filter(
            IndustryBoardRealtimeQuotes.board_code == board_code
        ).first()
        
        if not board_data:
            return JSONResponse({
                'success': False,
                'message': f'未找到板块代码 {board_code} 的数据'
            })
        
        # 检查是否有领涨股信息
        if not board_data.leading_stock_name or not board_data.leading_stock_code:
            return JSONResponse({
                'success': False,
                'message': f'板块 {board_data.board_name} 暂无领涨股数据'
            })
        
        # 构建领涨股数据
        leading_stock = {
            'code': board_data.leading_stock_code,
            'name': board_data.leading_stock_name,
            'change_percent': board_data.leading_stock_change_percent or 0.0,
            'data_source': 'database_realtime'
        }
        
        # 目前数据库表只存储了一只领涨股，返回单只股票
        top_stocks = [leading_stock]
        
        return JSONResponse({
            'success': True,
            'data': {
                'board_code': board_code,
                'board_name': board_data.board_name,
                'top_stocks': top_stocks,
                'total_stocks': 1,  # 目前只返回一只领涨股
                'data_source': 'database_realtime',
                'message': '数据来源：industry_board_realtime_quotes 表'
            }
        })
        
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return JSONResponse({
            'success': False,
            'message': '获取板块龙头股数据失败',
            'error': str(e),
            'traceback': tb
        }, status_code=500) 