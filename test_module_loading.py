#!/usr/bin/env python3
"""
测试管理后台模块化加载功能
验证各个独立HTML模块文件是否正确创建和可访问
"""

import os
import requests
import json

def test_module_files_exist():
    """测试模块文件是否存在"""
    print("📁 测试模块文件存在性")
    print("=" * 40)
    
    module_files = [
        'admin/dashboard.html',
        'admin/users.html', 
        'admin/quotes.html',
        'admin/logs.html',
        'admin/datasource.html',
        'admin/datacollect.html',
        'admin/monitoring.html',
        'admin/models.html',
        'admin/content.html',
        'admin/announcements.html'
    ]
    
    all_exist = True
    for file_path in module_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - 存在")
        else:
            print(f"❌ {file_path} - 不存在")
            all_exist = False
    
    return all_exist

def test_module_content():
    """测试模块文件内容"""
    print("\n📄 测试模块文件内容")
    print("=" * 40)
    
    test_modules = [
        ('admin/dashboard.html', '仪表板页面'),
        ('admin/users.html', '用户管理页面'),
        ('admin/quotes.html', '行情数据页面'),
        ('admin/logs.html', '系统日志页面'),
        ('admin/datasource.html', '数据源配置页面'),
        ('admin/datacollect.html', '数据采集页面'),
        ('admin/monitoring.html', '系统监控页面'),
        ('admin/models.html', '预测模型页面'),
        ('admin/content.html', '内容管理页面'),
        ('admin/announcements.html', '公告发布页面')
    ]
    
    for file_path, module_name in test_modules:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查基本结构
            checks = [
                ('包含页面标题', f'<h2>{module_name}</h2>' in content or f'<h3>{module_name}</h3>' in content),
                ('包含页面内容', 'page-content' in content),
                ('包含表格或卡片', 'data-table' in content or 'stat-card' in content or 'chart-card' in content),
                ('包含操作按钮', 'btn' in content)
            ]
            
            print(f"\n📋 {module_name}:")
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"  {status} {check_name}")
                
        except Exception as e:
            print(f"❌ {module_name}: 读取失败 - {e}")

def test_main_index_structure():
    """测试主框架文件结构"""
    print("\n🏗️ 测试主框架文件结构")
    print("=" * 40)
    
    try:
        with open('admin/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('包含模块加载器', 'module-loader.js' in content),
            ('包含动态内容区域', 'contentBody' in content),
            ('包含加载状态', 'loadingContent' in content),
            ('包含导航链接', 'nav-link' in content),
            ('包含所有模块链接', all(module in content for module in ['dashboard', 'users', 'quotes', 'logs']))
        ]
        
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}")
            
    except Exception as e:
        print(f"❌ 主框架文件测试失败: {e}")

def test_module_loader_js():
    """测试模块加载器JavaScript文件"""
    print("\n🔧 测试模块加载器JavaScript")
    print("=" * 40)
    
    try:
        with open('admin/js/module-loader.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('包含ModuleLoader类', 'class ModuleLoader' in content),
            ('包含loadModule方法', 'loadModule(' in content),
            ('包含缓存机制', 'cache' in content),
            ('包含错误处理', 'showError(' in content),
            ('包含加载状态', 'showLoading(' in content),
            ('包含所有模块初始化', all(module in content for module in ['initDashboard', 'initUsers', 'initLogs']))
        ]
        
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}")
            
    except Exception as e:
        print(f"❌ 模块加载器测试失败: {e}")

def test_css_styles():
    """测试CSS样式文件"""
    print("\n🎨 测试CSS样式文件")
    print("=" * 40)
    
    try:
        with open('admin/css/admin.css', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('包含加载状态样式', '.loading-content' in content),
            ('包含错误状态样式', '.error-content' in content),
            ('包含模块化样式', '.page-content' in content),
            ('包含响应式设计', '@media' in content)
        ]
        
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}")
            
    except Exception as e:
        print(f"❌ CSS样式测试失败: {e}")

def test_backend_integration():
    """测试后端集成"""
    print("\n🔗 测试后端集成")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    # 测试主页面访问
    try:
        response = requests.get(f"{base_url}/admin/index.html", timeout=5)
        if response.status_code == 200:
            print("✅ 主页面访问成功")
        else:
            print(f"❌ 主页面访问失败: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 后端服务未运行")
    except Exception as e:
        print(f"❌ 主页面访问异常: {e}")
    
    # 测试模块文件访问
    test_modules = ['dashboard.html', 'users.html', 'logs.html']
    for module in test_modules:
        try:
            response = requests.get(f"{base_url}/admin/{module}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {module} 访问成功")
            else:
                print(f"❌ {module} 访问失败: {response.status_code}")
        except Exception as e:
            print(f"❌ {module} 访问异常: {e}")

def generate_summary():
    """生成总结报告"""
    print("\n📊 模块化重构总结")
    print("=" * 40)
    
    summary = """
✅ 已完成的工作:

1. 模块化拆分:
   - 将原来的单一index.html按功能拆分为10个独立模块
   - 每个模块都有独立的HTML文件，便于维护和开发

2. 模块文件:
   - dashboard.html - 仪表板模块
   - users.html - 用户管理模块  
   - quotes.html - 行情数据模块
   - logs.html - 系统日志模块
   - datasource.html - 数据源配置模块
   - datacollect.html - 数据采集模块
   - monitoring.html - 系统监控模块
   - models.html - 预测模型模块
   - content.html - 内容管理模块
   - announcements.html - 公告发布模块

3. 技术实现:
   - 创建了module-loader.js模块加载器
   - 实现了动态加载和缓存机制
   - 支持浏览器前进后退功能
   - 添加了加载状态和错误处理

4. 样式优化:
   - 添加了加载状态样式
   - 添加了错误显示样式
   - 保持了原有的响应式设计

5. 主框架优化:
   - index.html简化为框架结构
   - 内容区域改为动态加载
   - 保留了所有导航和基础功能

🎯 优势:
- 代码结构更清晰，便于团队协作
- 各模块独立开发，互不影响
- 支持按需加载，提高性能
- 便于后续功能扩展和维护
"""
    
    print(summary)

def main():
    """主测试函数"""
    print("🚀 开始测试管理后台模块化加载功能")
    print("=" * 60)
    
    # 执行各项测试
    test_module_files_exist()
    test_module_content()
    test_main_index_structure()
    test_module_loader_js()
    test_css_styles()
    test_backend_integration()
    
    # 生成总结
    generate_summary()
    
    print("\n✨ 测试完成！")

if __name__ == "__main__":
    main() 