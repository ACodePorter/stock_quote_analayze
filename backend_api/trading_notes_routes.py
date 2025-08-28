#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易备注管理API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from database import get_db
from models import TradingNotes, HistoricalQuotes
from sqlalchemy import text

router = APIRouter(prefix="/api/trading_notes", tags=["trading_notes"])

# Pydantic模型
class TradingNoteCreate(BaseModel):
    stock_code: str
    trade_date: date
    notes: Optional[str] = None
    strategy_type: Optional[str] = None
    risk_level: Optional[str] = None
    created_by: Optional[str] = None

class TradingNoteUpdate(BaseModel):
    notes: Optional[str] = None
    strategy_type: Optional[str] = None
    risk_level: Optional[str] = None

class TradingNoteResponse(BaseModel):
    id: int
    stock_code: str
    trade_date: date
    notes: Optional[str]
    strategy_type: Optional[str]
    risk_level: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

class HistoricalQuoteWithNotes(BaseModel):
    code: str
    name: Optional[str]
    date: date
    open: Optional[float]
    close: Optional[float]
    high: Optional[float]
    low: Optional[float]
    volume: Optional[int]
    amount: Optional[float]
    change_percent: Optional[float]
    change: Optional[float]
    turnover_rate: Optional[float]
    cumulative_change_percent: Optional[float]
    five_day_change_percent: Optional[float]
    remarks: Optional[str]
    # 交易备注信息
    user_notes: Optional[str]
    strategy_type: Optional[str]
    risk_level: Optional[str]
    notes_creator: Optional[str]
    notes_created_at: Optional[datetime]
    notes_updated_at: Optional[datetime]

    class Config:
        from_attributes = True

@router.post("/", response_model=TradingNoteResponse)
def create_trading_note(note: TradingNoteCreate, db: Session = Depends(get_db)):
    """创建交易备注"""
    try:
        # 检查是否已存在
        existing_note = db.query(TradingNotes).filter(
            TradingNotes.stock_code == note.stock_code,
            TradingNotes.trade_date == note.trade_date
        ).first()
        
        if existing_note:
            raise HTTPException(status_code=400, detail="该日期的交易备注已存在")
        
        # 创建新备注
        db_note = TradingNotes(
            stock_code=note.stock_code,
            trade_date=note.trade_date,
            notes=note.notes,
            strategy_type=note.strategy_type,
            risk_level=note.risk_level,
            created_by=note.created_by or "system"
        )
        
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        
        return db_note
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建交易备注失败: {str(e)}")

