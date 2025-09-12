#!/usr/bin/env python3
"""
生产环境配置测试脚本
用于验证域名访问配置是否正确
"""

import requests
import json
import time

def test_api_endpoints():
    """测试API端点"""
    
    # 测试配置
    test_urls = [
        "http://localhost:5000/api/auth/status",
        "http://127.0.0.1:5000/api/auth/status",
        "http://192.168.31.237:5000/api/auth/status"
    ]
    
    print("🔍 测试API端点...")
    print("=" * 50)
    
    for url in test_urls:
        try:
            print(f"测试: {url}")
            response = requests.get(url, timeout=5)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                print("✅ 连接成功")
                try:
                    data = response.json()
                    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
                except:
                    print(f"响应内容: {response.text[:200]}...")
            else:
                print(f"❌ 连接失败: {response.status_code}")
                print(f"错误信息: {response.text[:200]}...")
        except requests.exceptions.ConnectionError:
            print("❌ 连接被拒绝 - 服务可能未启动")
        except requests.exceptions.Timeout:
            print("❌ 连接超时")
        except Exception as e:
            print(f"❌ 其他错误: {str(e)}")
        print("-" * 30)

def test_cors_config():
    """测试CORS配置"""
    print("\n🌐 测试CORS配置...")
    print("=" * 50)
    
    # 模拟生产环境的请求
    headers = {
        'Origin': 'http://www.icemaplecity.com',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    test_urls = [
        "http://localhost:5000/api/auth/login",
        "http://127.0.0.1:5000/api/auth/login",
        "http://192.168.31.237:5000/api/auth/login"
    ]
    
    for url in test_urls:
        try:
            print(f"测试CORS: {url}")
            # 先发送OPTIONS请求测试CORS预检
            response = requests.options(url, headers=headers, timeout=5)
            print(f"OPTIONS状态码: {response.status_code}")
            print(f"CORS头: {dict(response.headers)}")
            
            # 测试POST请求
            post_data = {"username": "test", "password": "test"}
            response = requests.post(url, json=post_data, headers={'Origin': 'http://www.icemaplecity.com'}, timeout=5)
            print(f"POST状态码: {response.status_code}")
            if response.status_code == 401:
                print("✅ CORS配置正确 - 收到预期的401认证错误")
            else:
                print(f"响应: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ CORS测试失败: {str(e)}")
        print("-" * 30)

def test_frontend_config():
    """测试前端配置"""
    print("\n📱 测试前端配置...")
    print("=" * 50)
    
    # 检查配置文件是否存在
    import os
    config_file = "frontend/js/config.js"
    if os.path.exists(config_file):
        print("✅ config.js 文件存在")
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "icemaplecity.com" in content:
                print("✅ 生产域名配置正确")
            else:
                print("❌ 生产域名配置缺失")
    else:
        print("❌ config.js 文件不存在")
    
    # 检查HTML文件是否包含config.js
    html_files = [
        "frontend/login.html",
        "frontend/index.html",
        "frontend/markets.html"
    ]
    
    for html_file in html_files:
        if os.path.exists(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "config.js" in content:
                    print(f"✅ {html_file} 包含config.js")
                else:
                    print(f"❌ {html_file} 缺少config.js")

def main():
    """主函数"""
    print("🚀 生产环境配置测试")
    print("=" * 60)
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 测试API端点
    test_api_endpoints()
    
    # 测试CORS配置
    test_cors_config()
    
    # 测试前端配置
    test_frontend_config()
    
    print("\n" + "=" * 60)
    print("📋 测试总结")
    print("=" * 60)
    print("如果看到以下情况，说明配置正确：")
    print("1. ✅ API端点返回200状态码")
    print("2. ✅ CORS预检请求返回200状态码")
    print("3. ✅ POST请求返回401（认证错误，但CORS正确）")
    print("4. ✅ 前端配置文件存在且包含生产域名")
    print("\n如果仍有405错误，请检查：")
    print("1. Nginx反向代理配置")
    print("2. 域名DNS解析")
    print("3. 防火墙设置")
    print("4. 后端服务是否正常运行")

if __name__ == "__main__":
    main()
