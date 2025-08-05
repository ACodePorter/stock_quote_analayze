#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试logs页面修复效果
"""

import requests
import json
from datetime import datetime

def test_logs_page_fix():
    """测试logs页面修复效果"""
    print("🔧 测试logs页面修复效果")
    print("=" * 50)
    
    # 测试后端API
    try:
        # 登录获取token
        login_data = {
            'username': 'admin',
            'password': '123456'
        }
        
        session = requests.Session()
        response = session.post(
            'http://localhost:5000/api/admin/auth/login',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            print("✅ 登录成功")
            
            # 测试logs API
            headers = {'Authorization': f'Bearer {token}'}
            response = session.get(
                'http://localhost:5000/api/admin/logs/stats/historical_collect',
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                print("✅ Logs API正常")
                print("✅ 后端功能正常")
            else:
                print(f"❌ Logs API异常: {response.status_code}")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 后端测试失败: {e}")
    
    print("\n📋 前端修复说明:")
    print("1. 移除了复杂的initLogsManagerRobust函数")
    print("2. 简化了初始化逻辑，参考Dashboard实现")
    print("3. 移除了全局错误处理器中的复杂重试逻辑")
    print("4. 统一通过AdminPanel管理页面数据加载")
    
    print("\n🌐 前端测试步骤:")
    print("1. 清除浏览器缓存")
    print("2. 访问: http://localhost:5000/admin")
    print("3. 登录: admin / 123456")
    print("4. 点击'系统日志'菜单")
    print("5. 检查控制台是否还有无限循环错误")
    
    print("\n🔍 预期效果:")
    print("- 不再出现'等待logsPage元素超时'的无限循环")
    print("- 页面正常加载和显示")
    print("- 控制台日志简洁明了")
    print("- 与Dashboard页面加载体验一致")
    
    print(f"\n⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

if __name__ == "__main__":
    test_logs_page_fix() 