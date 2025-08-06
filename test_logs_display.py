#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试系统日志页面显示
"""

import requests
import time
import webbrowser
from pathlib import Path

def test_logs_page():
    """测试系统日志页面"""
    print("🔍 测试系统日志页面显示...")
    
    # 检查admin目录是否存在
    admin_dir = Path("admin")
    if not admin_dir.exists():
        print("❌ admin目录不存在")
        return False
    
    # 检查关键文件
    required_files = [
        "admin/index.html",
        "admin/logs.html", 
        "admin/js/logs.js",
        "admin/js/module-loader.js",
        "admin/js/admin.js"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ 文件不存在: {file_path}")
            return False
        else:
            print(f"✅ 文件存在: {file_path}")
    
    # 检查后端API是否运行
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端API运行正常")
        else:
            print(f"⚠️ 后端API响应异常: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 无法连接到后端API: {e}")
    
    # 启动前端服务器（如果未运行）
    try:
        response = requests.get("http://localhost:8001", timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务器运行正常")
        else:
            print(f"⚠️ 前端服务器响应异常: {response.status_code}")
    except requests.exceptions.RequestException:
        print("⚠️ 前端服务器未运行，尝试启动...")
        start_frontend_server()
    
    # 打开系统日志页面
    logs_url = "http://localhost:8001/#logs"
    print(f"🌐 打开系统日志页面: {logs_url}")
    
    try:
        webbrowser.open(logs_url)
        print("✅ 已在浏览器中打开系统日志页面")
    except Exception as e:
        print(f"❌ 无法打开浏览器: {e}")
    
    return True

def start_frontend_server():
    """启动前端服务器"""
    import subprocess
    import sys
    
    print("🚀 启动前端服务器...")
    
    try:
        # 检查是否在admin目录中
        if Path("admin").exists():
            # 在admin目录中启动服务器
            process = subprocess.Popen([
                sys.executable, "-m", "http.server", "8001"
            ], cwd="admin")
            
            print("✅ 前端服务器已启动 (端口8001)")
            print("⏳ 等待服务器启动...")
            time.sleep(3)
            
            return process
        else:
            print("❌ 未找到admin目录")
            return None
    except Exception as e:
        print(f"❌ 启动前端服务器失败: {e}")
        return None

def check_logs_functionality():
    """检查日志功能"""
    print("\n🔍 检查日志功能...")
    
    # 检查logs.js中的关键函数
    logs_js_path = Path("admin/js/logs.js")
    if logs_js_path.exists():
        content = logs_js_path.read_text(encoding='utf-8')
        
        required_functions = [
            "class LogsManager",
            "init()",
            "loadLogs()",
            "renderLogsTable",
            "initLogsManager"
        ]
        
        for func in required_functions:
            if func in content:
                print(f"✅ 找到函数: {func}")
            else:
                print(f"❌ 缺少函数: {func}")
    
    # 检查logs.html中的关键元素
    logs_html_path = Path("admin/logs.html")
    if logs_html_path.exists():
        content = logs_html_path.read_text(encoding='utf-8')
        
        required_elements = [
            "logsPage",
            "logsTable",
            "logsTableBody",
            "tab-btn"
        ]
        
        for element in required_elements:
            if element in content:
                print(f"✅ 找到元素: {element}")
            else:
                print(f"❌ 缺少元素: {element}")

def main():
    """主函数"""
    print("=" * 50)
    print("🔧 系统日志页面测试工具")
    print("=" * 50)
    
    # 检查文件结构
    test_logs_page()
    
    # 检查功能
    check_logs_functionality()
    
    print("\n" + "=" * 50)
    print("📋 测试完成")
    print("=" * 50)
    print("\n💡 使用说明:")
    print("1. 确保后端API运行在 http://localhost:8000")
    print("2. 确保前端服务器运行在 http://localhost:8001")
    print("3. 在浏览器中访问 http://localhost:8001")
    print("4. 使用 admin/123456 登录")
    print("5. 点击左侧导航栏的'系统日志'")
    print("\n🔧 如果页面不显示，请检查浏览器控制台的错误信息")

if __name__ == "__main__":
    main() 