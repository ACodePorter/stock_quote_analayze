#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断系统日志页面问题
"""

import requests
import json
from pathlib import Path

def check_backend_api():
    """检查后端API"""
    print("🔍 检查后端API...")
    
    try:
        # 检查主端点
        response = requests.get('http://localhost:8000/', timeout=5)
        print(f"✅ 后端API运行正常 (状态码: {response.status_code})")
        
        # 检查管理员认证端点
        response = requests.post('http://localhost:8000/api/admin/auth/login', 
                               data={'username': 'admin', 'password': '123456'}, 
                               timeout=5)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print("✅ 管理员登录成功")
            
            # 测试日志相关API
            headers = {'Authorization': f'Bearer {token}'}
            
            # 测试日志查询API
            response = requests.get('http://localhost:8000/api/admin/logs/query/historical_collect', 
                                  headers=headers, timeout=5)
            print(f"📊 日志查询API: {response.status_code}")
            
            # 测试操作日志API
            response = requests.get('http://localhost:8000/api/admin/operation-logs/query', 
                                  headers=headers, timeout=5)
            print(f"📋 操作日志API: {response.status_code}")
            
        else:
            print(f"❌ 管理员登录失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 后端API检查失败: {e}")

def check_frontend_files():
    """检查前端文件"""
    print("\n📁 检查前端文件...")
    
    files_to_check = [
        ('admin/index.html', '主页面'),
        ('admin/logs.html', '日志页面'),
        ('admin/js/logs.js', '日志JavaScript'),
        ('admin/js/module-loader.js', '模块加载器'),
        ('admin/js/admin.js', '管理后台JavaScript'),
        ('admin/css/admin.css', '样式文件')
    ]
    
    for file_path, description in files_to_check:
        if Path(file_path).exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}: {file_path} (不存在)")

def check_logs_html_content():
    """检查logs.html内容"""
    print("\n📄 检查logs.html内容...")
    
    logs_html_path = Path("admin/logs.html")
    if not logs_html_path.exists():
        print("❌ logs.html文件不存在")
        return
    
    content = logs_html_path.read_text(encoding='utf-8')
    
    # 检查关键元素
    elements_to_check = [
        ('logsPage', '主容器'),
        ('tab-btn', '标签页按钮'),
        ('logsTable', '日志表格'),
        ('logsTableBody', '表格内容'),
        ('filter-section', '筛选区域'),
        ('stats-section', '统计区域'),
        ('pagination', '分页控件')
    ]
    
    for element, description in elements_to_check:
        if element in content:
            print(f"✅ {description}: {element}")
        else:
            print(f"❌ {description}: {element} (缺失)")

def check_logs_js_content():
    """检查logs.js内容"""
    print("\n📜 检查logs.js内容...")
    
    logs_js_path = Path("admin/js/logs.js")
    if not logs_js_path.exists():
        print("❌ logs.js文件不存在")
        return
    
    content = logs_js_path.read_text(encoding='utf-8')
    
    # 检查关键函数和类
    functions_to_check = [
        ('class LogsManager', 'LogsManager类'),
        ('init()', '初始化方法'),
        ('loadLogs()', '加载日志方法'),
        ('renderLogsTable', '渲染表格方法'),
        ('initLogsManager', '全局初始化函数'),
        ('refreshLogs', '刷新日志函数')
    ]
    
    for func, description in functions_to_check:
        if func in content:
            print(f"✅ {description}: {func}")
        else:
            print(f"❌ {description}: {func} (缺失)")

def check_module_loader():
    """检查模块加载器"""
    print("\n🔧 检查模块加载器...")
    
    module_loader_path = Path("admin/js/module-loader.js")
    if not module_loader_path.exists():
        print("❌ module-loader.js文件不存在")
        return
    
    content = module_loader_path.read_text(encoding='utf-8')
    
    # 检查关键功能
    features_to_check = [
        ('class ModuleLoader', 'ModuleLoader类'),
        ('loadModule', '加载模块方法'),
        ('initLogs', '初始化日志方法'),
        ('fetchModuleContent', '获取模块内容方法')
    ]
    
    for feature, description in features_to_check:
        if feature in content:
            print(f"✅ {description}: {feature}")
        else:
            print(f"❌ {description}: {feature} (缺失)")

def check_index_html_integration():
    """检查index.html集成"""
    print("\n🌐 检查index.html集成...")
    
    index_html_path = Path("admin/index.html")
    if not index_html_path.exists():
        print("❌ index.html文件不存在")
        return
    
    content = index_html_path.read_text(encoding='utf-8')
    
    # 检查关键集成点
    integration_points = [
        ('data-page="logs"', '日志页面导航'),
        ('js/logs.js', 'logs.js引用'),
        ('js/module-loader.js', 'module-loader.js引用'),
        ('系统日志', '日志页面文本'),
        ('LogsManager', 'LogsManager类引用')
    ]
    
    for point, description in integration_points:
        if point in content:
            print(f"✅ {description}: {point}")
        else:
            print(f"❌ {description}: {point} (缺失)")

def generate_solutions():
    """生成解决方案"""
    print("\n🛠️ 解决方案建议:")
    print("=" * 50)
    
    solutions = [
        "1. 确保所有JavaScript文件正确加载",
        "2. 检查浏览器控制台是否有JavaScript错误",
        "3. 验证ModuleLoader正确初始化LogsManager",
        "4. 确保logs.html内容正确加载到DOM中",
        "5. 检查API端点是否正常工作",
        "6. 验证认证token是否有效",
        "7. 确保CSS样式没有隐藏内容"
    ]
    
    for solution in solutions:
        print(f"   {solution}")
    
    print("\n🔍 调试步骤:")
    print("1. 打开浏览器开发者工具 (F12)")
    print("2. 检查Console标签页的错误信息")
    print("3. 检查Network标签页的请求状态")
    print("4. 检查Elements标签页的DOM结构")
    print("5. 确认logsPage元素存在且可见")

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 系统日志页面问题诊断工具")
    print("=" * 60)
    
    # 执行各项检查
    check_backend_api()
    check_frontend_files()
    check_logs_html_content()
    check_logs_js_content()
    check_module_loader()
    check_index_html_integration()
    
    # 生成解决方案
    generate_solutions()
    
    print("\n" + "=" * 60)
    print("📋 诊断完成")
    print("=" * 60)

if __name__ == "__main__":
    main() 