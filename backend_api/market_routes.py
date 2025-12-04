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
from sqlalchemy import desc
from backend_api.database import get_db
from backend_api.models import IndexRealtimeQuotes, IndustryBoardRealtimeQuotes, HKIndexRealtimeQuotes



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
    def map_index_fields(row, target_code):
        """映射字段，并标准化code为前端期望的格式"""
        return {
            "code": target_code,  # 使用标准化的代码（不带sh/sz前缀）
            "name": row.name,
            "current": row.price,
            "change": row.change,
            "change_percent": row.pct_chg,
            "volume": row.volume,
            "timestamp": row.update_time,
        }
    try:
        # 定义目标指数：名称和对应的标准代码
        target_indices = {
            '000001': ['上证指数'],  # 可能有sh000001格式
            '399001': ['深证成指', '深圳成指'],  # 支持两种名称
            '399006': ['创业板指'],
            '000300': ['沪深300'],
        }
        indices_data = []
        for target_code, possible_names in target_indices.items():
            # 尝试按名称匹配（支持多种可能的名称）
            row = None
            for name in possible_names:
                row = db.query(IndexRealtimeQuotes).filter(
                    IndexRealtimeQuotes.name == name
                ).order_by(IndexRealtimeQuotes.update_time.desc()).first()
                if row:
                    break
            
            # 如果按名称没找到，尝试按代码匹配（支持sh/sz前缀格式）
            if row is None:
                # 尝试直接匹配代码
                row = db.query(IndexRealtimeQuotes).filter(
                    IndexRealtimeQuotes.code == target_code
                ).order_by(IndexRealtimeQuotes.update_time.desc()).first()
            
            # 如果还是没找到，尝试匹配带前缀的代码
            if row is None:
                # 根据代码判断市场前缀：000开头是sh，399开头是sz
                if target_code.startswith('000'):
                    prefix_code = f'sh{target_code}'
                elif target_code.startswith('399') or target_code.startswith('159'):
                    prefix_code = f'sz{target_code}'
                else:
                    prefix_code = target_code
                
                row = db.query(IndexRealtimeQuotes).filter(
                    IndexRealtimeQuotes.code == prefix_code
                ).order_by(IndexRealtimeQuotes.update_time.desc()).first()
            
            if row:
                indices_data.append(map_index_fields(row, target_code))
        
        return JSONResponse({'success': True, 'data': indices_data})
    except Exception as e:
        import traceback
        return JSONResponse({
            'success': False, 
            'message': str(e),
            'traceback': traceback.format_exc()
        })

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

# 获取港股指数数据
@router.get("/hk-indices")
def get_hk_market_indices(db: Session = Depends(get_db)):
    """获取港股指数数据（从数据库 hk_index_realtime_quotes 表中获取当前日期的数据）"""
    try:
        # 获取当前日期
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # 查询当前日期的所有港股指数数据，如果没有则查询最新日期的数据
        rows = db.query(HKIndexRealtimeQuotes).filter(
            HKIndexRealtimeQuotes.trade_date == current_date
        ).all()
        
        # 如果当前日期没有数据，查询最新日期的数据
        if not rows:
            # 获取最新的交易日期
            latest_date_row = db.query(HKIndexRealtimeQuotes).order_by(
                desc(HKIndexRealtimeQuotes.trade_date)
            ).first()
            
            if latest_date_row:
                latest_date = latest_date_row.trade_date
                rows = db.query(HKIndexRealtimeQuotes).filter(
                    HKIndexRealtimeQuotes.trade_date == latest_date
                ).all()
        
        indices_data = []
        if rows:
            for row in rows:
                indices_data.append({
                    'code': row.code,
                    'name': row.name,
                    'current': row.price,
                    'change': row.change,
                    'change_percent': row.pct_chg,
                    'volume': row.volume or 0,
                    'timestamp': row.update_time or datetime.now().isoformat()
                })
        
        if indices_data:
            return JSONResponse({'success': True, 'data': indices_data})
        else:
            # 如果数据库没有数据，返回空数据提示
            return JSONResponse({
                'success': False,
                'message': '数据库中暂无港股指数数据，请先运行数据采集任务',
                'data': []
            })
        
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f'[get_hk_market_indices] 获取港股指数数据异常: {str(e)}')
        print(tb)
        return JSONResponse({
            'success': False,
            'message': f'获取港股指数数据失败: {str(e)}',
            'error': str(e),
            'traceback': tb
        }, status_code=500)

# 获取行业板块内涨幅领先的股票
@router.get("/industry_board/{board_code}/top_stocks")
def get_industry_board_top_stocks(board_code: str, board_name: str = None, db: Session = Depends(get_db)):
    """获取指定行业板块内涨幅领先的股票（从数据库表获取真实数据）"""
    try:
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