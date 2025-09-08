#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资讯频道API路由
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, desc, func, or_
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from database import get_db
from models import StockNews

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/news", tags=["news_channel"])

@router.get("/categories")
async def get_news_categories(db: Session = Depends(get_db)):
    """获取资讯分类列表"""
    try:
        result = db.execute(text("""
            SELECT id, name, description, sort_order 
            FROM news_categories 
            WHERE is_active = TRUE 
            ORDER BY sort_order
        """))
        categories = result.fetchall()
        
        return JSONResponse({
            "success": True,
            "data": [
                {
                    "id": cat[0],
                    "name": cat[1],
                    "description": cat[2],
                    "sort_order": cat[3]
                }
                for cat in categories
            ]
        })
    except Exception as e:
        logger.error(f"获取分类失败: {e}")
        return JSONResponse({
            "success": False,
            "message": f"获取分类失败: {str(e)}"
        }, status_code=500)

@router.get("/list")
async def get_news_list(
    category_id: Optional[int] = Query(None, description="分类ID"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """获取资讯列表"""
    try:
        # 构建查询条件
        where_conditions = []
        params = {}
        
        if category_id and category_id != 1:  # 1表示"全部"
            where_conditions.append("category_id = :category_id")
            params["category_id"] = category_id
        
        if keyword:
            where_conditions.append("(title ILIKE :keyword OR content ILIKE :keyword)")
            params["keyword"] = f"%{keyword}%"
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # 分页参数
        offset = (page - 1) * page_size
        params["offset"] = offset
        params["limit"] = page_size
        
        # 查询总数
        count_sql = f"""
            SELECT COUNT(*) FROM stock_news 
            WHERE {where_clause}
        """
        total_result = db.execute(text(count_sql), params)
        total = total_result.scalar()
        
        # 查询数据
        data_sql = f"""
            SELECT id, title, summary, publish_time, source, read_count, 
                   is_hot, tags, image_url, category_id
            FROM stock_news 
            WHERE {where_clause}
            ORDER BY publish_time DESC
            OFFSET :offset LIMIT :limit
        """
        result = db.execute(text(data_sql), params)
        news_list = result.fetchall()
        
        return JSONResponse({
            "success": True,
            "data": {
                "items": [
                    {
                        "id": news[0],
                        "title": news[1],
                        "summary": news[2] or (news[1][:200] + "..." if len(news[1]) > 200 else news[1]),
                        "publish_time": str(news[3]) if news[3] else '',
                        "source": news[4] or '',
                        "read_count": news[5] or 0,
                        "is_hot": news[6] or False,
                        "tags": news[7] or [],
                        "image_url": news[8] or '',
                        "category_id": news[9]
                    }
                    for news in news_list
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        })
    except Exception as e:
        logger.error(f"获取资讯列表失败: {e}")
        return JSONResponse({
            "success": False,
            "message": f"获取资讯列表失败: {str(e)}"
        }, status_code=500)

@router.get("/hot")
async def get_hot_news(limit: int = Query(10, description="数量限制"), db: Session = Depends(get_db)):
    """获取热门资讯"""
    try:
        result = db.execute(text("""
            SELECT id, title, summary, publish_time, read_count, source, is_hot
            FROM stock_news 
            WHERE is_hot = TRUE
            ORDER BY read_count DESC
            LIMIT :limit
        """), {"limit": limit})
        hot_news = result.fetchall()
        
        return JSONResponse({
            "success": True,
            "data": [
                {
                    "id": news[0],
                    "title": news[1],
                    "summary": news[2] or news[1][:100] + "...",
                    "publish_time": str(news[3]) if news[3] else '',
                    "read_count": news[4] or 0,
                    "source": news[5] or '',
                    "is_hot": news[6] or False
                }
                for news in hot_news
            ]
        })
    except Exception as e:
        logger.error(f"获取热门资讯失败: {e}")
        return JSONResponse({
            "success": False,
            "message": f"获取热门资讯失败: {str(e)}"
        }, status_code=500)

@router.get("/detail/{news_id}")
async def get_news_detail(news_id: int, db: Session = Depends(get_db)):
    """获取资讯详情"""
    try:
        # 查询资讯详情
        result = db.execute(text("""
            SELECT id, title, content, summary, publish_time, source, url, 
                   read_count, tags, image_url, stock_code, category_id
            FROM stock_news 
            WHERE id = :news_id
        """), {"news_id": news_id})
        news = result.fetchone()
        
        if not news:
            return JSONResponse({
                "success": False,
                "message": "资讯不存在"
            }, status_code=404)
        
        # 增加阅读量
        db.execute(text("""
            UPDATE stock_news 
            SET read_count = COALESCE(read_count, 0) + 1 
            WHERE id = :news_id
        """), {"news_id": news_id})
        db.commit()
        
        return JSONResponse({
            "success": True,
            "data": {
                "id": news[0],
                "title": news[1],
                "content": news[2] or '',
                "summary": news[3] or '',
                "publish_time": str(news[4]) if news[4] else '',
                "source": news[5] or '',
                "url": news[6] or '',
                "read_count": (news[7] or 0) + 1,  # 显示更新后的阅读量
                "tags": news[8] or [],
                "image_url": news[9] or '',
                "stock_code": news[10] or '',
                "category_id": news[11]
            }
        })
    except Exception as e:
        logger.error(f"获取资讯详情失败: {e}")
        return JSONResponse({
            "success": False,
            "message": f"获取资讯详情失败: {str(e)}"
        }, status_code=500)

@router.get("/featured")
async def get_featured_news(db: Session = Depends(get_db)):
    """获取头条新闻（最新且阅读量较高的）"""
    try:
        result = db.execute(text("""
            SELECT id, title, summary, publish_time, source, read_count, is_hot
            FROM stock_news 
            ORDER BY publish_time DESC, read_count DESC
            LIMIT 1
        """))
        featured = result.fetchone()
        
        if not featured:
            return JSONResponse({
                "success": False,
                "message": "暂无头条新闻"
            }, status_code=404)
        
        return JSONResponse({
            "success": True,
            "data": {
                "id": featured[0],
                "title": featured[1],
                "summary": featured[2] or featured[1][:200] + "...",
                "publish_time": str(featured[3]) if featured[3] else '',
                "source": featured[4] or '',
                "read_count": featured[5] or 0,
                "is_hot": featured[6] or False
            }
        })
    except Exception as e:
        logger.error(f"获取头条新闻失败: {e}")
        return JSONResponse({
            "success": False,
            "message": f"获取头条新闻失败: {str(e)}"
        }, status_code=500)

@router.get("/search")
async def search_news(
    keyword: str = Query(..., description="搜索关键词"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
    db: Session = Depends(get_db)
):
    """搜索资讯"""
    try:
        # 构建查询条件
        where_conditions = ["(title ILIKE :keyword OR content ILIKE :keyword OR summary ILIKE :keyword)"]
        params = {"keyword": f"%{keyword}%"}
        
        if category_id and category_id != 1:
            where_conditions.append("category_id = :category_id")
            params["category_id"] = category_id
        
        where_clause = " AND ".join(where_conditions)
        
        # 分页参数
        offset = (page - 1) * page_size
        params["offset"] = offset
        params["limit"] = page_size
        
        # 查询总数
        count_sql = f"""
            SELECT COUNT(*) FROM stock_news 
            WHERE {where_clause}
        """
        total_result = db.execute(text(count_sql), params)
        total = total_result.scalar()
        
        # 查询数据
        data_sql = f"""
            SELECT id, title, summary, publish_time, source, read_count, 
                   is_hot, tags, image_url, category_id
            FROM stock_news 
            WHERE {where_clause}
            ORDER BY publish_time DESC
            OFFSET :offset LIMIT :limit
        """
        result = db.execute(text(data_sql), params)
        news_list = result.fetchall()
        
        return JSONResponse({
            "success": True,
            "data": {
                "items": [
                    {
                        "id": news[0],
                        "title": news[1],
                        "summary": news[2] or news[1][:200] + "...",
                        "publish_time": str(news[3]) if news[3] else '',
                        "source": news[4] or '',
                        "read_count": news[5] or 0,
                        "is_hot": news[6] or False,
                        "tags": news[7] or [],
                        "image_url": news[8] or '',
                        "category_id": news[9]
                    }
                    for news in news_list
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
                "keyword": keyword
            }
        })
    except Exception as e:
        logger.error(f"搜索资讯失败: {e}")
        return JSONResponse({
            "success": False,
            "message": f"搜索资讯失败: {str(e)}"
        }, status_code=500)

@router.get("/statistics")
async def get_news_statistics(db: Session = Depends(get_db)):
    """获取资讯统计信息"""
    try:
        # 总资讯数
        total_result = db.execute(text("SELECT COUNT(*) FROM stock_news"))
        total_news = total_result.scalar()
        
        # 今日资讯数
        today_result = db.execute(text("""
            SELECT COUNT(*) FROM stock_news 
            WHERE DATE(publish_time) = CURRENT_DATE
        """))
        today_news = today_result.scalar()
        
        # 热门资讯数
        hot_result = db.execute(text("SELECT COUNT(*) FROM stock_news WHERE is_hot = TRUE"))
        hot_news_count = hot_result.scalar()
        
        # 总阅读量
        reads_result = db.execute(text("SELECT SUM(COALESCE(read_count, 0)) FROM stock_news"))
        total_reads = reads_result.scalar() or 0
        
        # 分类统计
        category_result = db.execute(text("""
            SELECT nc.name, COUNT(sn.id) as count
            FROM news_categories nc
            LEFT JOIN stock_news sn ON nc.id = sn.category_id
            WHERE nc.is_active = TRUE
            GROUP BY nc.id, nc.name
            ORDER BY nc.sort_order
        """))
        category_stats = category_result.fetchall()
        
        return JSONResponse({
            "success": True,
            "data": {
                "total_news": total_news,
                "today_news": today_news,
                "hot_news_count": hot_news_count,
                "total_reads": total_reads,
                "category_stats": [
                    {"name": stat[0], "count": stat[1]}
                    for stat in category_stats
                ]
            }
        })
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return JSONResponse({
            "success": False,
        }, status_code=500)

@router.get("/homepage")
async def get_homepage_news(limit: int = Query(3, description="数量限制"), db: Session = Depends(get_db)):
    """获取首页市场资讯（最新3条）"""
    try:
        result = db.execute(text("""
            SELECT id, title, summary, publish_time, source, read_count
            FROM stock_news 
            ORDER BY publish_time DESC
            LIMIT :limit
        """), {"limit": limit})
        news_list = result.fetchall()
        
        return JSONResponse({
            "success": True,
            "data": [
                {
                    "id": news[0],
                    "title": news[1],
                    "summary": news[2] or news[1][:100] + "..." if len(news[1]) > 100 else news[1],
                    "publish_time": str(news[3]) if news[3] else '',
                    "source": news[4] or '',
                    "read_count": news[5] or 0
                }
                for news in news_list
            ]
        })
    except Exception as e:
        logger.error(f"获取首页市场资讯失败: {e}")
        return JSONResponse({
            "success": False,
            "message": f"获取首页市场资讯失败: {str(e)}"
        }, status_code=500)
