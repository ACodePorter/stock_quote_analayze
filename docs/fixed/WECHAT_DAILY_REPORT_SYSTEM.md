# 每日股票行情报告微信发送系统

## 1. 企业微信API集成

### 1.1 企业微信配置类
```python
# backend_core/wechat/wechat_config.py
import os
from typing import Optional

class WeChatConfig:
    """企业微信配置"""
    
    def __init__(self):
        self.corp_id = os.getenv('WECHAT_CORP_ID')
        self.corp_secret = os.getenv('WECHAT_CORP_SECRET')
        self.agent_id = os.getenv('WECHAT_AGENT_ID')
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[int] = None
    
    def get_access_token(self) -> str:
        """获取企业微信访问令牌"""
        import requests
        import time
        
        if self.access_token and self.token_expires_at and time.time() < self.token_expires_at:
            return self.access_token
        
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            'corpid': self.corp_id,
            'corpsecret': self.corp_secret
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('errcode') == 0:
            self.access_token = data['access_token']
            self.token_expires_at = time.time() + data['expires_in'] - 60  # 提前1分钟过期
            return self.access_token
        else:
            raise Exception(f"获取企业微信访问令牌失败: {data}")
```

### 1.2 企业微信消息发送服务
```python
# backend_core/wechat/wechat_service.py
import requests
import json
from typing import List, Dict, Any
from .wechat_config import WeChatConfig

class WeChatService:
    """企业微信服务"""
    
    def __init__(self):
        self.config = WeChatConfig()
    
    def send_text_message(self, user_ids: List[str], content: str) -> bool:
        """发送文本消息"""
        access_token = self.config.get_access_token()
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        
        data = {
            "touser": "|".join(user_ids),
            "msgtype": "text",
            "agentid": self.config.agent_id,
            "text": {
                "content": content
            }
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        return result.get('errcode') == 0
    
    def send_file_message(self, user_ids: List[str], file_path: str, file_name: str) -> bool:
        """发送文件消息"""
        # 1. 上传文件获取media_id
        media_id = self._upload_file(file_path)
        if not media_id:
            return False
        
        # 2. 发送文件消息
        access_token = self.config.get_access_token()
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        
        data = {
            "touser": "|".join(user_ids),
            "msgtype": "file",
            "agentid": self.config.agent_id,
            "file": {
                "media_id": media_id
            }
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        return result.get('errcode') == 0
    
    def _upload_file(self, file_path: str) -> Optional[str]:
        """上传文件获取media_id"""
        access_token = self.config.get_access_token()
        url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=file"
        
        with open(file_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(url, files=files)
        
        result = response.json()
        if result.get('errcode') == 0:
            return result['media_id']
        else:
            print(f"文件上传失败: {result}")
            return None
```

## 2. CSV文件生成服务

### 2.1 股票数据收集服务
```python
# backend_core/reports/stock_data_collector.py
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from backend_core.database.db_manager import DatabaseManager

class StockDataCollector:
    """股票数据收集器"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
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
```

### 2.2 CSV报告生成器
```python
# backend_core/reports/csv_report_generator.py
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Any
from .stock_data_collector import StockDataCollector

class CSVReportGenerator:
    """CSV报告生成器"""
    
    def __init__(self):
        self.data_collector = StockDataCollector()
        self.report_dir = "reports/csv"
        
        # 确保报告目录存在
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_daily_report(self, user_id: int, days: int = 30) -> str:
        """生成每日报告"""
        # 1. 获取用户自选股
        watchlist = self.data_collector.get_user_watchlist(user_id)
        
        if not watchlist:
            raise Exception("用户没有自选股")
        
        # 2. 收集所有股票数据
        all_data = []
        summary_data = []
        
        for stock in watchlist:
            stock_code = stock['stock_code']
            stock_name = stock['stock_name']
            
            # 获取历史数据
            history_data = self.data_collector.get_stock_history_data(stock_code, days)
            
            # 获取汇总数据
            summary = self.data_collector.get_stock_summary_data(stock_code)
            
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
        
        # 3. 生成CSV文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stock_report_{user_id}_{timestamp}.csv"
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
    
    def generate_summary_report(self, user_id: int) -> str:
        """生成汇总报告（仅包含最新数据）"""
        watchlist = self.data_collector.get_user_watchlist(user_id)
        
        if not watchlist:
            raise Exception("用户没有自选股")
        
        summary_data = []
        for stock in watchlist:
            stock_code = stock['stock_code']
            summary = self.data_collector.get_stock_summary_data(stock_code)
            
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
```

## 3. 定时任务调度

