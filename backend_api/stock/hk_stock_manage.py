"""
港股行情管理API
提供港股实时行情数据查询服务
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from database import get_db
import traceback
import numpy as np
import pandas as pd
from sqlalchemy import text, create_engine

router = APIRouter(prefix="/api/stock", tags=["stock"])

def safe_float(value):
    """安全地将值转换为浮点数"""
    try:
        if value in [None, '', '-'] or pd.isna(value):
            return None
        return float(value)
    except (ValueError, TypeError):
        return None

def clean_nan(data_list):
    """清理数据中的NaN值"""
    if not isinstance(data_list, list):
        return data_list
    cleaned = []
    for item in data_list:
        if isinstance(item, dict):
            cleaned_item = {}
            for k, v in item.items():
                if pd.isna(v) or (isinstance(v, float) and np.isnan(v)):
                    cleaned_item[k] = None
                else:
                    cleaned_item[k] = v
            cleaned.append(cleaned_item)
        else:
            cleaned.append(item)
    return cleaned

@router.get("/hk_quote_board_list")
def get_hk_quote_board_list(
    ranking_type: str = Query('rise', description="排行类型: rise(涨幅榜), fall(跌幅榜), volume(成交量榜), turnover_rate(换手率榜)"),
    page: int = Query(1, description="页码，从1开始"),
    page_size: int = Query(20, description="每页条数，默认20"),
    keyword: str = Query(None, description="搜索关键词（股票代码或名称）")
):
    """
    获取港股实时行情排行数据，支持多种排行类型、搜索和分页 (数据源: stock_realtime_quote_hk)
    """
    try:
        print(f"📊 获取港股行情排行 (from DB): type={ranking_type}, page={page}, page_size={page_size}, keyword={keyword}")
        
        # 1. 获取最新交易日期的实时行情数据
        db = next(get_db())
        
        try:
            latest_date_result = pd.read_sql_query("""
                SELECT MAX(trade_date) as latest_date 
                FROM stock_realtime_quote_hk 
                WHERE change_percent IS NOT NULL
            """, db.bind)
            
            if latest_date_result.empty or latest_date_result.iloc[0]['latest_date'] is None:
                latest_trade_date = None
                df = pd.DataFrame()
            else:
                latest_trade_date = latest_date_result.iloc[0]['latest_date']
                if latest_trade_date is not None and len(str(latest_trade_date)) > 10:
                    latest_trade_date = str(latest_trade_date)[:10]
                print(f"📅 使用最新交易日期: {latest_trade_date}")
              
                # 构建查询SQL - 使用与stock_manage.py相同的方式
                if keyword and keyword.strip():
                    keyword_clean = keyword.strip().replace("'", "''")  # 防止SQL注入
                    sql_query = text(f"""
                        SELECT * FROM stock_realtime_quote_hk 
                        WHERE change_percent IS NOT NULL AND trade_date = '{latest_trade_date}'
                        AND (code LIKE '%{keyword_clean}%' OR name LIKE '%{keyword_clean}%' OR english_name LIKE '%{keyword_clean}%')
                        ORDER BY code
                    """)
                else:
                    sql_query = text(f"""
                        SELECT * FROM stock_realtime_quote_hk 
                        WHERE change_percent IS NOT NULL AND trade_date = '{latest_trade_date}'
                        ORDER BY code
                    """)
                
                df = pd.read_sql_query(sql_query, db.bind)
        finally:
            db.close()

        # 2. 排行类型排序
        sort_column_map = {
            'rise': ('change_percent', False),
            'fall': ('change_percent', True),
            'volume': ('volume', False),
            'turnover_rate': ('turnover_rate', False)
        }
        
        if ranking_type in sort_column_map:
            col, ascending = sort_column_map[ranking_type]
            if not df.empty and col in df.columns:
                df = df.sort_values(by=col, ascending=ascending, na_position='last')
        else:
            return JSONResponse({'success': False, 'message': '无效的排行类型'}, status_code=400)

        # 3. 字段重命名和格式化
        df = df.replace({np.nan: None})
        
        # 确保数值字段的数据类型正确
        numeric_columns = ['current_price', 'change_percent', 'change_amount', 'open', 'pre_close', 
                          'high', 'low', 'volume', 'amount']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 字段映射，与A股接口保持一致
        field_rename_map = {
            'code': 'code',
            'name': 'name',
            'english_name': 'english_name',
            'current_price': 'current',
            'change_percent': 'change_percent',
            'change_amount': 'change',
            'open': 'open',
            'pre_close': 'pre_close',
            'high': 'high',
            'low': 'low',
            'volume': 'volume',
            'amount': 'turnover'
        }
        
        if df.empty:
            df_selected = pd.DataFrame(columns=field_rename_map.values())
        else:
            # 只选择存在的字段
            available_fields = [f for f in field_rename_map.keys() if f in df.columns]
            df_selected = df[available_fields].rename(columns=field_rename_map)
            
            # 如果change字段不存在，尝试计算
            if 'change' not in df_selected.columns and 'current' in df_selected.columns and 'pre_close' in df_selected.columns:
                current_numeric = pd.to_numeric(df_selected['current'], errors='coerce')
                pre_close_numeric = pd.to_numeric(df_selected['pre_close'], errors='coerce')
                df_selected['change'] = (current_numeric - pre_close_numeric).round(2)
            
            # 添加rate字段（换手率），港股可能没有，设为None
            if 'rate' not in df_selected.columns:
                df_selected['rate'] = None

        total = len(df_selected)

        # 4. 分页处理
        start = (page - 1) * page_size
        end = start + page_size
        df_page = df_selected.iloc[start:end].copy()
        
        # 5. 格式化数据
        data = df_page.to_dict(orient='records')
        data = clean_nan(data)
        
        # 格式化数值字段
        for item in data:
            for key in ['current', 'change', 'change_percent', 'open', 'pre_close', 'high', 'low', 'volume', 'turnover', 'rate']:
                if key in item and item[key] is not None:
                    if key in ['change_percent', 'rate']:
                        # 百分比字段保留2位小数
                        item[key] = round(float(item[key]), 2) if item[key] is not None else None
                    elif key in ['current', 'open', 'pre_close', 'high', 'low', 'change']:
                        # 价格字段保留2位小数
                        item[key] = round(float(item[key]), 2) if item[key] is not None else None
                    else:
                        # 其他数值字段
                        item[key] = float(item[key]) if item[key] is not None else None
        
        print(f"✅ 成功获取 {len(data)} 条港股排行数据 (总数: {total})")
        return JSONResponse({
            'success': True, 
            'data': data, 
            'total': total, 
            'page': page, 
            'page_size': page_size
        })
        
    except Exception as e:
        print(f"❌ 获取港股排行数据失败: {str(e)}")
        tb = traceback.format_exc()
        print(tb)
        return JSONResponse({
            'success': False, 
            'message': '获取港股排行数据失败', 
            'error': str(e), 
            'traceback': tb
        }, status_code=500)

@router.get("/hk_indices")
def get_hk_indices():
    """
    获取港股指数模拟数据
    返回恒生指数、恒生科技指数等模拟数据
    """
    try:
        import random
        from datetime import datetime
        
        # 模拟港股指数数据
        indices_data = [
            {
                'code': 'HSI',
                'name': '恒生指数',
                'value': round(18000 + random.uniform(-500, 500), 2),
                'change': round(random.uniform(-200, 200), 2),
                'change_percent': round(random.uniform(-1.5, 1.5), 2)
            },
            {
                'code': 'HSTECH',
                'name': '恒生科技指数',
                'value': round(4500 + random.uniform(-200, 200), 2),
                'change': round(random.uniform(-80, 80), 2),
                'change_percent': round(random.uniform(-2.0, 2.0), 2)
            },
            {
                'code': 'HSCEI',
                'name': '恒生中国企业指数',
                'value': round(6500 + random.uniform(-300, 300), 2),
                'change': round(random.uniform(-150, 150), 2),
                'change_percent': round(random.uniform(-2.5, 2.5), 2)
            },
            {
                'code': 'HSCI',
                'name': '恒生综合指数',
                'value': round(2800 + random.uniform(-100, 100), 2),
                'change': round(random.uniform(-50, 50), 2),
                'change_percent': round(random.uniform(-2.0, 2.0), 2)
            }
        ]
        
        return JSONResponse({
            'success': True,
            'data': indices_data,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        print(f"❌ 获取港股指数数据失败: {str(e)}")
        tb = traceback.format_exc()
        print(tb)
        return JSONResponse({
            'success': False,
            'message': '获取港股指数数据失败',
            'error': str(e)
        }, status_code=500)

