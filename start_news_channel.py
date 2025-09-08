#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资讯频道启动和测试脚本
"""

import subprocess
import time
import requests
import webbrowser
import os
import sys

def check_backend_running():
    """检查后端是否运行"""
    try:
        response = requests.get('http://localhost:5000/api/news/categories', timeout=5)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端API服务...")
    try:
        # 启动后端API
        backend_process = subprocess.Popen([
            sys.executable, 'start_backend_api.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务启动
        print("⏳ 等待后端服务启动...")
        for i in range(30):  # 最多等待30秒
            if check_backend_running():
                print("✅ 后端服务启动成功!")
                return backend_process
            time.sleep(1)
            print(f"   等待中... ({i+1}/30)")
        
        print("❌ 后端服务启动超时")
        return None
        
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return None

def test_news_api():
    """测试资讯API"""
    print("\n🧪 测试资讯API...")
    
    base_url = 'http://localhost:5000'
    
    # 测试分类API
    try:
        response = requests.get(f'{base_url}/api/news/categories')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 分类API正常 - 共{len(data['data'])}个分类")
        else:
            print(f"❌ 分类API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 分类API异常: {e}")
    
    # 测试资讯列表API
    try:
        response = requests.get(f'{base_url}/api/news/list?page=1&page_size=3')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 资讯列表API正常 - 共{len(data['data']['items'])}条资讯")
        else:
            print(f"❌ 资讯列表API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 资讯列表API异常: {e}")

def open_test_page():
    """打开测试页面"""
    print("\n🌐 打开测试页面...")
    
    # 获取当前目录的绝对路径
    current_dir = os.path.abspath('.')
    test_page_path = os.path.join(current_dir, 'frontend', 'test_news.html')
    
    if os.path.exists(test_page_path):
        file_url = f'file:///{test_page_path.replace(os.sep, "/")}'
        print(f"📄 测试页面路径: {file_url}")
        
        try:
            webbrowser.open(file_url)
            print("✅ 测试页面已打开")
        except Exception as e:
            print(f"❌ 打开测试页面失败: {e}")
    else:
        print(f"❌ 测试页面不存在: {test_page_path}")

def main():
    """主函数"""
    print("🎯 资讯频道启动和测试脚本")
    print("=" * 50)
    
    # 检查后端是否已运行
    if check_backend_running():
        print("✅ 后端服务已在运行")
    else:
        backend_process = start_backend()
        if not backend_process:
            print("❌ 无法启动后端服务，请检查配置")
            return
    
    # 测试API
    test_news_api()
    
    # 打开测试页面
    open_test_page()
    
    print("\n🎉 资讯频道测试完成!")
    print("\n📋 使用说明:")
    print("1. 测试页面已自动打开，可以测试各项功能")
    print("2. 访问 http://localhost:8000/news.html 查看完整资讯频道")
    print("3. 按 Ctrl+C 停止后端服务")
    
    # 保持运行
    try:
        print("\n⏳ 按 Ctrl+C 停止服务...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ 服务已停止")

if __name__ == "__main__":
    main()
