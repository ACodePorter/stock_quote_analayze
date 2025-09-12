@echo off
title 数据采集定时任务（包含新闻采集）
echo ========================================
echo           数据采集定时任务
echo ========================================
echo 启动时间: %date% %time%
echo.
echo 任务配置:
echo   - A股实时行情采集（每15分钟）
echo   - 指数实时行情采集（每20分钟）
echo   - 行业板块行情采集（每30分钟）
echo   - 市场新闻采集（每30分钟）
echo   - 热门资讯更新（每小时）
echo   - 旧新闻清理（每天凌晨2点）
echo   - 自选股历史行情采集（每5分钟）
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python -m backend_core.data_collectors.main

echo.
echo 服务已停止
pause
