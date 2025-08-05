#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试logs页面是否按照dashboard的实现方式正常工作
包含认证流程
"""

import requests
import json
import time
from datetime import datetime

class AdminAPITester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.token = None
        self.session = requests.Session()
    
    def login(self):
        """登录获取token"""
        try:
            login_data = {
                'username': 'admin',
                'password': '123456'  # 修改为正确的密码
            }
            
            response = self.session.post(
                f"{self.base_url}/api/admin/auth/login",
                data=login_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=5
            )
            
            print(f"登录响应状态码: {response.status_code}")
            print(f"登录响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                # 直接获取access_token，不检查success字段
                self.token = result.get('access_token')
                if self.token:
                    print("✅ 登录成功，获取到token")
                    return True
                else:
                    print(f"❌ 登录失败: 未获取到token")
                    return False
            else:
                print(f"❌ 登录请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def test_dashboard_api(self):
        """测试dashboard API"""
        if not self.token:
            print("❌ 未登录，无法测试dashboard API")
            return False
            
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = self.session.get(
                f"{self.base_url}/api/admin/dashboard/stats",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Dashboard API正常")
                    print(f"   - 用户数: {result.get('data', {}).get('userCount', 0)}")
                    print(f"   - 股票数: {result.get('data', {}).get('stockCount', 0)}")
                    print(f"   - 行情数: {result.get('data', {}).get('quoteCount', 0)}")
                    print(f"   - 告警数: {result.get('data', {}).get('alertCount', 0)}")
                    return True
                else:
                    print(f"❌ Dashboard API返回错误: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"❌ Dashboard API请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Dashboard API异常: {e}")
            return False
    
    def test_logs_api(self):
        """测试logs API"""
        if not self.token:
            print("❌ 未登录，无法测试logs API")
            return False
            
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # 测试日志统计API
            response = self.session.get(
                f"{self.base_url}/api/admin/logs/stats/historical_collect",
                headers=headers,
                timeout=5
            )
            
            print(f"Logs API响应状态码: {response.status_code}")
            print(f"Logs API响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                # 直接处理响应数据，不检查success字段
                if 'table_key' in result:
                    print("✅ Logs API正常")
                    # 计算统计数据
                    status_stats = result.get('status_stats', [])
                    total = sum(stat.get('count', 0) for stat in status_stats)
                    success = sum(stat.get('count', 0) for stat in status_stats if stat.get('status') == 'success')
                    error = sum(stat.get('count', 0) for stat in status_stats if stat.get('status') != 'success')
                    success_rate = (success / total * 100) if total > 0 else 0
                    
                    print(f"   - 总记录数: {total}")
                    print(f"   - 成功记录: {success}")
                    print(f"   - 失败记录: {error}")
                    print(f"   - 成功率: {success_rate:.1f}%")
                    return True
                else:
                    print(f"❌ Logs API返回格式错误")
                    return False
            else:
                print(f"❌ Logs API请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Logs API异常: {e}")
            return False
    
    def test_logs_query_api(self):
        """测试logs查询API"""
        if not self.token:
            print("❌ 未登录，无法测试logs查询API")
            return False
            
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # 测试日志查询API
            response = self.session.get(
                f"{self.base_url}/api/admin/logs/query/historical_collect?page=1&page_size=10",
                headers=headers,
                timeout=5
            )
            
            print(f"Logs查询API响应状态码: {response.status_code}")
            print(f"Logs查询API响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                # 直接处理响应数据，日志数据在data字段中
                if 'data' in result:
                    logs = result.get('data', [])
                    pagination = result.get('pagination', {})
                    print("✅ Logs查询API正常")
                    print(f"   - 返回记录数: {len(logs)}")
                    print(f"   - 总页数: {pagination.get('total_pages', 0)}")
                    return True
                else:
                    print(f"❌ Logs查询API返回格式错误")
                    return False
            else:
                print(f"❌ Logs查询API请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Logs查询API异常: {e}")
            return False

def run_complete_test():
    """运行完整测试"""
    print("🚀 开始完整测试系统日志页面 (参考Dashboard实现方式)")
    print("=" * 70)
    
    tester = AdminAPITester()
    
    # 1. 测试登录
    print("\n1️⃣ 测试登录...")
    if not tester.login():
        print("❌ 登录失败，无法继续测试")
        return
    
    # 2. 测试Dashboard API
    print("\n2️⃣ 测试Dashboard API...")
    dashboard_ok = tester.test_dashboard_api()
    
    # 3. 测试Logs API
    print("\n3️⃣ 测试Logs API...")
    logs_ok = tester.test_logs_api()
    
    # 4. 测试Logs查询API
    print("\n4️⃣ 测试Logs查询API...")
    logs_query_ok = tester.test_logs_query_api()
    
    # 5. 生成测试报告
    print("\n" + "=" * 70)
    print("📊 测试报告")
    print("=" * 70)
    
    print(f"✅ 登录状态: {'成功' if tester.token else '失败'}")
    print(f"✅ Dashboard API: {'正常' if dashboard_ok else '异常'}")
    print(f"✅ Logs API: {'正常' if logs_ok else '异常'}")
    print(f"✅ Logs查询API: {'正常' if logs_query_ok else '异常'}")
    
    if dashboard_ok and logs_ok and logs_query_ok:
        print("\n🎉 所有API测试通过！")
        print("\n📋 前端测试建议:")
        print("1. 清除浏览器缓存")
        print("2. 访问 http://localhost:5000/admin")
        print("3. 登录: admin / admin123")
        print("4. 测试Dashboard页面加载")
        print("5. 测试系统日志页面加载")
        print("6. 对比两个页面的加载速度和响应性")
    else:
        print("\n⚠️  部分API测试失败，请检查后端服务")
    
    # 生成详细测试指令
    generate_detailed_instructions(dashboard_ok, logs_ok, logs_query_ok)

def generate_detailed_instructions(dashboard_ok, logs_ok, logs_query_ok):
    """生成详细的测试指令"""
    instructions = f"""
