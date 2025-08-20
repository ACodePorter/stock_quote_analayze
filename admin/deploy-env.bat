@echo off
chcp 65001 >nul

echo 🚀 股票分析系统管理后台 - 环境配置脚本
echo ==========================================

REM 检测当前环境
if "%1"=="production" (
    set ENV=production
    set API_URL=https://www.icemaplecity.com/api/admin
    echo 📦 配置生产环境
) else if "%1"=="development" (
    set ENV=development
    set API_URL=http://localhost:5000/api/admin
    echo 🔧 配置开发环境
) else (
    echo ❌ 请指定环境: production 或 development
    echo 用法: deploy-env.bat [production^|development]
    pause
    exit /b 1
)

echo 🔗 API地址: %API_URL%
echo 🌍 环境: %ENV%

REM 创建环境配置文件
(
echo # 自动生成的环境配置文件
echo # 环境: %ENV%
echo VITE_API_BASE_URL=%API_URL%
echo VITE_ENVIRONMENT=%ENV%
) > .env.local

echo ✅ 环境配置文件已创建: .env.local
echo 📝 内容:
type .env.local

echo.
echo 🔄 请重新构建项目以应用新配置:
echo    npm run build
echo.
echo 🌐 或者启动开发服务器:
echo    npm run dev

pause
