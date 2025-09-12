#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复443端口问题的脚本
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(command, check=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout, result.stderr, result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode

def backup_nginx_config():
    """备份nginx配置"""
    print("💾 备份nginx配置...")
    
    config_path = Path("nginx.conf")
    backup_path = Path("nginx.conf.backup.443_fix")
    
    if config_path.exists():
        try:
            shutil.copy2(config_path, backup_path)
            print(f"✅ 配置已备份到: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ 备份失败: {e}")
            return False
    else:
        print("⚠️  nginx.conf文件不存在")
        return False

def create_alternative_config():
    """创建使用8443端口的替代配置"""
    print("🔧 创建8443端口配置...")
    
    # 读取当前配置
    config_path = Path("nginx.conf")
    if not config_path.exists():
        print("❌ nginx.conf文件不存在")
        return False
    
    try:
        content = config_path.read_text(encoding='utf-8')
        
        # 替换443为8443
        new_content = content.replace('listen       443 ssl;', 'listen       8443 ssl;')
        
        # 保存新配置
        new_config_path = Path("nginx_8443.conf")
        new_config_path.write_text(new_content, encoding='utf-8')
        
        print(f"✅ 8443端口配置已创建: {new_config_path}")
        return True
    except Exception as e:
        print(f"❌ 创建替代配置失败: {e}")
        return False

def test_8443_config():
    """测试8443端口配置"""
    print("🧪 测试8443端口配置...")
    
    # 使用临时配置文件测试
    test_config = """
server {
    listen       8443 ssl;
    http2 on;
    server_name  www.icemaplecity.com icemaplecity.com;

    ssl_certificate      C:/work/stock_quote_analayze/tools/nginx/ssl/www.icemaplecity.com-chain.pem;
    ssl_certificate_key  C:/work/stock_quote_analayze/tools/nginx/ssl/www.icemaplecity.com-key.pem;

    ssl_session_cache    shared:SSL:1m;
    ssl_session_timeout  5m;

    ssl_ciphers  ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers  on;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        return 200 "HTTPS test successful on port 8443\\n";
        add_header Content-Type text/plain;
    }
}
"""
    
    # 保存测试配置
    test_config_path = Path("test_8443.conf")
    test_config_path.write_text(test_config, encoding='utf-8')
    
    print(f"✅ 测试配置文件已创建: {test_config_path}")
    return True

def check_admin_privileges():
    """检查是否有管理员权限"""
    print("🔍 检查管理员权限...")
    
    try:
        # 尝试绑定特权端口
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 443))
        sock.close()
        print("✅ 有足够权限绑定443端口")
        return True
    except PermissionError:
        print("❌ 权限不足，无法绑定443端口")
        return False
    except Exception as e:
        print(f"❌ 检查权限时出错: {e}")
        return False

def stop_nginx():
    """停止nginx进程"""
    print("🛑 停止nginx进程...")
    
    stdout, stderr, code = run_command("nginx -s quit", check=False)
    
    if code == 0:
        print("✅ nginx已停止")
        return True
    else:
        print("⚠️  nginx停止失败或未运行")
        return True

def start_nginx():
    """启动nginx"""
    print("🚀 启动nginx...")
    
    stdout, stderr, code = run_command("nginx", check=False)
    
    if code == 0:
        print("✅ nginx启动成功")
        return True
    else:
        print(f"❌ nginx启动失败:\n{stderr}")
        return False

def reload_nginx():
    """重新加载nginx配置"""
    print("🔄 重新加载nginx配置...")
    
    stdout, stderr, code = run_command("nginx -s reload", check=False)
    
    if code == 0:
        print("✅ nginx配置重新加载成功")
        return True
    else:
        print(f"❌ nginx重新加载失败:\n{stderr}")
        return False

def create_admin_batch_file():
    """创建管理员权限运行脚本"""
    print("📝 创建管理员权限运行脚本...")
    
    batch_content = """@echo off
echo 正在以管理员身份启动nginx...
echo.

REM 检查nginx配置
echo 检查nginx配置...
nginx -t
if errorlevel 1 (
    echo nginx配置检查失败！
    pause
    exit /b 1
)

REM 重新加载nginx配置
echo 重新加载nginx配置...
nginx -s reload
if errorlevel 1 (
    echo nginx重新加载失败！
    pause
    exit /b 1
)

echo.
echo nginx已成功启动！
echo 现在可以通过以下地址访问：
echo - HTTP: http://www.icemaplecity.com (自动重定向到HTTPS)
echo - HTTPS: https://www.icemaplecity.com
echo.
pause
"""
    
    batch_file = Path("start_nginx_as_admin.bat")
    batch_file.write_text(batch_content, encoding='gbk')
    
    print(f"✅ 管理员权限脚本已创建: {batch_file}")
    return True

def main():
    """主函数"""
    print("🚀 443端口问题修复脚本")
    print("=" * 50)
    
    # 备份配置
    backup_nginx_config()
    
    # 检查管理员权限
    has_privileges = check_admin_privileges()
    
    if not has_privileges:
        print("\n⚠️  检测到权限不足问题")
        print("   解决方案:")
        print("   1. 以管理员身份运行PowerShell或命令提示符")
        print("   2. 导航到nginx目录")
        print("   3. 运行: nginx -s reload")
        
        # 创建管理员权限脚本
        create_admin_batch_file()
        
        print("\n或者使用8443端口作为临时解决方案:")
        create_alternative_config()
        test_8443_config()
        
        return
    
    # 如果有权限，尝试修复
    print("\n🔧 尝试修复443端口问题...")
    
    # 停止nginx
    stop_nginx()
    
    # 等待一下
    import time
    time.sleep(2)
    
    # 启动nginx
    if start_nginx():
        print("\n✅ 修复成功！")
        print("现在可以通过以下地址访问：")
        print("- HTTP: http://www.icemaplecity.com (自动重定向到HTTPS)")
        print("- HTTPS: https://www.icemaplecity.com")
    else:
        print("\n❌ 修复失败")
        print("建议使用8443端口作为临时解决方案")
        create_alternative_config()
        test_8443_config()

if __name__ == "__main__":
    main()
