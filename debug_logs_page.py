#!/usr/bin/env python3
"""
详细调试系统日志页面显示问题
检查DOM状态、JavaScript执行和API响应
"""

import requests
import json
import time

def test_direct_logs_page():
    """直接测试logs.html页面"""
    print("🔍 直接测试logs.html页面")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:5000/admin/logs.html', timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print("✅ logs.html可访问")
            
            # 检查关键DOM元素
            dom_elements = [
                ('logsPage', 'id="logsPage"'),
                ('generalLogsContent', 'id="generalLogsContent"'),
                ('operationLogsContent', 'id="operationLogsContent"'),
                ('logsTable', 'id="logsTable"'),
                ('logsTableBody', 'id="logsTableBody"'),
                ('totalLogs', 'id="totalLogs"'),
                ('successLogs', 'id="successLogs"'),
                ('errorLogs', 'id="errorLogs"'),
                ('successRate', 'id="successRate"'),
                ('tab-nav', 'class="tab-nav"'),
                ('filter-section', 'class="filter-section"'),
                ('stats-section', 'class="stats-section"'),
                ('table-container', 'class="table-container"'),
                ('pagination', 'id="logsPagination"')
            ]
            
            for element_name, element_pattern in dom_elements:
                if element_pattern in content:
                    print(f"✅ {element_name}: 存在")
                else:
                    print(f"❌ {element_name}: 缺失")
                    
            # 检查JavaScript引用
            js_refs = [
                ('logs.js', 'js/logs.js'),
                ('operation_logs.js', 'js/operation_logs.js'),
                ('module-loader.js', 'js/module-loader.js')
            ]
            
            for js_name, js_path in js_refs:
                if js_path in content:
                    print(f"✅ {js_name}: 已引用")
                else:
                    print(f"❌ {js_name}: 未引用")
                    
        else:
            print(f"❌ logs.html访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试logs.html失败: {e}")

def test_logs_api_with_auth():
    """测试带认证的日志API"""
    print("\n🔐 测试带认证的日志API")
    print("=" * 50)
    
    try:
        # 登录获取token
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
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # 测试日志表列表
            print("\n📋 测试日志表列表API:")
            response = requests.get(
                'http://localhost:5000/api/admin/logs/tables',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                tables_data = response.json()
                print("✅ 日志表列表API正常")
                print(f"   返回的表: {[table.get('key') for table in tables_data.get('data', {}).get('tables', [])]}")
            else:
                print(f"❌ 日志表列表API失败: {response.status_code}")
                print(f"   响应: {response.text}")
            
            # 测试历史数据采集日志查询
            print("\n📊 测试历史数据采集日志查询:")
            response = requests.get(
                'http://localhost:5000/api/admin/logs/query/historical_collect?page=1&page_size=5',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logs_data = response.json()
                print("✅ 历史数据采集日志查询正常")
                logs = logs_data.get('data', {}).get('logs', [])
                print(f"   返回日志数量: {len(logs)}")
                if logs:
                    print(f"   第一条日志: {logs[0]}")
            else:
                print(f"❌ 历史数据采集日志查询失败: {response.status_code}")
                print(f"   响应: {response.text}")
            
            # 测试历史数据采集日志统计
            print("\n📈 测试历史数据采集日志统计:")
            response = requests.get(
                'http://localhost:5000/api/admin/logs/stats/historical_collect',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                stats_data = response.json()
                print("✅ 历史数据采集日志统计正常")
                stats = stats_data.get('data', {})
                print(f"   统计信息: {stats}")
            else:
                print(f"❌ 历史数据采集日志统计失败: {response.status_code}")
                print(f"   响应: {response.text}")
                
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试日志API失败: {e}")

def test_main_page_logs_integration():
    """测试主页面中的系统日志集成"""
    print("\n🌐 测试主页面系统日志集成")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:5000/admin/index.html', timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print("✅ 主页面可访问")
            
            # 检查系统日志导航链接
            if 'data-page="logs"' in content:
                print("✅ 系统日志导航链接存在")
            else:
                print("❌ 系统日志导航链接缺失")
            
            # 检查JavaScript文件引用
            js_files = [
                ('logs.js', 'js/logs.js'),
                ('operation_logs.js', 'js/operation_logs.js'),
                ('module-loader.js', 'js/module-loader.js'),
                ('admin.js', 'js/admin.js')
            ]
            
            for js_name, js_path in js_files:
                if js_path in content:
                    print(f"✅ {js_name}: 已引用")
                else:
                    print(f"❌ {js_name}: 未引用")
            
            # 检查模块加载器配置
            if 'initLogs()' in content:
                print("✅ 模块加载器包含logs初始化")
            elif 'case \'logs\':' in content:
                print("✅ 模块加载器包含logs case")
            else:
                print("❌ 模块加载器缺少logs初始化")
                
        else:
            print(f"❌ 主页面访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试主页面集成失败: {e}")

def generate_debug_instructions():
    """生成调试指令"""
    print("\n🔧 调试指令")
    print("=" * 50)
    
    instructions = """
🎯 浏览器调试步骤:

1. 打开浏览器开发者工具 (F12)
2. 访问: http://localhost:5000/admin/
3. 登录: admin / 123456
4. 点击"系统日志"导航项
5. 检查以下内容:

📋 Console面板检查:
- 查看是否有JavaScript错误
- 查找"初始化系统日志模块"日志
- 查找"LogsManager初始化完成"日志
- 查找API请求错误

🌐 Network面板检查:
- 查看logs.html是否成功加载
- 查看js/logs.js是否成功加载
- 查看API请求是否成功
- 检查请求状态码和响应

🔍 Elements面板检查:
- 查找#logsPage元素是否存在
- 查找#generalLogsContent元素是否存在
- 查找#operationLogsContent元素是否存在
- 检查这些元素的display属性

📊 手动测试API:
- 在Console中执行: fetch('/api/admin/logs/tables')
- 在Console中执行: fetch('/api/admin/logs/query/historical_collect?page=1&page_size=5')

🛠️ 可能的解决方案:

1. 如果DOM元素不存在:
   - 检查logs.html是否正确加载
   - 检查模块加载器是否正确渲染内容

2. 如果JavaScript错误:
   - 检查logs.js是否正确加载
   - 检查LogsManager类是否正确定义

3. 如果API请求失败:
   - 检查认证token是否有效
   - 检查后端服务是否正常运行

4. 如果内容被隐藏:
   - 检查CSS样式是否正确
   - 检查display属性设置
"""
    
    print(instructions)

def main():
    """主调试函数"""
    print("🚀 开始详细调试系统日志页面")
    print("=" * 60)
    
    # 执行各项测试
    test_direct_logs_page()
    test_logs_api_with_auth()
    test_main_page_logs_integration()
    
    # 生成调试指令
    generate_debug_instructions()
    
    print("\n✨ 调试完成！请按照上述指令在浏览器中进行调试。")

if __name__ == "__main__":
    main() 