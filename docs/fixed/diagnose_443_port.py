#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
443端口诊断脚本
"""

import os
import sys
import subprocess
import platform
import socket
from pathlib import Path

def run_command(command, check=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout, result.stderr, result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode

def check_port_usage():
    """检查443端口使用情况"""
    print("🔍 检查443端口使用情况...")
    
    try:
        # 尝试绑定443端口
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 443))
        sock.close()
        
        if result == 0:
            print("❌ 443端口已被占用")
            return False
        else:
            print("✅ 443端口可用")
            return True
    except Exception as e:
        print(f"❌ 检查端口时出错: {e}")
        return False

def check_nginx_process():
    """检查nginx进程"""
    print("🔍 检查nginx进程...")
    
    if platform.system() == "Windows":
        stdout, stderr, code = run_command("tasklist | findstr nginx", check=False)
        if "nginx.exe" in stdout:
            print("✅ nginx进程正在运行")
            return True
        else:
            print("❌ nginx进程未运行")
            return False
    else:
        stdout, stderr, code = run_command("ps aux | grep nginx | grep -v grep", check=False)
        if stdout.strip():
            print("✅ nginx进程正在运行")
            return True
        else:
            print("❌ nginx进程未运行")
            return False

def check_nginx_config():
    """检查nginx配置语法"""
    print("🔍 检查nginx配置语法...")
    
    stdout, stderr, code = run_command("nginx -t", check=False)
    
    if code == 0:
        print("✅ nginx配置语法正确")
        return True
    else:
        print(f"❌ nginx配置语法错误:\n{stderr}")
        return False

def check_admin_privileges():
    """检查管理员权限"""
    print("🔍 检查管理员权限...")
    
    try:
        # 尝试绑定特权端口
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 443))
        sock.close()
        print("✅ 有足够权限绑定443端口")
        return True
    except PermissionError:
        print("❌ 权限不足，无法绑定443端口")
        print("   需要以管理员身份运行nginx")
        return False
    except Exception as e:
        print(f"❌ 检查权限时出错: {e}")
        return False

def find_process_using_port():
    """查找使用443端口的进程"""
    print("🔍 查找使用443端口的进程...")
    
    if platform.system() == "Windows":
        stdout, stderr, code = run_command("netstat -ano | findstr :443", check=False)
        if stdout.strip():
            print("发现使用443端口的进程:")
            print(stdout)
            
            # 提取PID
            lines = stdout.strip().split('\n')
            for line in lines:
                if ':443' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"进程PID: {pid}")
                        
                        # 获取进程名称
                        proc_stdout, proc_stderr, proc_code = run_command(f"tasklist /FI \"PID eq {pid}\"", check=False)
                        if proc_stdout.strip():
                            print(f"进程信息:\n{proc_stdout}")
        else:
            print("未发现使用443端口的进程")
    else:
        stdout, stderr, code = run_command("netstat -tlnp | grep :443", check=False)
        if stdout.strip():
            print("发现使用443端口的进程:")
            print(stdout)
        else:
            print("未发现使用443端口的进程")

def suggest_solutions():
    """提供解决方案建议"""
    print("\n" + "=" * 50)
    print("🔧 解决方案建议:")
    print("=" * 50)
    
    print("\n1. 以管理员身份运行nginx:")
    print("   - 右键点击命令提示符或PowerShell")
    print("   - 选择'以管理员身份运行'")
    print("   - 导航到nginx目录")
    print("   - 运行: nginx -s reload")
    
    print("\n2. 如果443端口被其他程序占用:")
    print("   - 停止占用443端口的程序")
    print("   - 或者修改nginx配置使用其他端口")
    
    print("\n3. 临时使用其他端口测试:")
    print("   - 修改nginx配置中的443为8443")
    print("   - 测试配置是否正常")
    
    print("\n4. 检查防火墙设置:")
    print("   - 确保Windows防火墙允许nginx访问网络")
    print("   - 检查是否有其他安全软件阻止nginx")

def test_alternative_port():
    """测试使用其他端口"""
    print("\n🔧 测试使用8443端口...")
    
    # 创建临时配置文件
    temp_config = """
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
    
    # 保存临时配置
    temp_file = Path("temp_https_test.conf")
    temp_file.write_text(temp_config)
    
    print(f"临时配置文件已创建: {temp_file}")
    print("您可以手动测试这个配置")

def main():
    """主函数"""
    print("🚀 443端口诊断脚本")
    print("=" * 50)
    
    # 检查端口使用情况
    port_available = check_port_usage()
    
    # 检查nginx进程
    nginx_running = check_nginx_process()
    
    # 检查nginx配置
    config_ok = check_nginx_config()
    
    # 检查管理员权限
    has_privileges = check_admin_privileges()
    
    # 查找占用端口的进程
    find_process_using_port()
    
    # 提供解决方案
    suggest_solutions()
    
    # 测试替代端口
    test_alternative_port()
    
    print("\n" + "=" * 50)
    print("📋 诊断总结:")
    print("=" * 50)
    print(f"1. 443端口可用: {'✅' if port_available else '❌'}")
    print(f"2. nginx进程运行: {'✅' if nginx_running else '❌'}")
    print(f"3. 配置语法正确: {'✅' if config_ok else '❌'}")
    print(f"4. 有管理员权限: {'✅' if has_privileges else '❌'}")
    
    if not has_privileges:
        print("\n⚠️  主要问题: 权限不足")
        print("   解决方案: 以管理员身份运行nginx")
    elif not port_available:
        print("\n⚠️  主要问题: 443端口被占用")
        print("   解决方案: 停止占用端口的程序或使用其他端口")

if __name__ == "__main__":
    main()
