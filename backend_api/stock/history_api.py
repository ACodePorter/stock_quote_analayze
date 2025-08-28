import codecs
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend_api.database import get_db
from typing import List, Optional
import io
import csv
from sqlalchemy import text
from datetime import datetime

# 新增依赖
import pandas as pd
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font

router = APIRouter(prefix="/api/stock/history", tags=["StockHistory"])

def format_date_yyyymmdd(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    # 支持 "YYYY-MM-DD"、"YYYY/MM/DD"、"YYYY.MM.DD" 等
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    # 如果本身就是8位数字，尝试转为YYYY-MM-DD格式
    if len(date_str) == 8 and date_str.isdigit():
        try:
            return datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
        except Exception:
            pass
    return date_str  # fallback

@router.get("")
def get_stock_history(
    code: str = Query(...),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    include_notes: bool = Query(True, description="是否包含交易备注"),
    db: Session = Depends(get_db)
):
    start_date_fmt = format_date_yyyymmdd(start_date)
    end_date_fmt = format_date_yyyymmdd(end_date)
    print(f"[get_stock_history] 输入参数: code={code}, start_date={start_date_fmt}, end_date={end_date_fmt}, page={page}, size={size}, include_notes={include_notes}")
    
    if include_notes:
        # 使用视图查询，包含交易备注
        query = """
            SELECT 
                h.code, h.name, h.date, h.open, h.close, h.high, h.low, 
                h.volume, h.amount, h.change_percent, h.change, h.turnover_rate,
                h.cumulative_change_percent, h.five_day_change_percent, h.remarks,
                COALESCE(tn.notes, '') as user_notes,
                COALESCE(tn.strategy_type, '') as strategy_type,
                COALESCE(tn.risk_level, '') as risk_level,
                COALESCE(tn.created_by, '') as notes_creator,
                tn.created_at as notes_created_at,
                tn.updated_at as notes_updated_at
            FROM historical_quotes h
            LEFT JOIN trading_notes tn ON h.code = tn.stock_code AND h.date::date = tn.trade_date
            WHERE h.code = :code
        """
    else:
        # 只查询基础历史行情数据
        query = """
            SELECT 
                code, name, date, open, close, high, low, 
                volume, amount, change_percent, change, turnover_rate,
                cumulative_change_percent, five_day_change_percent, remarks
            FROM historical_quotes 
            WHERE code = :code
        """
    
    params = {"code": code}
    if start_date_fmt:
        query += " AND date >= :start_date"
        params["start_date"] = start_date_fmt
    if end_date_fmt:
        query += " AND date <= :end_date"
        params["end_date"] = end_date_fmt
    query += " ORDER BY date DESC"
    
    count_query = f"SELECT COUNT(*) FROM ({query})"
    total = db.execute(text(count_query), params).scalar()

    query += " LIMIT :limit OFFSET :offset"
    params["limit"] = size
    params["offset"] = (page - 1) * size
    result = db.execute(text(query), params)   
    
    items = []
    for row in result.fetchall():
        item = {
            "code": row[0],
            "name": row[1],
            "date": row[2],
            "open": row[3],
            "close": row[4],
            "high": row[5],
            "low": row[6],
            "volume": row[7],
            "amount": row[8],
            "change_percent": row[9],
            "change": row[10],
            "turnover_rate": row[11],
            "cumulative_change_percent": row[12],
            "five_day_change_percent": row[13],
            "remarks": row[14]
        }
        
        # 如果包含备注，添加备注相关字段
        if include_notes and len(row) > 15:
            item.update({
                "user_notes": row[15],
                "strategy_type": row[16],
                "risk_level": row[17],
                "notes_creator": row[18],
                "notes_created_at": row[19],
                "notes_updated_at": row[20]
            })
        
        items.append(item)
    
    print(f"[get_stock_history] 输出: total={total}, items_count={len(items)}")
    return {"items": items, "total": total}

@router.get("/export")
def export_stock_history(
    code: str = Query(...),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    include_notes: bool = Query(True, description="是否包含交易备注"),
    db: Session = Depends(get_db)
):
    start_date_fmt = format_date_yyyymmdd(start_date)
    end_date_fmt = format_date_yyyymmdd(end_date)
    print(f"[export_stock_history] 输入参数: code={code}, start_date={start_date_fmt}, end_date={end_date_fmt}, include_notes={include_notes}")
    
    # 简化查询，先获取基础数据
    base_query = """
        SELECT 
            code, name, date, open, close, high, low, 
            volume, amount, change_percent, change, turnover_rate,
            COALESCE(cumulative_change_percent, 0) as cumulative_change_percent, 
            COALESCE(five_day_change_percent, 0) as five_day_change_percent, 
            COALESCE(remarks, '') as remarks
        FROM historical_quotes 
        WHERE code = :code
    """
    
    params = {"code": code}
    if start_date_fmt:
        base_query += " AND date >= :start_date"
        params["start_date"] = start_date_fmt
    if end_date_fmt:
        base_query += " AND date <= :end_date"
        params["end_date"] = end_date_fmt
    base_query += " ORDER BY date DESC"
    
    result = db.execute(text(base_query), params)
    rows = result.fetchall()
    
    if not rows:
        raise HTTPException(status_code=404, detail="未找到数据")
    
    # 创建CSV内容
    output = io.StringIO()
    
    # 添加BOM头，解决Excel打开中文乱码问题
    output.write('\ufeff')
    
    writer = csv.writer(output)
    
    # 基础CSV头
    headers = [
        "股票代码", "股票名称", "日期", "开盘", "收盘", "最高", "最低",
        "成交量", "成交额", "涨跌幅%", "涨跌额", "换手率%",
        "累计升跌%", "5天升跌%", "备注"
    ]
    writer.writerow(headers)
    
    # 写入数据
    for row in rows:
        writer.writerow([
            row[0], row[1], row[2], row[3], row[4], row[5], row[6],
            row[7], row[8], row[9], row[10], row[11],
            row[12], row[13], row[14]
        ])
    
    output.seek(0)
    
    # 生成文件名
    filename = f"{code}_historical_quotes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )