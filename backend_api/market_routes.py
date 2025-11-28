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
def get_hk_market_indices():
    """获取港股指数数据，优先使用akshare stock_hk_index_spot_em，失败则使用stock_hk_index_daily_sina"""
    try:
        import akshare as ak
        
        # 港股指数代码映射
        hk_index_map = {
            'HSI': {'name': '恒生指数', 'ak_code': 'HSI'},
            'HSTECH': {'name': '恒生科技指数', 'ak_code': 'HSTECH'},
            'HSCI': {'name': '恒生综合指数', 'ak_code': 'HSCI'},
            'HSCEI': {'name': '恒生中国企业指数', 'ak_code': 'HSCEI'}
        }
        
        indices_data = []
        
        # 优先尝试使用 stock_hk_index_spot_em
        try:
            print('[get_hk_market_indices] 尝试使用 stock_hk_index_spot_em 接口')
            df = ak.stock_hk_index_spot_em()
            
            if df is not None and not df.empty:
                print(f'[get_hk_market_indices] stock_hk_index_spot_em 返回数据形状: {df.shape}')
                print(f'[get_hk_market_indices] stock_hk_index_spot_em 列名: {df.columns.tolist()}')
                
                # 遍历目标指数
                for code, info in hk_index_map.items():
                    try:
                        # 尝试通过指数代码或名称匹配
                        index_row = None
                        
                        # 先尝试通过代码匹配（可能列名是"代码"或"index_code"等）
                        if '代码' in df.columns:
                            index_row = df[df['代码'] == info['ak_code']]
                        elif 'index_code' in df.columns:
                            index_row = df[df['index_code'] == info['ak_code']]
                        elif 'code' in df.columns:
                            index_row = df[df['code'] == info['ak_code']]
                        
                        # 如果代码匹配失败，尝试通过名称匹配
                        if (index_row is None or index_row.empty) and '名称' in df.columns:
                            index_row = df[df['名称'].str.contains(info['name'], na=False)]
                        elif (index_row is None or index_row.empty) and 'name' in df.columns:
                            index_row = df[df['name'].str.contains(info['name'], na=False)]
                        
                        if index_row is not None and not index_row.empty:
                            row = index_row.iloc[0]
                            
                            # 提取数据（列名可能不同，需要灵活处理）
                            current = safe_float(row.get('最新价', row.get('current', row.get('price', None))))
                            change = safe_float(row.get('涨跌额', row.get('change', row.get('change_amount', None))))
                            change_percent = safe_float(row.get('涨跌幅', row.get('change_percent', row.get('pct_chg', None))))
                            volume = safe_float(row.get('成交量', row.get('volume', row.get('vol', 0))))
                            
                            indices_data.append({
                                'code': code,
                                'name': info['name'],
                                'current': current,
                                'change': change,
                                'change_percent': change_percent,
                                'volume': volume,
                                'timestamp': datetime.now().isoformat()
                            })
                            print(f'[get_hk_market_indices] 成功获取 {info["name"]} 数据')
                        else:
                            print(f'[get_hk_market_indices] 未找到 {info["name"]} 的数据')
                    except Exception as e:
                        print(f'[get_hk_market_indices] 处理 {info["name"]} 时出错: {str(e)}')
                        import traceback
                        traceback.print_exc()
                        continue
                
                if indices_data:
                    print(f'[get_hk_market_indices] 成功获取 {len(indices_data)} 个港股指数数据')
                    return JSONResponse({'success': True, 'data': indices_data})
            else:
                print('[get_hk_market_indices] stock_hk_index_spot_em 返回空数据')
                raise Exception('stock_hk_index_spot_em 返回空数据')
        except Exception as e1:
            print(f'[get_hk_market_indices] stock_hk_index_spot_em 接口调用失败: {str(e1)}')
            import traceback
            traceback.print_exc()
            
            # 失败则尝试使用 stock_hk_index_daily_sina
            try:
                print('[get_hk_market_indices] 尝试使用 stock_hk_index_daily_sina 接口')
                
                # 遍历目标指数，逐个获取
                for code, info in hk_index_map.items():
                    try:
                        # stock_hk_index_daily_sina 需要传入指数代码
                        df_sina = ak.stock_hk_index_daily_sina(symbol=info['ak_code'])
                        
                        if df_sina is not None and not df_sina.empty:
                            # 获取最新一条数据
                            latest_row = df_sina.iloc[-1]
                            
                            # 提取数据（列名可能是 date, open, close, high, low, volume 等）
                            current = safe_float(latest_row.get('close', latest_row.get('收盘', None)))
                            
                            # 计算涨跌额和涨跌幅（需要前一日数据）
                            if len(df_sina) >= 2:
                                prev_row = df_sina.iloc[-2]
                                prev_close = safe_float(prev_row.get('close', prev_row.get('收盘', None)))
                                if current is not None and prev_close is not None and prev_close > 0:
                                    change = current - prev_close
                                    change_percent = (change / prev_close) * 100
                                else:
                                    change = None
                                    change_percent = None
                            else:
                                change = None
                                change_percent = None
                            
                            volume = safe_float(latest_row.get('volume', latest_row.get('成交量', 0)))
                            
                            indices_data.append({
                                'code': code,
                                'name': info['name'],
                                'current': current,
                                'change': change,
                                'change_percent': change_percent,
                                'volume': volume,
                                'timestamp': datetime.now().isoformat()
                            })
                            print(f'[get_hk_market_indices] 通过sina接口成功获取 {info["name"]} 数据')
                    except Exception as e2:
                        print(f'[get_hk_market_indices] 通过sina接口获取 {info["name"]} 失败: {str(e2)}')
                        continue
                
                if indices_data:
                    print(f'[get_hk_market_indices] 通过sina接口成功获取 {len(indices_data)} 个港股指数数据')
                    return JSONResponse({'success': True, 'data': indices_data})
                else:
                    raise Exception('所有接口都未能获取到数据')
            except Exception as e2:
                print(f'[get_hk_market_indices] stock_hk_index_daily_sina 接口调用失败: {str(e2)}')
                import traceback
                traceback.print_exc()
                raise Exception(f'港股指数数据获取失败: {str(e2)}')
        
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