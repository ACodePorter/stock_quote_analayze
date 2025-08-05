#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志监控功能快速测试脚本
"""

import subprocess
import time
import requests
import json
import sys
import os

def check_backend_running():
    """检查后端服务是否运行"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    try:
        # 切换到backend_api目录
        os.chdir("backend_api")
        
        # 启动服务
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务启动
        for i in range(30):
            if check_backend_running():
                print("✅ 后端服务启动成功")
                return process
            time.sleep(1)
            print(f"⏳ 等待服务启动... ({i+1}/30)")
        
        print("❌ 后端服务启动超时")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return None

def test_logs_api():
    """测试日志API"""
    print("\n🧪 测试日志API...")
    
    # 测试获取日志表列表
    try:
        response = requests.get("http://localhost:8000/api/admin/logs/tables")
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取日志表列表成功")
            print(f"   发现 {len(data.get('tables', []))} 个日志表")
            for table in data.get('tables', []):
                print(f"   - {table['display_name']} ({table['key']})")
        else:
            print(f"❌ 获取日志表列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试日志表列表API失败: {e}")
        return False
    
    # 测试查询日志数据
    log_tables = ["historical_collect", "realtime_collect", "watchlist_history"]
    for table_key in log_tables:
        try:
            response = requests.get(f"http://localhost:8000/api/admin/logs/query/{table_key}?page=1&page_size=5")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 查询 {table_key} 日志成功")
                print(f"   总记录数: {data.get('pagination', {}).get('total_count', 0)}")
            else:
                print(f"❌ 查询 {table_key} 日志失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 测试 {table_key} 日志查询失败: {e}")
    
    return True

def test_admin_frontend():
    """测试管理后台前端"""
    print("\n🌐 测试管理后台前端...")
    
    try:
        response = requests.get("http://localhost:8000/admin/")
        if response.status_code == 200:
            print("✅ 管理后台前端访问成功")
            if "系统日志" in response.text:
                print("✅ 日志监控页面已集成")
            else:
                print("⚠️  日志监控页面可能未正确集成")
        else:
            print(f"❌ 管理后台前端访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试管理后台前端失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("📊 股票分析系统 - 日志监控功能测试")
    print("=" * 60)
    
    # 检查当前目录
    if not os.path.exists("backend_api"):
        print("❌ 请在项目根目录运行此脚本")
        return
    
    # 启动后端服务
    backend_process = start_backend()
    if not backend_process:
        return
    
    try:
        # 测试API
        if test_logs_api():
            print("\n✅ 日志API测试通过")
        else:
            print("\n❌ 日志API测试失败")
        
        # 测试前端
        if test_admin_frontend():
            print("\n✅ 管理后台前端测试通过")
        else:
            print("\n❌ 管理后台前端测试失败")
        
        print("\n" + "=" * 60)
        print("🎉 测试完成！")
        print("=" * 60)
        print("\n📋 使用说明:")
        print("1. 访问管理后台: http://localhost:8000/admin")
        print("2. 登录账号: admin / 123456")
        print("3. 点击左侧导航栏的'系统日志'")
        print("4. 使用日志监控功能")
        print("\n按 Ctrl+C 停止服务")
        
        # 保持服务运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 收到停止信号，正在关闭服务...")
    finally:
        if backend_process:
            backend_process.terminate()
            print("✅ 后端服务已停止")

if __name__ == "__main__":
    main() 