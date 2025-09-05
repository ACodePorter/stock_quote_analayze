#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日股票报告发送服务启动脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_core.scheduler.daily_report_scheduler import DailyReportScheduler

def main():
    """主函数"""
    print("=" * 50)
    print("每日股票报告发送服务")
    print("=" * 50)
    
    try:
        scheduler = DailyReportScheduler()
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"服务启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
