@echo off
echo ========================================
echo    生产环境快速修复脚本
echo ========================================
echo.

echo 正在检查服务状态...
echo.

echo 1. 检查8000端口（前端服务）...
netstat -ano | findstr :8000
if %errorlevel% equ 0 (
    echo ✅ 8000端口正常
) else (
    echo ❌ 8000端口异常，正在启动前端服务...
    cd /d C:\work\stock_quote_analayze\run\frontend
    start "Frontend" cmd /k "python start_frontend.py"
    timeout /t 3 /nobreak > nul
)

echo.
echo 2. 检查5000端口（后端API）...
netstat -ano | findstr :5000
if %errorlevel% equ 0 (
    echo ✅ 5000端口正常
) else (
    echo ❌ 5000端口异常，正在启动后端API...
    cd /d C:\work\stock_quote_analayze\run\backend_api
    start "Backend API" cmd /k "python start_backend_api.py"
    timeout /t 3 /nobreak > nul
)

echo.
echo 3. 检查8001端口（管理后台）...
netstat -ano | findstr :8001
if %errorlevel% equ 0 (
    echo ✅ 8001端口正常
) else (
    echo ❌ 8001端口异常，正在启动管理后台...
    cd /d C:\work\stock_quote_analayze\run\admin-modern
    start "Admin" cmd /k "python -m http.server 8001"
    timeout /t 3 /nobreak > nul
)

echo.
echo 4. 检查80端口（Nginx HTTP）...
netstat -ano | findstr :80
if %errorlevel% equ 0 (
    echo ✅ 80端口正常
) else (
    echo ❌ 80端口异常，正在启动Nginx...
    cd /d C:\work\stock_quote_analayze\tools\nginx-1.28.0
    nginx.exe
    timeout /t 3 /nobreak > nul
)

echo.
echo 5. 检查443端口（Nginx HTTPS）...
netstat -ano | findstr :443
if %errorlevel% equ 0 (
    echo ✅ 443端口正常
) else (
    echo ❌ 443端口异常，Nginx HTTPS服务未启动
)

echo.
echo ========================================
echo    修复完成，正在验证服务状态...
echo ========================================
echo.

echo 最终服务状态检查：
echo.
netstat -ano | findstr :80
netstat -ano | findstr :443
netstat -ano | findstr :8000
netstat -ano | findstr :5000
netstat -ano | findstr :8001

echo.
echo ========================================
echo    修复完成！
echo ========================================
echo.
echo 如果所有服务都正常启动，请访问：
echo   前端应用: https://www.icemaplecity.com/
echo   管理后台: https://www.icemaplecity.com/admin
echo   后端API: https://www.icemaplecity.com/api
echo.
echo 如果仍有问题，请检查：
echo   1. nginx配置文件路径是否正确
echo   2. SSL证书文件是否存在
echo   3. 防火墙是否阻止了端口访问
echo.
pause
