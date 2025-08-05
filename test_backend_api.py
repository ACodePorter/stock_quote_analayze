#!/usr/bin/env python3
"""
测试后端API是否正常工作
验证仪表板API和其他关键端点
"""

import requests
import json
import time

def test_backend_connection():
    """测试后端连接"""
    print("🔗 测试后端连接")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试根路径
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("   请确保后端服务正在运行: python backend_api/start.py")
        return False
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False
    
    return True

def test_dashboard_api():
    """测试仪表板API"""
    print("\n📊 测试仪表板API")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    # 测试仪表板统计API
    try:
        response = requests.get(f"{base_url}/api/admin/dashboard/stats", timeout=10)
        print(f"📈 仪表板统计API状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 仪表板统计API正常")
            print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        elif response.status_code == 401:
            print("⚠️ 需要认证，这是正常的")
        else:
            print(f"❌ 仪表板统计API异常: {response.text}")
            
    except Exception as e:
        print(f"❌ 仪表板统计API测试失败: {e}")
    
    # 测试最近活动API
    try:
        response = requests.get(f"{base_url}/api/admin/dashboard/recent-activities", timeout=10)
        print(f"📋 最近活动API状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 最近活动API正常")
            print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        elif response.status_code == 401:
            print("⚠️ 需要认证，这是正常的")
        else:
            print(f"❌ 最近活动API异常: {response.text}")
            
    except Exception as e:
        print(f"❌ 最近活动API测试失败: {e}")

def test_admin_auth():
    """测试管理员认证"""
    print("\n🔐 测试管理员认证")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    # 测试登录API
    try:
        login_data = {
            "username": "admin",
            "password": "123456"
        }
        
        response = requests.post(
            f"{base_url}/api/admin/auth/login",
            data=login_data,  # 使用form-data格式
            timeout=10
        )
        
        print(f"🔑 登录API状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 登录API正常")
            print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 保存token用于后续测试
            if 'access_token' in data:
                token = data['access_token']
                print(f"   获取到token: {token[:20]}...")
                return token
        else:
            print(f"❌ 登录API异常: {response.text}")
            
    except Exception as e:
        print(f"❌ 登录API测试失败: {e}")
    
    return None

def test_authenticated_apis(token):
    """测试需要认证的API"""
    if not token:
        print("⚠️ 跳过认证API测试（无token）")
        return
    
    print("\n🔒 测试认证API")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试仪表板统计API（带认证）
    try:
        response = requests.get(
            f"{base_url}/api/admin/dashboard/stats",
            headers=headers,
            timeout=10
        )
        
        print(f"📊 认证仪表板统计API状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 认证仪表板统计API正常")
            print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 认证仪表板统计API异常: {response.text}")
            
    except Exception as e:
        print(f"❌ 认证仪表板统计API测试失败: {e}")

def test_frontend_access():
    """测试前端页面访问"""
    print("\n🌐 测试前端页面访问")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    # 测试管理后台页面
    try:
        response = requests.get(f"{base_url}/admin/index.html", timeout=10)
        print(f"📄 管理后台页面状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 管理后台页面访问正常")
            if "管理后台" in response.text:
                print("✅ 页面内容正确")
            else:
                print("⚠️ 页面内容可能有问题")
        else:
            print(f"❌ 管理后台页面访问异常: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 管理后台页面访问失败: {e}")
    
    # 测试模块文件访问
    module_files = ['dashboard.html', 'logs.html', 'users.html']
    for module in module_files:
        try:
            response = requests.get(f"{base_url}/admin/{module}", timeout=5)
            print(f"📄 {module} 状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ {module} 访问正常")
            else:
                print(f"❌ {module} 访问异常")
                
        except Exception as e:
            print(f"❌ {module} 访问失败: {e}")

def generate_diagnosis():
    """生成诊断报告"""
    print("\n📋 诊断报告")
    print("=" * 40)
    
    diagnosis = """
🔍 问题诊断:

1. 前端API请求失败的可能原因:
   - 后端服务未启动
   - API端点路径不匹配
   - 认证问题
   - 网络连接问题

2. 解决方案:
   - 确保后端服务正在运行: python backend_api/start.py
   - 检查API端点路径是否正确
   - 验证认证配置
   - 检查网络连接

3. 前端配置:
   - API基础URL: http://localhost:5000/api/admin
   - 仪表板端点: /dashboard/stats
   - 认证端点: /auth/login

4. 后端配置:
   - 服务端口: 5000
   - 仪表板路由: /api/admin/dashboard
   - 认证路由: /api/admin/auth

🎯 建议:
1. 首先启动后端服务
2. 运行此测试脚本验证API
3. 检查前端配置是否正确
4. 确保认证流程正常
"""
    
    print(diagnosis)

def main():
    """主测试函数"""
    print("🚀 开始测试后端API")
    print("=" * 60)
    
    # 测试后端连接
    if not test_backend_connection():
        generate_diagnosis()
        return
    
    # 测试仪表板API
    test_dashboard_api()
    
    # 测试管理员认证
    token = test_admin_auth()
    
    # 测试认证API
    test_authenticated_apis(token)
    
    # 测试前端访问
    test_frontend_access()
    
    # 生成诊断报告
    generate_diagnosis()
    
    print("\n✨ 测试完成！")

if __name__ == "__main__":
    main() 