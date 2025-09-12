@echo off
echo ========================================
echo    股票分析系统生产环境启动脚本
echo ========================================
echo.

echo 1. 启动后端API服务...
cd /d C:\work\stock_quote_analayze\run\backend_api
start "Backend API" cmd /k "python start_backend_api.py"
timeout /t 5 /nobreak > nul

echo 2. 启动前端服务...
cd /d C:\work\stock_quote_analayze\run\frontend
start "Frontend" cmd /k "python start_frontend.py"
timeout /t 5 /nobreak > nul

echo 3. 启动管理后台...
cd /d C:\work\stock_quote_analayze\run\admin-modern
start "Admin" cmd /k "python -m http.server 8001"
timeout /t 5 /nobreak > nul

echo 4. 启动Nginx...
cd /d C:\work\stock_quote_analayze\tools\nginx-1.28.0
start "Nginx" cmd /k "nginx.exe"

echo.
echo 所有服务已启动！
echo 请检查各服务是否正常运行。
echo.
echo 访问地址:
echo   前端应用: https://www.icemaplecity.com/
echo   管理后台: https://www.icemaplecity.com/admin
echo   后端API: https://www.icemaplecity.com/api
echo.
pause