📋 系统日志页面详细测试指令 (参考Dashboard实现方式)

🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 后端API测试结果:
- Dashboard API: {'✅ 正常' if dashboard_ok else '❌ 异常'}
- Logs API: {'✅ 正常' if logs_ok else '❌ 异常'}
- Logs查询API: {'✅ 正常' if logs_query_ok else '❌ 异常'}

🌐 前端测试步骤:

1. 清除浏览器缓存:
   - Chrome: Ctrl+Shift+Delete → 清除数据
   - Firefox: Ctrl+Shift+Delete → 清除数据

2. 访问管理后台:
   - 打开: http://localhost:5000/admin
   - 登录: admin / admin123

3. 测试Dashboard页面:
   - 点击"仪表板"菜单
   - 确认统计卡片正常显示数据
   - 确认页面响应流畅
   - 记录加载时间

4. 测试系统日志页面:
   - 点击"系统日志"菜单
   - 确认页面正常加载
   - 确认统计卡片显示数据
   - 确认日志表格显示内容
   - 测试标签页切换功能
   - 记录加载时间

5. 浏览器控制台检查:
   - 按F12打开开发者工具
   - 查看Console标签页
   - 确认没有错误信息
   - 查看Network标签页确认API请求正常

6. 对比Dashboard和Logs页面:
   - 确认两个页面的加载速度相近
   - 确认两个页面的响应性相近
   - 确认两个页面的错误处理机制相近

🔍 预期改进效果:
- Logs页面初始化逻辑简化，参考Dashboard实现
- 减少复杂的DOM检查和延迟逻辑
- 通过AdminPanel统一管理页面数据加载
- 提高页面加载的稳定性和响应速度

📝 如果仍有问题，请提供:
1. 浏览器控制台的错误信息
2. Network标签页的API请求状态
3. 具体的页面显示问题描述
4. Dashboard和Logs页面的加载时间对比
"""
    
    # 保存到文件
    with open('logs_dashboard_complete_test_instructions.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"\n📄 详细测试指令已保存到: logs_dashboard_complete_test_instructions.txt")

if __name__ == "__main__":
    run_complete_test() 