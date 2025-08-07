#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSL证书生成失败快速修复脚本
"""

import os
import sys
import shutil
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

def check_nginx_status():
    """检查nginx状态"""
    print("🔍 检查nginx状态...")
    
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

def create_directories():
    """创建必要的目录结构"""
    print("📁 创建必要的目录结构...")
    
    base_path = Path("C:/work/stock_quote_analayze/tools/nginx-1.28.0")
    html_path = base_path / "html"
    acme_path = html_path / ".well-known" / "acme-challenge"
    
    try:
        # 创建目录
        acme_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 目录创建成功: {acme_path}")
        
        # 创建测试文件
        test_file = acme_path / "test.txt"
        test_file.write_text("test")
        print(f"✅ 测试文件创建成功: {test_file}")
        
        return True
    except Exception as e:
        print(f"❌ 目录创建失败: {e}")
        return False

def backup_nginx_config():
    """备份nginx配置"""
    print("💾 备份nginx配置...")
    
    config_path = Path("nginx.conf")
    backup_path = Path("nginx.conf.backup")
    
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

def apply_fixed_config():
    """应用修复的配置"""
    print("🔧 应用修复的nginx配置...")
    
    fixed_config = Path("docs/fixed/nginx_ssl_fix.conf")
    target_config = Path("nginx.conf")
    
    if not fixed_config.exists():
        print(f"❌ 修复配置文件不存在: {fixed_config}")
        return False
    
    try:
        shutil.copy2(fixed_config, target_config)
        print(f"✅ 修复配置已应用")
        return True
    except Exception as e:
        print(f"❌ 配置应用失败: {e}")
        return False

def test_nginx_config():
    """测试nginx配置语法"""
    print("🧪 测试nginx配置语法...")
    
    stdout, stderr, code = run_command("nginx -t", check=False)
    
    if code == 0:
        print("✅ nginx配置语法正确")
        return True
    else:
        print(f"❌ nginx配置语法错误:\n{stderr}")
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

def test_acme_path():
    """测试ACME挑战路径"""
    print("🌐 测试ACME挑战路径...")
    
    test_url = "http://www.icemaplecity.com/.well-known/acme-challenge/test.txt"
    
    stdout, stderr, code = run_command(f"curl -s -o /dev/null -w '%{{http_code}}' {test_url}", check=False)
    
    if stdout.strip() == "200":
        print("✅ ACME挑战路径可访问")
        return True
    else:
        print(f"❌ ACME挑战路径不可访问，HTTP状态码: {stdout.strip()}")
        return False

def clean_certbot():
    """清理certbot之前的申请"""
    print("🧹 清理certbot之前的申请...")
    
    stdout, stderr, code = run_command("certbot delete --cert-name www.icemaplecity.com", check=False)
    
    if code == 0:
        print("✅ certbot清理成功")
    else:
        print("⚠️  certbot清理失败或证书不存在")
    
    return True

def regenerate_certificate():
    """重新生成证书"""
    print("🔐 重新生成SSL证书...")
    
    webroot_path = "C:/work/stock_quote_analayze/tools/nginx-1.28.0/html"
    command = f"certbot certonly --webroot -w {webroot_path} -d www.icemaplecity.com -d icemaplecity.com"
    
    print(f"执行命令: {command}")
    print("请手动执行上述命令来生成证书...")
    
    return True

def main():
    """主函数"""
    print("🚀 SSL证书生成失败修复脚本")
    print("=" * 50)
    
    # 检查nginx状态
    if not check_nginx_status():
        print("请先启动nginx服务")
        return
    
    # 创建目录
    if not create_directories():
        print("目录创建失败，请检查权限")
        return
    
    # 备份配置
    backup_nginx_config()
    
    # 应用修复配置
    if not apply_fixed_config():
        print("配置应用失败")
        return
    
    # 测试配置
    if not test_nginx_config():
        print("配置测试失败，请检查配置文件")
        return
    
    # 重新加载nginx
    if not reload_nginx():
        print("nginx重新加载失败")
        return
    
    # 等待一下让nginx完全启动
    import time
    time.sleep(2)
    
    # 测试ACME路径
    if not test_acme_path():
        print("ACME路径测试失败，请检查网络和DNS设置")
        return
    
    # 清理certbot
    clean_certbot()
    
    # 重新生成证书
    regenerate_certificate()
    
    print("\n" + "=" * 50)
    print("🎉 修复脚本执行完成！")
    print("\n下一步操作：")
    print("1. 手动执行certbot命令生成证书")
    print("2. 检查证书生成是否成功")
    print("3. 配置HTTPS服务器块")
    print("4. 测试HTTPS访问")

if __name__ == "__main__":
    main()
