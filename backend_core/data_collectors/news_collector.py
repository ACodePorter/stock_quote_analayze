#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资讯数据采集器
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import re
import time
from backend_core.database.db import SessionLocal
from sqlalchemy import text

logger = logging.getLogger(__name__)

class NewsCollector:
    """资讯数据采集器"""
    
    def __init__(self):
        self.session = SessionLocal()
    
    def collect_market_news(self) -> List[Dict]:
        """采集市场新闻"""
        try:
            logger.info("开始采集市场新闻...")
            
            # 使用akshare获取财经新闻
            news_df = ak.stock_news_em()
            
            if news_df is None or news_df.empty:
                logger.warning("akshare返回空数据")
                return []
            
            logger.info(f"akshare返回 {len(news_df)} 条原始新闻数据")
            
            news_list = []
            for _, row in news_df.iterrows():
                try:
                    title = str(row.get('新闻标题', '') or row.get('标题', '') or '').strip()
                    content = str(row.get('新闻内容', '') or row.get('内容', '') or '').strip()
                    
                    if not title or not content:
                        continue
                    
                    # 处理发布时间
                    publish_time = row.get('发布时间', '') or row.get('时间', '')
                    if pd.isna(publish_time) or not publish_time:
                        publish_time = datetime.now()
                    else:
                        if hasattr(publish_time, 'strftime'):
                            publish_time = publish_time
                        else:
                            try:
                                publish_time = datetime.strptime(str(publish_time), '%Y-%m-%d %H:%M:%S')
                            except:
                                publish_time = datetime.now()
                    
                    news_item = {
                        'title': title,
                        'content': content,
                        'publish_time': publish_time,
                        'source': str(row.get('文章来源', '') or '东方财富').strip(),
                        'url': str(row.get('新闻链接', '') or '').strip(),
                        'category_id': self._classify_news(title, content),
                        'summary': self._extract_summary(content),
                        'tags': self._extract_tags(title, content),
                        'read_count': 0,
                        'is_hot': False,
                        'stock_code': None,  # 市场新闻不关联特定股票
                        'image_url': None
                    }
                    news_list.append(news_item)
                    
                except Exception as e:
                    logger.error(f"处理单条新闻失败: {e}")
                    continue
            
            logger.info(f"成功处理 {len(news_list)} 条新闻")
            return news_list
            
        except Exception as e:
            logger.error(f"采集市场新闻失败: {e}")
            return []
    
    def collect_stock_news(self, stock_code: str) -> List[Dict]:
        """采集特定股票的新闻"""
        try:
            logger.info(f"开始采集股票 {stock_code} 的新闻...")
            
            # 使用akshare获取股票新闻
            news_df = ak.stock_news_em(symbol=stock_code)
            
            if news_df is None or news_df.empty:
                logger.warning(f"股票 {stock_code} 无新闻数据")
                return []
            
            logger.info(f"股票 {stock_code} 返回 {len(news_df)} 条新闻数据")
            
            news_list = []
            for _, row in news_df.iterrows():
                try:
                    title = str(row.get('新闻标题', '') or row.get('标题', '') or '').strip()
                    content = str(row.get('新闻内容', '') or row.get('内容', '') or '').strip()
                    
                    if not title or not content:
                        continue
                    
                    # 处理发布时间
                    publish_time = row.get('发布时间', '') or row.get('时间', '')
                    if pd.isna(publish_time) or not publish_time:
                        publish_time = datetime.now()
                    else:
                        if hasattr(publish_time, 'strftime'):
                            publish_time = publish_time
                        else:
                            try:
                                publish_time = datetime.strptime(str(publish_time), '%Y-%m-%d %H:%M:%S')
                            except:
                                publish_time = datetime.now()
                    
                    news_item = {
                        'title': title,
                        'content': content,
                        'publish_time': publish_time,
                        'source': str(row.get('文章来源', '') or '东方财富').strip(),
                        'url': str(row.get('新闻链接', '') or '').strip(),
                        'category_id': self._classify_news(title, content),
                        'summary': self._extract_summary(content),
                        'tags': self._extract_tags(title, content),
                        'read_count': 0,
                        'is_hot': False,
                        'stock_code': stock_code,
                        'image_url': None
                    }
                    news_list.append(news_item)
                    
                except Exception as e:
                    logger.error(f"处理股票 {stock_code} 单条新闻失败: {e}")
                    continue
            
            logger.info(f"股票 {stock_code} 成功处理 {len(news_list)} 条新闻")
            return news_list
            
        except Exception as e:
            logger.error(f"采集股票 {stock_code} 新闻失败: {e}")
            return []
    
    def _classify_news(self, title: str, content: str) -> int:
        """根据标题和内容分类新闻"""
        try:
            text = (title + " " + content).lower()
            
            # 政策解读
            policy_keywords = ['政策', '监管', '央行', '证监会', '银保监会', '财政部', '发改委', '降准', '降息', '利率']
            if any(keyword in text for keyword in policy_keywords):
                return 3
            
            # 公司资讯
            company_keywords = ['公司', '财报', '公告', '业绩', '年报', '季报', '分红', '增持', '减持', '重组', '并购']
            if any(keyword in text for keyword in company_keywords):
                return 4
            
            # 国际财经
            international_keywords = ['美股', '港股', '外汇', '国际', '美元', '欧元', '日元', '原油', '黄金', '期货']
            if any(keyword in text for keyword in international_keywords):
                return 5
            
            # 分析研判
            analysis_keywords = ['分析', '预测', '研判', '投资', '策略', '建议', '评级', '目标价', '研报']
            if any(keyword in text for keyword in analysis_keywords):
                return 6
            
            # 默认为市场动态
            return 2
            
        except Exception as e:
            logger.error(f"分类新闻失败: {e}")
            return 2
    
    def _extract_summary(self, content: str) -> str:
        """提取摘要"""
        try:
            if not content:
                return ""
            
            # 移除HTML标签
            content = re.sub(r'<[^>]+>', '', content)
            
            # 移除多余空白
            content = re.sub(r'\s+', ' ', content).strip()
            
            if len(content) <= 200:
                return content
            
            # 尝试在句号处截断
            sentences = content.split('。')
            summary = ""
            for sentence in sentences:
                if len(summary + sentence) <= 200:
                    summary += sentence + "。"
                else:
                    break
            
            if summary:
                return summary.strip()
            
            # 如果无法在句号处截断，直接截取200字符
            return content[:200] + "..."
            
        except Exception as e:
            logger.error(f"提取摘要失败: {e}")
            return content[:200] + "..." if len(content) > 200 else content
    
    def _extract_tags(self, title: str, content: str) -> List[str]:
        """提取标签"""
        try:
            text = (title + " " + content).lower()
            tags = []
            
            # 行业标签
            industry_tags = {
                '科技': ['科技', 'ai', '人工智能', '芯片', '半导体', '5g', '物联网'],
                '新能源': ['新能源', '汽车', '电池', '光伏', '风电', '储能', '电动车'],
                '金融': ['银行', '金融', '保险', '证券', '基金', '理财'],
                '医药': ['医药', '生物', '疫苗', '医疗', '健康', '制药'],
                '地产': ['地产', '房地产', '建筑', '物业', '土地'],
                '消费': ['消费', '零售', '食品', '饮料', '服装', '家电'],
                '军工': ['军工', '国防', '航空', '航天', '船舶'],
                '教育': ['教育', '培训', '学校', '在线教育'],
                '传媒': ['传媒', '影视', '游戏', '广告', '出版']
            }
            
            for tag, keywords in industry_tags.items():
                if any(keyword in text for keyword in keywords):
                    tags.append(tag)
            
            # 概念标签
            concept_tags = {
                '政策': ['政策', '监管', '改革'],
                '业绩': ['业绩', '财报', '盈利'],
                '并购': ['并购', '重组', '收购'],
                '分红': ['分红', '派息', '送股'],
                '增持': ['增持', '减持', '回购']
            }
            
            for tag, keywords in concept_tags.items():
                if any(keyword in text for keyword in keywords):
                    tags.append(tag)
            
            # 限制标签数量
            return tags[:5]
            
        except Exception as e:
            logger.error(f"提取标签失败: {e}")
            return []
    
    def save_news_to_db(self, news_list: List[Dict]) -> int:
        """保存新闻到数据库"""
        if not news_list:
            return 0
        
        saved_count = 0
        try:
            for news in news_list:
                try:
                    # 检查是否已存在（基于标题和发布时间）
                    # 将datetime对象转换为字符串
                    publish_time_str = news['publish_time'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(news['publish_time'], datetime) else str(news['publish_time'])
                    existing = self.session.execute(text("""
                        SELECT id FROM stock_news 
                        WHERE title = :title AND publish_time = :publish_time
                    """), {
                        'title': news['title'],
                        'publish_time': publish_time_str
                    }).fetchone()
                    
                    if not existing:
                        # 插入新新闻
                        # 准备插入数据，确保publish_time是字符串格式
                        insert_data = news.copy()
                        insert_data['publish_time'] = publish_time_str
                        self.session.execute(text("""
                            INSERT INTO stock_news 
                            (title, content, publish_time, source, url, category_id, 
                             summary, tags, read_count, is_hot, stock_code, image_url)
                            VALUES (:title, :content, :publish_time, :source, :url, :category_id,
                                    :summary, :tags, :read_count, :is_hot, :stock_code, :image_url)
                        """), insert_data)
                        saved_count += 1
                        
                except Exception as e:
                    logger.error(f"保存单条新闻失败: {e}")
                    continue
            
            self.session.commit()
            logger.info(f"成功保存 {saved_count} 条新闻到数据库")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"保存新闻到数据库失败: {e}")
        
        return saved_count
    
    def update_hot_news(self) -> bool:
        """更新热门资讯标记"""
        try:
            # 调用数据库函数更新热门标记
            self.session.execute(text("SELECT update_hot_news_mark()"))
            self.session.commit()
            logger.info("热门资讯标记更新完成")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"更新热门资讯失败: {e}")
            return False
    
    def collect_and_save_market_news(self) -> Dict:
        """采集并保存市场新闻"""
        try:
            # 采集新闻
            news_list = self.collect_market_news()
            
            # 保存到数据库
            saved_count = self.save_news_to_db(news_list)
            
            # 更新热门标记
            self.update_hot_news()
            
            return {
                "success": True,
                "collected": len(news_list),
                "saved": saved_count,
                "message": f"采集 {len(news_list)} 条新闻，保存 {saved_count} 条"
            }
            
        except Exception as e:
            logger.error(f"采集并保存市场新闻失败: {e}")
            return {
                "success": False,
                "message": f"采集失败: {str(e)}"
            }
    
    def collect_and_save_stock_news(self, stock_code: str) -> Dict:
        """采集并保存股票新闻"""
        try:
            # 采集新闻
            news_list = self.collect_stock_news(stock_code)
            
            # 保存到数据库
            saved_count = self.save_news_to_db(news_list)
            
            return {
                "success": True,
                "stock_code": stock_code,
                "collected": len(news_list),
                "saved": saved_count,
                "message": f"股票 {stock_code} 采集 {len(news_list)} 条新闻，保存 {saved_count} 条"
            }
            
        except Exception as e:
            logger.error(f"采集并保存股票 {stock_code} 新闻失败: {e}")
            return {
                "success": False,
                "stock_code": stock_code,
                "message": f"采集失败: {str(e)}"
            }
    
    def cleanup_old_news(self, days: int = 30) -> int:
        """清理旧新闻"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            result = self.session.execute(text("""
                DELETE FROM stock_news 
                WHERE publish_time < :cutoff_date
            """), {"cutoff_date": cutoff_date})
            
            deleted_count = result.rowcount
            self.session.commit()
            
            logger.info(f"清理了 {deleted_count} 条 {days} 天前的旧新闻")
            return deleted_count
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"清理旧新闻失败: {e}")
            return 0
    
    def close(self):
        """关闭数据库连接"""
        if self.session:
            self.session.close()

# 便捷函数
def collect_market_news() -> Dict:
    """采集市场新闻的便捷函数"""
    collector = NewsCollector()
    try:
        return collector.collect_and_save_market_news()
    finally:
        collector.close()

def collect_stock_news(stock_code: str) -> Dict:
    """采集股票新闻的便捷函数"""
    collector = NewsCollector()
    try:
        return collector.collect_and_save_stock_news(stock_code)
    finally:
        collector.close()

if __name__ == "__main__":
    # 测试采集功能
    collector = NewsCollector()
    try:
        result = collector.collect_and_save_market_news()
        print(f"采集结果: {result}")
    finally:
        collector.close()
