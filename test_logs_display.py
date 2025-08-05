#!/usr/bin/env python3
"""
测试系统日志页面显示是否正常
验证logs.html内容加载和JavaScript初始化
"""

import requests
import re
import json

def test_logs_html_content():
    """测试logs.html内容"""
    print("📄 测试logs.html内容")
    print("=" * 40)
    
    try:
        response = requests.get('http://localhost:5000/admin/logs.html', timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print("✅ logs.html文件可访问")
            
            # 检查关键元素
            checks = [
                ('页面标题', '系统日志监控' in content),
                ('标签页导航', 'tab-nav' in content),
                ('历史数据采集日志标签', '历史数据采集日志' in content),
                ('实时数据采集日志标签', '实时数据采集日志' in content),
                ('系统操作日志标签', '系统操作日志' in content),
                ('自选股历史采集日志标签', '自选股历史采集日志' in content),
                ('筛选条件区域', 'filter-section' in content),
                ('统计信息区域', 'stats-section' in content),
                ('数据表格', 'data-table' in content),
                ('分页控件', 'pagination' in content),
                ('通用日志内容区域', 'generalLogsContent' in content),
                ('系统操作日志内容区域', 'operationLogsContent' in content)
            ]
            
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"{status} {check_name}")
                
            return True
        else:
            print(f"❌ logs.html访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试logs.html失败: {e}")
        return False

def test_logs_js_files():
    """测试logs.js和operation_logs.js文件"""
    print("\n📜 测试JavaScript文件")
    print("=" * 40)
    
    js_files = [
        ('logs.js', 'js/logs.js'),
        ('operation_logs.js', 'js/operation_logs.js')
    ]
    
    for file_name, file_path in js_files:
        try:
            response = requests.get(f'http://localhost:5000/admin/{file_path}', timeout=10)
            
            if response.status_code == 200:
                content = response.text
                print(f"✅ {file_name} 可访问")
                
                # 检查关键类和方法
                if file_name == 'logs.js':
                    checks = [
                        ('LogsManager类', 'class LogsManager' in content),
                        ('init方法', 'init()' in content),
                        ('refresh方法', 'refresh()' in content),
                        ('switchTab方法', 'switchTab(' in content),
                        ('loadLogs方法', 'loadLogs()' in content)
                    ]
                else:  # operation_logs.js
                    checks = [
                        ('OperationLogsManager类', 'class OperationLogsManager' in content),
                        ('init方法', 'init()' in content),
                        ('refresh方法', 'refresh()' in content),
                        ('loadData方法', 'loadData()' in content)
                    ]
                
                for check_name, result in checks:
                    status = "✅" if result else "❌"
                    print(f"  {status} {check_name}")
                    
            else:
                print(f"❌ {file_name} 访问失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试{file_name}失败: {e}")

def test_logs_api_endpoints():
    """测试日志相关API端点"""
    print("\n🔌 测试日志API端点")
    print("=" * 40)
    
    # 首先获取认证token
    try:
        login_data = {
            'username': 'admin',
            'password': '123456'
        }
        
        response = requests.post(
            'http://localhost:5000/api/admin/auth/login',
            data=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print("✅ 登录成功，获取到token")
            
            # 测试日志API端点
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            api_endpoints = [
                ('/api/admin/logs/tables', '获取日志表列表'),
                ('/api/admin/logs/stats/historical_collect', '获取历史数据采集日志统计'),
                ('/api/admin/logs/query/historical_collect', '查询历史数据采集日志'),
                ('/api/admin/operation-logs/stats', '获取系统操作日志统计'),
                ('/api/admin/operation-logs/query', '查询系统操作日志')
            ]
            
            for endpoint, description in api_endpoints:
                try:
                    response = requests.get(
                        f'http://localhost:5000{endpoint}',
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        print(f"✅ {description} - 正常")
                    elif response.status_code == 401:
                        print(f"⚠️ {description} - 需要认证")
                    else:
                        print(f"❌ {description} - 错误: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ {description} - 请求失败: {e}")
                    
        else:
            print(f"❌ 登录失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试API端点失败: {e}")

def test_main_page_integration():
    """测试主页面集成"""
    print("\n🌐 测试主页面集成")
    print("=" * 40)
    
    try:
        response = requests.get('http://localhost:5000/admin/index.html', timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print("✅ 主页面可访问")
            
            # 检查关键元素
            checks = [
                ('系统日志导航链接', 'data-page="logs"' in content),
                ('logs.js引用', 'js/logs.js' in content),
                ('operation_logs.js引用', 'js/operation_logs.js' in content),
                ('module-loader.js引用', 'js/module-loader.js' in content),
                ('系统日志文本', '系统日志' in content)
            ]
            
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"{status} {check_name}")
                
        else:
            print(f"❌ 主页面访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试主页面集成失败: {e}")

def generate_diagnosis():
    """生成诊断报告"""
    print("\n📋 系统日志显示问题诊断")
    print("=" * 40)
    
    diagnosis = """
🔍 可能的问题原因:

1. JavaScript初始化问题:
   - logs.js在页面加载时立即初始化，但DOM元素可能还未加载
   - 模块加载器没有正确调用日志模块初始化
   - 全局变量logsManager未正确暴露

2. DOM元素查找问题:
   - logs.html内容加载后，JavaScript无法找到必要的DOM元素
   - 元素ID不匹配或不存在

3. API请求问题:
   - 日志API端点不可用
   - 认证token问题
   - 网络连接问题

4. CSS样式问题:
   - 内容被隐藏或样式错误
   - 布局问题导致内容不可见

🛠️ 解决方案:

1. 修改JavaScript初始化逻辑:
   - 延迟初始化，等待DOM元素加载完成
   - 添加DOM元素存在性检查
   - 改进模块加载器的初始化调用

2. 确保API端点正常:
   - 验证后端日志API是否正常工作
   - 检查认证流程
   - 测试API响应

3. 调试步骤:
   - 打开浏览器开发者工具
   - 检查Console错误信息
   - 验证Network请求
   - 检查Elements面板中的DOM结构

🎯 建议:
1. 刷新页面并检查浏览器控制台
2. 确认后端服务正在运行
3. 验证API端点响应正常
4. 检查JavaScript文件是否正确加载
"""
    
    print(diagnosis)

def main():
    """主测试函数"""
    print("🚀 开始测试系统日志页面显示")
    print("=" * 60)
    
    # 执行各项测试
    test_logs_html_content()
    test_logs_js_files()
    test_logs_api_endpoints()
    test_main_page_integration()
    
    # 生成诊断报告
    generate_diagnosis()
    
    print("\n✨ 测试完成！")

if __name__ == "__main__":
    main() 