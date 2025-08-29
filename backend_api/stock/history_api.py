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
from pydantic import BaseModel

# 新增依赖
import pandas as pd
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font

router = APIRouter(prefix="/api/stock/history", tags=["StockHistory"])

# 计算5天升跌请求模型
class CalculateFiveDayChangeRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str

def format_date_yyyymmdd(date_str: Optional[str]) -> str:
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
    
    # 根据是否包含备注选择不同的查询
    if include_notes:
        # 包含备注的查询，关联trading_notes表
        base_query = """
            SELECT 
                hq.code, hq.name, hq.date, hq.open, hq.close, hq.high, hq.low, 
                hq.volume, hq.amount, hq.change_percent, hq.change, hq.turnover_rate,
                COALESCE(hq.cumulative_change_percent, 0) as cumulative_change_percent, 
                COALESCE(hq.five_day_change_percent, 0) as five_day_change_percent,
                COALESCE(tn.notes, '') as user_notes,
                COALESCE(tn.strategy_type, '') as strategy_type,
                COALESCE(tn.risk_level, '') as risk_level
            FROM historical_quotes hq
            LEFT JOIN trading_notes tn ON hq.code = tn.stock_code AND CAST(hq.date AS DATE) = CAST(tn.trade_date AS DATE)
            WHERE hq.code = :code
        """
    else:
        # 不包含备注的查询
        base_query = """
            SELECT 
                code, name, date, open, close, high, low, 
                volume, amount, change_percent, change, turnover_rate,
                COALESCE(cumulative_change_percent, 0) as cumulative_change_percent, 
                COALESCE(five_day_change_percent, 0) as five_day_change_percent,
                '' as user_notes,
                '' as strategy_type,
                '' as risk_level
            FROM historical_quotes 
            WHERE code = :code
        """
    
    params = {"code": code}
    if start_date_fmt:
        base_query += " AND hq.date >= :start_date" if include_notes else " AND date >= :start_date"
        params["start_date"] = start_date_fmt
    if end_date_fmt:
        base_query += " AND hq.date <= :end_date" if include_notes else " AND date <= :end_date"
        params["end_date"] = end_date_fmt
    base_query += " ORDER BY hq.date DESC" if include_notes else " ORDER BY date DESC"
    
    try:
        result = db.execute(text(base_query), params)
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="未找到数据")
        
        # 检查是否有备注数据
        has_notes_data = False
        if include_notes:
            try:
                # 首先检查trading_notes表是否存在
                table_check_query = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'trading_notes'
                    );
                """
                table_exists = db.execute(text(table_check_query)).scalar()
                
                if not table_exists:
                    print(f"[export_stock_history] trading_notes表不存在，跳过备注查询")
                    has_notes_data = False
                else:
                    # 检查是否有任何备注数据
                    notes_check_query = """
                        SELECT COUNT(*) FROM trading_notes 
                        WHERE stock_code = :code 
                        AND (user_notes IS NOT NULL AND user_notes != '')
                    """
                    notes_count = db.execute(text(notes_check_query), {"code": code}).scalar()
                    has_notes_data = notes_count > 0
                    print(f"[export_stock_history] 备注数据检查: 找到 {notes_count} 条有备注的记录")
                    
            except Exception as e:
                print(f"[export_stock_history] 检查备注数据时出错: {e}")
                has_notes_data = False
        
        # 创建CSV内容
        output = io.StringIO()
        
        # 添加BOM头，解决Excel打开中文乱码问题
        output.write('\ufeff')
        
        writer = csv.writer(output)
        
        # 根据是否有备注数据设置不同的CSV头
        if include_notes and has_notes_data:
            headers = [
                "股票代码", "股票名称", "日期", "开盘", "收盘", "最高", "最低",
                "成交量", "成交额", "涨跌幅%", "涨跌额", "换手率%",
                "累计升跌%", "5天升跌%", "用户备注", "策略类型", "风险等级"
            ]
        else:
            headers = [
                "股票代码", "股票名称", "日期", "开盘", "收盘", "最高", "最低",
                "成交量", "成交额", "涨跌幅%", "涨跌额", "换手率%",
                "累计升跌%", "5天升跌%", "备注"
            ]
        
        writer.writerow(headers)
        
        # 写入数据
        for row in rows:
            if include_notes and has_notes_data:
                # 包含备注的数据
                writer.writerow([
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                    row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13], row[14], row[15], row[16]
                ])
            else:
                # 不包含备注的数据
                writer.writerow([
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                    row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13], row[14]
                ])
        
        output.seek(0)
        
        # 生成文件名
        filename = f"{code}_historical_quotes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        print(f"[export_stock_history] 导出成功: {len(rows)} 条记录, 包含备注: {include_notes and has_notes_data}")
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"导出失败: {str(e)}"
        print(f"[export_stock_history] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/calculate_five_day_change")
def calculate_five_day_change(
    request: CalculateFiveDayChangeRequest,
    db: Session = Depends(get_db)
):
    """计算指定日期范围内股票的5天升跌%"""
    try:
        # 格式化日期
        start_date_fmt = format_date_yyyymmdd(request.start_date)
        end_date_fmt = format_date_yyyymmdd(request.end_date)
        
        if not start_date_fmt or not end_date_fmt:
            raise HTTPException(status_code=400, detail="日期格式无效")
        
        print(f"[calculate_five_day_change] 开始计算股票 {request.stock_code} 在 {start_date_fmt} 到 {end_date_fmt} 期间的5天升跌%")
        
        # 为了确保最后5条记录也能计算5天升跌%，需要延长查询范围
        # 查询指定日期范围内的所有历史数据，按日期排序
        # 注意：这里不需要额外的日期范围扩展，因为我们需要的是前5天的数据
        query = """
            SELECT date, close
            FROM historical_quotes 
            WHERE code = :stock_code 
            AND date >= :start_date 
            AND date <= :end_date
            ORDER BY date ASC
        """
        
        result = db.execute(text(query), {
            "stock_code": request.stock_code,
            "start_date": start_date_fmt,
            "end_date": end_date_fmt
        })
        
        quotes = result.fetchall()
        
        if len(quotes) < 6:
            raise HTTPException(status_code=400, detail="数据不足6天，无法计算5天升跌%")
        
        # 计算5天升跌%
        updated_count = 0
        for i in range(5, len(quotes)):
            current_quote = quotes[i]
            prev_quote = quotes[i-5]  # 5天前的数据
            
            if current_quote.close and prev_quote.close and prev_quote.close > 0:
                five_day_change = ((current_quote.close - prev_quote.close) / prev_quote.close) * 100
                five_day_change = round(five_day_change, 2)
                
                # 更新数据库，不管之前是否有值都更新
                update_query = """
                    UPDATE historical_quotes 
                    SET five_day_change_percent = :five_day_change
                    WHERE code = :stock_code AND date = :date
                """
                
                db.execute(text(update_query), {
                    "five_day_change": five_day_change,
                    "stock_code": request.stock_code,
                    "date": current_quote.date
                })
                
                updated_count += 1
        
        # 提交事务
        db.commit()
        
        message = f"股票 {request.stock_code} 在 {start_date_fmt} 到 {end_date_fmt} 期间的5天升跌%计算完成"
        print(f"[calculate_five_day_change] {message}, 更新了 {updated_count} 条记录")
        
        return {
            "message": message,
            "stock_code": request.stock_code,
            "start_date": start_date_fmt,
            "end_date": end_date_fmt,
            "updated_count": updated_count,
            "total_records": len(quotes)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_msg = f"计算5天升跌%失败: {str(e)}"
        print(f"[calculate_five_day_change] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)