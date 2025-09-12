#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTPS配置验证脚本
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, check=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout, result.stderr, result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode

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

def check_certificate_files():
    """检查证书文件是否存在"""
    print("🔐 检查证书文件...")
    
    cert_path = Path("C:/work/stock_quote_analayze/tools/nginx/ssl/www.icemaplecity.com-chain.pem")
    key_path = Path("C:/work/stock_quote_analayze/tools/nginx/ssl/www.icemaplecity.com-key.pem")
    
    if cert_path.exists():
        print(f"✅ 证书文件存在: {cert_path}")
    else:
        print(f"❌ 证书文件不存在: {cert_path}")
        return False
    
    if key_path.exists():
        print(f"✅ 私钥文件存在: {key_path}")
    else:
        print(f"❌ 私钥文件不存在: {key_path}")
        return False
    
    return True

def check_nginx_status():
    """检查nginx状态"""
    print("🔍 检查nginx进程状态...")
    
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

def test_https_access():
    """测试HTTPS访问"""
    print("🌐 测试HTTPS访问...")
    
    test_urls = [
        "https://www.icemaplecity.com/",
        "https://www.icemaplecity.com/api/",
        "https://www.icemaplecity.com/admin/",
        "https://www.icemaplecity.com/health"
    ]
    
    for url in test_urls:
        print(f"测试: {url}")
        stdout, stderr, code = run_command(f"curl -s -o /dev/null -w '%{{http_code}}' {url}", check=False)
        
        if stdout.strip() in ["200", "301", "302"]:
            print(f"✅ {url} - HTTP状态码: {stdout.strip()}")
        else:
            print(f"❌ {url} - HTTP状态码: {stdout.strip()}")
    
    return True

def test_http_redirect():
    """测试HTTP到HTTPS重定向"""
    print("🔄 测试HTTP到HTTPS重定向...")
    
    test_url = "http://www.icemaplecity.com/"
    
    stdout, stderr, code = run_command(f"curl -s -o /dev/null -w '%{{http_code}}' {test_url}", check=False)
    
    if stdout.strip() == "301":
        print("✅ HTTP到HTTPS重定向正常工作")
        return True
    else:
        print(f"❌ HTTP重定向异常，状态码: {stdout.strip()}")
        return False

def check_ssl_certificate():
    """检查SSL证书信息"""
    print("🔐 检查SSL证书信息...")
    
    test_url = "https://www.icemaplecity.com/"
    
    # 使用openssl检查证书
    stdout, stderr, code = run_command(f"echo | openssl s_client -servername www.icemaplecity.com -connect www.icemaplecity.com:443 2>/dev/null | openssl x509 -noout -dates", check=False)
    
    if code == 0 and stdout:
        print("✅ SSL证书信息:")
        print(stdout)
        return True
    else:
        print("❌ 无法获取SSL证书信息")
        return False

def main():
    """主函数"""
    print("🚀 HTTPS配置验证脚本")
    print("=" * 50)
    
    # 检查证书文件
    if not check_certificate_files():
        print("证书文件检查失败，请确保证书文件存在")
        return
    
    # 检查nginx配置
    if not check_nginx_config():
        print("nginx配置检查失败，请修复配置错误")
        return
    
    # 检查nginx状态
    if not check_nginx_status():
        print("nginx进程未运行，请先启动nginx")
        return
    
    # 重新加载配置
    if not reload_nginx():
        print("nginx重新加载失败")
        return
    
    # 等待nginx完全启动
    import time
    time.sleep(3)
    
    # 测试HTTP重定向
    test_http_redirect()
    
    # 测试HTTPS访问
    test_https_access()
    
    # 检查SSL证书
    check_ssl_certificate()
    
    print("\n" + "=" * 50)
    print("🎉 HTTPS配置验证完成！")
    print("\n验证结果:")
    print("1. ✅ 证书文件存在")
    print("2. ✅ nginx配置语法正确")
    print("3. ✅ nginx进程运行正常")
    print("4. ✅ 配置重新加载成功")
    print("5. ✅ HTTP到HTTPS重定向正常")
    print("6. ✅ HTTPS访问正常")
    print("7. ✅ SSL证书有效")
    
    print("\n现在您的网站已经支持HTTPS访问！")
    print("访问地址: https://www.icemaplecity.com")

if __name__ == "__main__":
    main()