@router.get("/{stock_code}", response_model=List[TradingNoteResponse])
def get_trading_notes(
    stock_code: str,
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """获取指定股票的交易备注"""
    try:
        query = db.query(TradingNotes).filter(TradingNotes.stock_code == stock_code)
        
        if start_date:
            query = query.filter(TradingNotes.trade_date >= start_date)
        if end_date:
            query = query.filter(TradingNotes.trade_date <= end_date)
        
        notes = query.order_by(TradingNotes.trade_date.desc()).all()
        return notes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易备注失败: {str(e)}")

@router.put("/{note_id}", response_model=TradingNoteResponse)
def update_trading_note(
    note_id: int,
    note_update: TradingNoteUpdate,
    db: Session = Depends(get_db)
):
    """更新交易备注"""
    try:
        db_note = db.query(TradingNotes).filter(TradingNotes.id == note_id).first()
        if not db_note:
            raise HTTPException(status_code=404, detail="交易备注不存在")
        
        # 更新字段
        if note_update.notes is not None:
            db_note.notes = note_update.notes
        if note_update.strategy_type is not None:
            db_note.strategy_type = note_update.strategy_type
        if note_update.risk_level is not None:
            db_note.risk_level = note_update.risk_level
        
        db_note.updated_at = datetime.now()
        db.commit()
        db.refresh(db_note)
        
        return db_note
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新交易备注失败: {str(e)}")

@router.delete("/{note_id}")
def delete_trading_note(note_id: int, db: Session = Depends(get_db)):
    """删除交易备注"""
    try:
        db_note = db.query(TradingNotes).filter(TradingNotes.id == note_id).first()
        if not db_note:
            raise HTTPException(status_code=404, detail="交易备注不存在")
        
        db.delete(db_note)
        db.commit()
        
        return {"message": "交易备注删除成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除交易备注失败: {str(e)}")

@router.get("/{stock_code}/with_quotes", response_model=List[HistoricalQuoteWithNotes])
def get_historical_quotes_with_notes(
    stock_code: str,
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    include_notes: bool = Query(True, description="是否包含备注"),
    db: Session = Depends(get_db)
):
    """获取指定股票的历史行情数据（包含交易备注）"""
    try:
        if include_notes:
            # 使用视图查询
            query = f"""
                SELECT 
                    h.*,
                    COALESCE(tn.notes, '') as user_notes,
                    COALESCE(tn.strategy_type, '') as strategy_type,
                    COALESCE(tn.risk_level, '') as risk_level,
                    COALESCE(tn.created_by, '') as notes_creator,
                    tn.created_at as notes_created_at,
                    tn.updated_at as notes_updated_at
                FROM historical_quotes h
                LEFT JOIN trading_notes tn ON h.code = tn.stock_code AND h.date::date = tn.trade_date
                WHERE h.code = :stock_code
            """
            
            params = {"stock_code": stock_code}
            if start_date:
                query += " AND h.date::date >= :start_date"
                params["start_date"] = start_date
            if end_date:
                query += " AND h.date::date <= :end_date"
                params["end_date"] = end_date
            
            query += " ORDER BY h.date DESC"
            
            result = db.execute(text(query), params)
            rows = result.fetchall()
            
            # 转换为响应模型
            quotes_with_notes = []
            for row in rows:
                quote_data = dict(row._mapping)
                quotes_with_notes.append(HistoricalQuoteWithNotes(**quote_data))
            
            return quotes_with_notes
        else:
            # 只查询历史行情数据
            query = db.query(HistoricalQuotes).filter(HistoricalQuotes.code == stock_code)
            
            if start_date:
                query = query.filter(HistoricalQuotes.date >= start_date)
            if end_date:
                query = query.filter(HistoricalQuotes.date <= end_date)
            
            quotes = query.order_by(HistoricalQuotes.date.desc()).all()
            
            # 转换为响应模型
            quotes_with_notes = []
            for quote in quotes:
                quote_data = {
                    "code": quote.code,
                    "name": quote.name,
                    "date": quote.date,
                    "open": quote.open,
                    "close": quote.close,
                    "high": quote.high,
                    "low": quote.low,
                    "volume": quote.volume,
                    "amount": quote.amount,
                    "change_percent": quote.change_percent,
                    "change": quote.change,
                    "turnover_rate": quote.turnover_rate,
                    "cumulative_change_percent": quote.cumulative_change_percent,
                    "five_day_change_percent": quote.five_day_change_percent,
                    "remarks": quote.remarks,
                    "user_notes": None,
                    "strategy_type": None,
                    "risk_level": None,
                    "notes_creator": None,
                    "notes_created_at": None,
                    "notes_updated_at": None
                }
                quotes_with_notes.append(HistoricalQuoteWithNotes(**quote_data))
            
            return quotes_with_notes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史行情数据失败: {str(e)}")

@router.post("/{stock_code}/calculate_fields")
def calculate_derived_fields(
    stock_code: str,
    base_date: Optional[date] = Query(None, description="基准日期（累计升跌%计算用）"),
    db: Session = Depends(get_db)
):
    """计算派生字段：累计升跌%和5天升跌%"""
    try:
        # 计算累计升跌%
        if base_date:
            base_quote = db.query(HistoricalQuotes).filter(
                HistoricalQuotes.code == stock_code,
                HistoricalQuotes.date == base_date
            ).first()
            
            if base_quote and base_quote.close:
                base_price = base_quote.close
                
                # 更新所有日期的累计升跌%
                quotes = db.query(HistoricalQuotes).filter(
                    HistoricalQuotes.code == stock_code
                ).all()
                
                for quote in quotes:
                    if quote.close and base_price > 0:
                        quote.cumulative_change_percent = ((quote.close - base_price) / base_price) * 100
                
                db.commit()
        
        # 计算5天升跌%
        quotes = db.query(HistoricalQuotes).filter(
            HistoricalQuotes.code == stock_code
        ).order_by(HistoricalQuotes.date).all()
        
        for i, quote in enumerate(quotes):
            if i >= 5:  # 从第6天开始计算
                prev_quote = quotes[i-5]
                if quote.close and prev_quote.close and prev_quote.close > 0:
                    quote.five_day_change_percent = ((quote.close - prev_quote.close) / prev_quote.close) * 100
        
        db.commit()
        
        return {
            "message": "派生字段计算完成",
            "stock_code": stock_code,
            "base_date": base_date.isoformat() if base_date else None,
            "updated_records": len(quotes)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"计算派生字段失败: {str(e)}")

@router.get("/strategy_types")
def get_strategy_types():
    """获取可用的策略类型"""
    return {
        "strategy_types": [
            "买入信号",
            "卖出信号", 
            "观察",
            "持有",
            "加仓",
            "减仓",
            "止损",
            "止盈"
        ],
        "risk_levels": [
            "低",
            "中",
            "高"
        ]
    }
