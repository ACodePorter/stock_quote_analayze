#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境连接问题诊断和修复脚本
解决nginx无法连接到127.0.0.1:8000的问题
"""

import subprocess
import socket
import time
import os
import sys
from datetime import datetime

def check_port_status(host, port):
    """检查端口是否可连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"检查端口 {host}:{port} 时出错: {e}")
        return False

def check_process_on_port(port):
    """检查端口上运行的进程"""
    try:
        # Windows系统使用netstat命令
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    return pid
        return None
    except Exception as e:
        print(f"检查进程时出错: {e}")
        return None

def get_process_name(pid):
    """获取进程名称"""
    try:
        result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if pid in line:
                parts = line.split()
                if len(parts) >= 1:
                    return parts[0]
        return "Unknown"
    except Exception as e:
        print(f"获取进程名称时出错: {e}")
        return "Unknown"

def diagnose_production_issue():
    """诊断生产环境问题"""
    print("=" * 60)
    print("           生产环境连接问题诊断")
    print("=" * 60)
    print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查各个服务端口
    services = [
        ("前端服务", "127.0.0.1", 8000),
        ("管理后台", "127.0.0.1", 8001),
        ("后端API", "127.0.0.1", 5000),
        ("Nginx", "127.0.0.1", 80),
        ("Nginx HTTPS", "127.0.0.1", 443)
    ]
    
    print("=== 服务端口状态检查 ===")
    for service_name, host, port in services:
        is_running = check_port_status(host, port)
        status = "✅ 运行中" if is_running else "❌ 未运行"
        print(f"{service_name:12} {host}:{port:4} - {status}")
        
        if not is_running and port in [8000, 8001, 5000]:
            # 检查是否有进程占用端口
            pid = check_process_on_port(port)
            if pid:
                process_name = get_process_name(pid)
                print(f"            端口被进程占用: PID={pid}, 进程名={process_name}")
    
    print()
    
    # 重点检查8000端口
    print("=== 重点检查8000端口（前端服务）===")
    if not check_port_status("127.0.0.1", 8000):
        print("❌ 8000端口无法连接，这是导致nginx错误的原因")
        
        # 检查是否有进程占用
        pid = check_process_on_port(8000)
        if pid:
            process_name = get_process_name(pid)
            print(f"   端口被进程占用: PID={pid}, 进程名={process_name}")
        else:
            print("   端口未被占用，前端服务未启动")
    else:
        print("✅ 8000端口正常，前端服务运行中")
    
    print()
    
    # 检查nginx配置
    print("=== Nginx配置检查 ===")
    nginx_config_paths = [
        "C:/work/stock_quote_analayze/tools/nginx-1.28.0/conf/nginx.conf",
        "nginx_complete.conf",
        "docs/prod/nginx.conf"
    ]
    
    for config_path in nginx_config_paths:
        if os.path.exists(config_path):
            print(f"✅ 找到nginx配置文件: {config_path}")
            # 检查配置内容
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "upstream frontend_server" in content and "server 127.0.0.1:8000" in content:
                        print(f"   ✅ 配置正确：upstream frontend_server指向127.0.0.1:8000")
                    else:
                        print(f"   ❌ 配置可能有问题：未找到正确的upstream配置")
            except Exception as e:
                print(f"   ❌ 读取配置文件失败: {e}")
        else:
            print(f"❌ 配置文件不存在: {config_path}")

def generate_fix_commands():
    """生成修复命令"""
    print()
    print("=== 修复建议 ===")
    print()
    
    print("1. 启动前端服务:")
    print("   cd C:\\work\\stock_quote_analayze\\run\\frontend")
    print("   python start_frontend.py")
    print()
    
    print("2. 或者使用Python内置服务器:")
    print("   cd C:\\work\\stock_quote_analayze\\run\\frontend")
    print("   python -m http.server 8000")
    print()
    
    print("3. 检查前端服务是否启动成功:")
    print("   netstat -ano | findstr :8000")
    print()
    
    print("4. 重启nginx服务:")
    print("   cd C:\\work\\stock_quote_analayze\\tools\\nginx-1.28.0")
    print("   nginx.exe -s stop")
    print("   nginx.exe")
    print()
    
    print("5. 检查nginx配置:")
    print("   nginx.exe -t")
    print()
    
    print("6. 查看nginx错误日志:")
    print("   type C:\\work\\stock_quote_analayze\\tools\\nginx-1.28.0\\logs\\error.log")
    print()

def create_startup_script():
    """创建启动脚本"""
    script_content = """@echo off
echo ========================================
echo    股票分析系统生产环境启动脚本
echo ========================================
echo.

echo 1. 启动后端API服务...
cd /d C:\\work\\stock_quote_analayze\\run\\backend_api
start "Backend API" cmd /k "python start_backend_api.py"
timeout /t 5 /nobreak > nul

echo 2. 启动前端服务...
cd /d C:\\work\\stock_quote_analayze\\run\\frontend
start "Frontend" cmd /k "python start_frontend.py"
timeout /t 5 /nobreak > nul

echo 3. 启动管理后台...
cd /d C:\\work\\stock_quote_analayze\\run\\admin-modern
start "Admin" cmd /k "python -m http.server 8001"
timeout /t 5 /nobreak > nul

echo 4. 启动Nginx...
cd /d C:\\work\\stock_quote_analayze\\tools\\nginx-1.28.0
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
"""
    
    script_path = "start_production_services.bat"
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"✅ 创建启动脚本: {script_path}")
        print("   可以使用此脚本一键启动所有生产环境服务")
    except Exception as e:
        print(f"❌ 创建启动脚本失败: {e}")

def main():
    """主函数"""
    diagnose_production_issue()
    generate_fix_commands()
    create_startup_script()
    
    print()
    print("=" * 60)
    print("           诊断完成")
    print("=" * 60)
    print("根据以上诊断结果，主要问题是8000端口的前端服务未启动。")
    print("请按照修复建议启动相应的服务。")

if __name__ == "__main__":
    main()
