# CSV报告生成器
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Any
from backend_core.database.db_manager import DatabaseManager

class CSVReportGenerator:
    """CSV报告生成器"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.report_dir = "reports/csv"
        
        # 确保报告目录存在
        os.makedirs(self.report_dir, exist_ok=True)
    
    def get_user_watchlist(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户自选股列表"""
        query = """
        SELECT ws.stock_code, s.stock_name, s.market
        FROM user_watchlist ws
        JOIN stocks s ON ws.stock_code = s.stock_code
        WHERE ws.user_id = %s AND ws.is_active = 1
        ORDER BY ws.created_at DESC
        """
        
        return self.db.query(query, (user_id,))
    
    def get_stock_history_data(self, stock_code: str, days: int = 30) -> List[Dict[str, Any]]:
        """获取股票历史数据"""
        query = """
        SELECT 
            trade_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            amount,
            change_amount,
            change_percent
        FROM stock_quotes
        WHERE stock_code = %s
        AND trade_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        ORDER BY trade_date DESC
        """
        
        return self.db.query(query, (stock_code, days))
    
    def get_stock_summary_data(self, stock_code: str) -> Dict[str, Any]:
        """获取股票汇总数据"""
        query = """
        SELECT 
            s.stock_name,
            s.market,
            sq.close_price as current_price,
            sq.change_amount,
            sq.change_percent,
            sq.volume,
            sq.amount,
            sq.trade_date
        FROM stocks s
        LEFT JOIN stock_quotes sq ON s.stock_code = sq.stock_code
        WHERE s.stock_code = %s
        ORDER BY sq.trade_date DESC
        LIMIT 1
        """
        
        result = self.db.query(query, (stock_code,))
        return result[0] if result else {}
    
    def generate_summary_report(self, user_id: int) -> str:
        """生成汇总报告（仅包含最新数据）"""
        watchlist = self.get_user_watchlist(user_id)
        
        if not watchlist:
            raise Exception("用户没有自选股")
        
        summary_data = []
        for stock in watchlist:
            stock_code = stock['stock_code']
            summary = self.get_stock_summary_data(stock_code)
            
            if summary:
                summary_data.append({
                    '股票代码': stock_code,
                    '股票名称': stock['stock_name'],
                    '市场': summary.get('market', ''),
                    '当前价格': summary.get('current_price', 0),
                    '涨跌额': summary.get('change_amount', 0),
                    '涨跌幅(%)': summary.get('change_percent', 0),
                    '成交量': summary.get('volume', 0),
                    '成交额': summary.get('amount', 0),
                    '最新交易日': summary.get('trade_date', '')
                })
        
        # 生成CSV文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stock_summary_{user_id}_{timestamp}.csv"
        filepath = os.path.join(self.report_dir, filename)
        
        df = pd.DataFrame(summary_data)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath
    
    def generate_detailed_report(self, user_id: int, days: int = 30) -> str:
        """生成详细报告（包含历史数据）"""
        watchlist = self.get_user_watchlist(user_id)
        
        if not watchlist:
            raise Exception("用户没有自选股")
        
        all_data = []
        summary_data = []
        
        for stock in watchlist:
            stock_code = stock['stock_code']
            stock_name = stock['stock_name']
            
            # 获取历史数据
            history_data = self.get_stock_history_data(stock_code, days)
            
            # 获取汇总数据
            summary = self.get_stock_summary_data(stock_code)
            
            # 处理历史数据
            for data in history_data:
                all_data.append({
                    '股票代码': stock_code,
                    '股票名称': stock_name,
                    '交易日期': data['trade_date'],
                    '开盘价': data['open_price'],
                    '最高价': data['high_price'],
                    '最低价': data['low_price'],
                    '收盘价': data['close_price'],
                    '成交量': data['volume'],
                    '成交额': data['amount'],
                    '涨跌额': data['change_amount'],
                    '涨跌幅(%)': data['change_percent']
                })
            
            # 处理汇总数据
            if summary:
                summary_data.append({
                    '股票代码': stock_code,
                    '股票名称': stock_name,
                    '市场': summary.get('market', ''),
                    '当前价格': summary.get('current_price', 0),
                    '涨跌额': summary.get('change_amount', 0),
                    '涨跌幅(%)': summary.get('change_percent', 0),
                    '成交量': summary.get('volume', 0),
                    '成交额': summary.get('amount', 0),
                    '最新交易日': summary.get('trade_date', '')
                })
        
        # 生成Excel文件，包含多个工作表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stock_report_{user_id}_{timestamp}.xlsx"
        filepath = os.path.join(self.report_dir, filename)
        
        # 创建Excel文件，包含多个工作表
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # 历史数据表
            if all_data:
                df_history = pd.DataFrame(all_data)
                df_history.to_excel(writer, sheet_name='历史数据', index=False)
            
            # 汇总数据表
            if summary_data:
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='股票汇总', index=False)
        
        return filepath
