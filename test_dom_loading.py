#!/usr/bin/env python3
"""
测试DOM加载和JavaScript初始化
验证logsPage元素是否正确加载
"""

import requests
import time

def test_dom_loading():
    """测试DOM加载"""
    print("🔍 测试DOM加载")
    print("=" * 40)
    
    try:
        # 测试logs.html内容
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
                ('successRate', 'id="successRate"')
            ]
            
            missing_elements = []
            for element_name, element_pattern in dom_elements:
                if element_pattern in content:
                    print(f"✅ {element_name}: 存在")
                else:
                    print(f"❌ {element_name}: 缺失")
                    missing_elements.append(element_name)
            
            if missing_elements:
                print(f"\n⚠️ 缺失的元素: {', '.join(missing_elements)}")
                return False
            else:
                print("\n✅ 所有DOM元素都存在")
                return True
                
        else:
            print(f"❌ logs.html访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_module_loader():
    """测试模块加载器"""
    print("\n📦 测试模块加载器")
    print("=" * 40)
    
    try:
        response = requests.get('http://localhost:5000/admin/js/module-loader.js', timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print("✅ module-loader.js可访问")
            
            # 检查关键方法
            methods = [
                ('renderModule', 'renderModule(pageName, content)'),
                ('initModuleScripts', 'initModuleScripts(pageName)'),
                ('initLogs', 'initLogs()'),
                ('setTimeout', 'setTimeout(() => {')
            ]
            
            for method_name, method_pattern in methods:
                if method_pattern in content:
                    print(f"✅ {method_name}: 存在")
                else:
                    print(f"❌ {method_name}: 缺失")
                    
        else:
            print(f"❌ module-loader.js访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def generate_debug_instructions():
    """生成调试指令"""
    print("\n🔧 调试指令")
    print("=" * 40)
    
    instructions = """
🎯 浏览器调试步骤:

1. 打开浏览器开发者工具 (F12)
2. 访问: http://localhost:5000/admin/
3. 登录: admin / 123456
4. 点击"系统日志"导航项
5. 在Console中执行以下命令:

📋 DOM检查命令:
```javascript
// 检查logsPage元素是否存在
console.log('logsPage元素:', document.getElementById('logsPage'));

// 检查generalLogsContent元素是否存在
console.log('generalLogsContent元素:', document.getElementById('generalLogsContent'));

// 检查operationLogsContent元素是否存在
console.log('operationLogsContent元素:', document.getElementById('operationLogsContent'));

// 检查所有相关元素
const elements = ['logsPage', 'generalLogsContent', 'operationLogsContent', 'logsTable', 'totalLogs'];
elements.forEach(id => {
    const element = document.getElementById(id);
    console.log(`${id}:`, element ? '存在' : '不存在');
});
```

🔍 模块加载器检查:
```javascript
// 检查模块加载器是否存在
console.log('moduleLoader:', window.moduleLoader);

// 检查当前模块
console.log('当前模块:', window.moduleLoader?.currentModule);

// 检查缓存
console.log('缓存:', window.moduleLoader?.cache);
```

📊 JavaScript初始化检查:
```javascript
// 检查LogsManager类
console.log('LogsManager类:', typeof LogsManager);

// 检查logsManager实例
console.log('logsManager实例:', window.logsManager);

// 检查initLogsManager函数
console.log('initLogsManager函数:', typeof window.initLogsManager);
```

🛠️ 手动触发初始化:
```javascript
// 手动触发日志管理器初始化
if (window.initLogsManager) {
    window.initLogsManager();
}

// 或者手动创建LogsManager实例
if (typeof LogsManager !== 'undefined' && !window.logsManager) {
    window.logsManager = new LogsManager();
}
```

📞 如果仍有问题，请提供:
1. 上述命令的执行结果
2. Console面板的错误信息
3. Network面板的请求状态
4. Elements面板的DOM结构截图
"""
    
    print(instructions)

def main():
    """主测试函数"""
    print("🚀 测试DOM加载和JavaScript初始化")
    print("=" * 50)
    
    # 测试DOM加载
    if test_dom_loading():
        print("\n✅ DOM加载测试通过")
    else:
        print("\n❌ DOM加载测试失败")
    
    # 测试模块加载器
    test_module_loader()
    
    # 生成调试指令
    generate_debug_instructions()
    
    print("\n✨ 测试完成！请按照上述指令在浏览器中进行调试。")

if __name__ == "__main__":
    main() 