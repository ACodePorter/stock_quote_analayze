# 每日报告调度器
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