### 3.1 定时任务服务
```python
# backend_core/scheduler/daily_report_scheduler.py
import schedule
import time
from datetime import datetime
from backend_core.reports.csv_report_generator import CSVReportGenerator
from backend_core.wechat.wechat_service import WeChatService
from backend_core.database.db_manager import DatabaseManager

class DailyReportScheduler:
    """每日报告调度器"""
    
    def __init__(self):
        self.report_generator = CSVReportGenerator()
        self.wechat_service = WeChatService()
        self.db = DatabaseManager()
    
    def get_active_users(self) -> List[Dict[str, Any]]:
        """获取活跃用户列表"""
        query = """
        SELECT DISTINCT u.user_id, u.username, u.wechat_user_id
        FROM users u
        JOIN user_watchlist w ON u.user_id = w.user_id
        WHERE u.is_active = 1 
        AND w.is_active = 1
        AND u.wechat_user_id IS NOT NULL
        AND u.wechat_user_id != ''
        """
        
        return self.db.query(query)
    
    def send_daily_report(self):
        """发送每日报告"""
        print(f"[{datetime.now()}] 开始发送每日股票报告...")
        
        try:
            # 获取活跃用户
            users = self.get_active_users()
            
            if not users:
                print("没有找到需要发送报告的用户")
                return
            
            success_count = 0
            error_count = 0
            
            for user in users:
                try:
                    user_id = user['user_id']
                    username = user['username']
                    wechat_user_id = user['wechat_user_id']
                    
                    print(f"为用户 {username} (ID: {user_id}) 生成报告...")
                    
                    # 生成报告文件
                    report_file = self.report_generator.generate_summary_report(user_id)
                    
                    # 发送到微信
                    success = self.wechat_service.send_file_message(
                        user_ids=[wechat_user_id],
                        file_path=report_file,
                        file_name=f"每日股票报告_{datetime.now().strftime('%Y%m%d')}.csv"
                    )
                    
                    if success:
                        print(f"✓ 用户 {username} 报告发送成功")
                        success_count += 1
                    else:
                        print(f"✗ 用户 {username} 报告发送失败")
                        error_count += 1
                    
                    # 清理临时文件
                    import os
                    if os.path.exists(report_file):
                        os.remove(report_file)
                    
                except Exception as e:
                    print(f"✗ 用户 {user['username']} 报告生成失败: {str(e)}")
                    error_count += 1
            
            print(f"每日报告发送完成: 成功 {success_count} 个，失败 {error_count} 个")
            
        except Exception as e:
            print(f"每日报告发送过程中发生错误: {str(e)}")
    
    def start_scheduler(self):
        """启动调度器"""
        # 每天上午9:30发送报告（股市开盘前）
        schedule.every().day.at("09:30").do(self.send_daily_report)
        
        # 每天下午15:30发送报告（股市收盘后）
        schedule.every().day.at("15:30").do(self.send_daily_report)
        
        print("每日股票报告调度器已启动")
        print("发送时间: 每天 09:30 和 15:30")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
```

## 4. 用户微信绑定管理

### 4.1 用户微信绑定API
```python
# backend_api/user/wechat_binding_api.py
from flask import Blueprint, request, jsonify
from backend_core.database.db_manager import DatabaseManager
from backend_core.wechat.wechat_service import WeChatService

wechat_binding_bp = Blueprint('wechat_binding', __name__)

@wechat_binding_bp.route('/api/user/bind-wechat', methods=['POST'])
def bind_wechat():
    """绑定用户微信"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        wechat_user_id = data.get('wechat_user_id')
        
        if not user_id or not wechat_user_id:
            return jsonify({'success': False, 'message': '参数不完整'}), 400
        
        # 更新用户微信绑定
        db = DatabaseManager()
        query = "UPDATE users SET wechat_user_id = %s WHERE user_id = %s"
        db.execute(query, (wechat_user_id, user_id))
        
        return jsonify({'success': True, 'message': '微信绑定成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'绑定失败: {str(e)}'}), 500

@wechat_binding_bp.route('/api/user/unbind-wechat', methods=['POST'])
def unbind_wechat():
    """解绑用户微信"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'}), 400
        
        # 清除用户微信绑定
        db = DatabaseManager()
        query = "UPDATE users SET wechat_user_id = NULL WHERE user_id = %s"
        db.execute(query, (user_id,))
        
        return jsonify({'success': True, 'message': '微信解绑成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'解绑失败: {str(e)}'}), 500
```

## 5. 环境配置

### 5.1 环境变量配置
```bash
# .env 文件
WECHAT_CORP_ID=your_corp_id
WECHAT_CORP_SECRET=your_corp_secret
WECHAT_AGENT_ID=your_agent_id
```

### 5.2 数据库表结构更新
```sql
-- 添加用户微信绑定字段
ALTER TABLE users ADD COLUMN wechat_user_id VARCHAR(100) NULL COMMENT '企业微信用户ID';

-- 创建索引
CREATE INDEX idx_users_wechat_user_id ON users(wechat_user_id);
```

## 6. 启动脚本

### 6.1 启动定时任务
```python
# start_daily_report_service.py
from backend_core.scheduler.daily_report_scheduler import DailyReportScheduler

if __name__ == "__main__":
    scheduler = DailyReportScheduler()
    scheduler.start_scheduler()
```

### 6.2 手动发送报告
```python
# manual_send_report.py
from backend_core.scheduler.daily_report_scheduler import DailyReportScheduler

if __name__ == "__main__":
    scheduler = DailyReportScheduler()
    scheduler.send_daily_report()
```
