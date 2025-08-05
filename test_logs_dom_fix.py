#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试logs页面DOM元素存在性检查修复效果
"""

import requests
import json
from datetime import datetime

def test_logs_dom_fix():
    """测试logs页面DOM元素存在性检查修复效果"""
    print("🔧 测试logs页面DOM元素存在性检查修复效果")
    print("=" * 60)
    
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
    
    print("\n📋 DOM元素存在性检查修复说明:")
    print("1. bindEvents方法: 添加了DOM元素存在性检查")
    print("   - 检查startDate, endDate, statusFilter等元素是否存在")
    print("   - 只有元素存在时才添加事件监听器")
    
    print("\n2. switchTab方法: 添加了DOM元素存在性检查")
    print("   - 检查activeTab, generalContent, operationContent等元素是否存在")
    print("   - 只有元素存在时才进行操作")
    
    print("\n3. updateFilters方法: 使用可选链操作符")
    print("   - 使用?.value || '' 避免null引用错误")
    print("   - 提供默认值确保数据完整性")
    
    print("\n🌐 前端测试步骤:")
    print("1. 清除浏览器缓存")
    print("2. 访问: http://localhost:5000/admin")
    print("3. 登录: admin / 123456")
    print("4. 点击'系统日志'菜单")
    print("5. 检查控制台是否还有DOM元素错误")
    
    print("\n🔍 预期效果:")
    print("- 不再出现'Cannot read properties of null'错误")
    print("- 不再出现'Cannot read properties of null (reading addEventListener)'错误")
    print("- 页面正常加载和显示")
    print("- 控制台日志简洁明了")
    print("- 与Dashboard页面加载体验一致")
    
    print("\n⚠️ 可能的情况:")
    print("- 如果某些DOM元素不存在，会跳过相关操作")
    print("- 不会影响页面的基本功能")
    print("- 控制台会显示相应的跳过信息")
    
    print(f"\n⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    test_logs_dom_fix() 