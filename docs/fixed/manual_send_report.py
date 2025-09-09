#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动发送每日股票报告脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_core.scheduler.daily_report_scheduler import DailyReportScheduler

def main():
    """主函数"""
    print("=" * 50)
    print("手动发送每日股票报告")
    print("=" * 50)
    
    try:
        scheduler = DailyReportScheduler()
        scheduler.send_daily_report()
        print("报告发送完成")
    except Exception as e:
        print(f"报告发送失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
