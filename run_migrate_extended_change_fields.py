#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行数据库迁移脚本
为historical_quotes表添加10天和60天涨幅字段
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend_core.data_collectors.tushare.migrate_extended_change_fields import migrate_historical_quotes_table

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    主函数
    """
    logger.info("=" * 60)
    logger.info("开始运行数据库迁移脚本")
    logger.info("为historical_quotes表添加10天和60天涨幅字段")
    logger.info("=" * 60)
    
    try:
        success = migrate_historical_quotes_table()
        
        if success:
            logger.info("=" * 60)
            logger.info("数据库迁移成功完成！")
            logger.info("historical_quotes表现在包含以下涨跌幅字段:")
            logger.info("  - five_day_change_percent (5日涨跌幅)")
            logger.info("  - ten_day_change_percent (10日涨跌幅)")
            logger.info("  - sixty_day_change_percent (60日涨跌幅)")
            logger.info("=" * 60)
        else:
            logger.error("=" * 60)
            logger.error("数据库迁移失败！请检查错误日志")
            logger.error("=" * 60)
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"运行迁移脚本时发生异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
