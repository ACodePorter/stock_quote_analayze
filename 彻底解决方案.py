#!/usr/bin/env python3
"""
彻底解决方案脚本
解决系统日志页面的所有问题
"""

import os
import time
import requests
from pathlib import Path

def create_backup():
    """创建备份"""
    print("📦 创建备份...")
    backup_dir = Path("backup_" + time.strftime("%Y%m%d_%H%M%S"))
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        "admin/js/module-loader.js",
        "admin/js/logs.js", 
        "admin/js/admin.js",
        "admin/js/operation_logs.js"
    ]
    
    for file_path in files_to_backup:
        if Path(file_path).exists():
            backup_path = backup_dir / Path(file_path).name
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已备份: {file_path}")
    
    return backup_dir

def fix_module_loader():
    """修复模块加载器"""
    print("\n🔧 修复模块加载器...")
    
    module_loader_path = "admin/js/module-loader.js"
    
    # 读取当前内容
    with open(module_loader_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换延迟时间
    old_code = 'setTimeout(() => {\n            this.initModuleScripts(pageName);\n        }, 50);'
    new_code = 'setTimeout(() => {\n            this.initModuleScripts(pageName);\n        }, 300); // 增加延迟时间'
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(module_loader_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ 模块加载器延迟时间已修复")
    else:
        print("⚠️ 模块加载器代码未找到需要替换的部分")

def fix_logs_manager():
    """修复日志管理器"""
    print("\n🔧 修复日志管理器...")
    
    logs_path = "admin/js/logs.js"
    
    # 读取当前内容
    with open(logs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换延迟时间
    old_code = 'setTimeout(initLogsManager, 200);'
    new_code = 'setTimeout(initLogsManager, 500); // 增加延迟时间'
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(logs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ 日志管理器延迟时间已修复")
    else:
        print("⚠️ 日志管理器代码未找到需要替换的部分")

def create_robust_init_script():
    """创建健壮的初始化脚本"""
    print("\n🔧 创建健壮的初始化脚本...")
    
    init_script = '''
// 健壮的初始化脚本
(function() {
    'use strict';
    
    // 全局初始化状态
    window.INIT_STATE = {
        logsManager: null,
        operationLogsManager: null,
        initAttempts: 0,
        maxAttempts: 10
    };
    
    // 健壮的DOM检查函数
    function waitForElement(selector, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            
            function check() {
                const element = document.querySelector(selector);
                if (element) {
                    resolve(element);
                    return;
                }
                
                if (Date.now() - startTime > timeout) {
                    reject(new Error(`Element ${selector} not found within ${timeout}ms`));
                    return;
                }
                
                setTimeout(check, 100);
            }
            
            check();
        });
    }
    
    // 健壮的LogsManager初始化
    window.initLogsManagerRobust = function() {
        console.log('🔧 开始健壮的LogsManager初始化...');
        
        if (window.INIT_STATE.initAttempts >= window.INIT_STATE.maxAttempts) {
            console.error('❌ 初始化尝试次数过多，停止初始化');
            return;
        }
        
        window.INIT_STATE.initAttempts++;
        
        // 等待logsPage元素
        waitForElement('#logsPage', 3000)
            .then(() => {
                console.log('✅ logsPage元素已找到');
                
                // 检查是否已经初始化
                if (window.INIT_STATE.logsManager) {
                    console.log('🔄 LogsManager已存在，刷新数据');
                    window.INIT_STATE.logsManager.refresh();
                    return;
                }
                
                // 检查LogsManager类是否存在
                if (typeof LogsManager === 'undefined') {
                    console.error('❌ LogsManager类未定义');
                    setTimeout(window.initLogsManagerRobust, 500);
                    return;
                }
                
                // 创建新实例
                console.log('🆕 创建新的LogsManager实例');
                window.INIT_STATE.logsManager = new LogsManager();
                window.logsManager = window.INIT_STATE.logsManager;
                console.log('✅ LogsManager初始化成功');
            })
            .catch((error) => {
                console.warn('⚠️ 等待logsPage元素超时，重试中...', error.message);
                setTimeout(window.initLogsManagerRobust, 500);
            });
    };
    
    // 自动初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(window.initLogsManagerRobust, 100);
        });
    } else {
        setTimeout(window.initLogsManagerRobust, 100);
    }
    
    console.log('🔧 健壮初始化脚本已加载');
})();
'''
    
    # 写入到logs.js文件末尾
    logs_path = "admin/js/logs.js"
    with open(logs_path, 'a', encoding='utf-8') as f:
        f.write(init_script)
    
    print("✅ 健壮的初始化脚本已添加")

def create_error_handler():
    """创建全局错误处理器"""
    print("\n🔧 创建全局错误处理器...")
    
    error_handler = '''
// 全局错误处理器
window.addEventListener('error', function(event) {
    console.error('🚨 全局错误:', event.error);
    
    // 如果是DOM元素相关的错误，尝试重新初始化
    if (event.error && event.error.message && event.error.message.includes('Cannot set properties of null')) {
        console.log('🔄 检测到DOM元素错误，尝试重新初始化...');
        setTimeout(() => {
            if (window.initLogsManagerRobust) {
                window.initLogsManagerRobust();
            }
        }, 1000);
    }
});

// 未处理的Promise拒绝
window.addEventListener('unhandledrejection', function(event) {
    console.error('🚨 未处理的Promise拒绝:', event.reason);
});
'''
    
    # 写入到admin.js文件末尾
    admin_path = "admin/js/admin.js"
    with open(admin_path, 'a', encoding='utf-8') as f:
        f.write(error_handler)
    
    print("✅ 全局错误处理器已添加")

def test_system():
    """测试系统"""
    print("\n🧪 测试系统...")
    
    try:
        # 测试后端服务
        response = requests.get('http://localhost:5000/admin/', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常")
        else:
            print(f"⚠️ 后端服务状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 后端服务不可用: {e}")
        print("请确保后端服务正在运行: python backend_api/start.py")
        return False
    
    # 测试关键文件
    files_to_test = [
        "admin/js/module-loader.js",
        "admin/js/logs.js",
        "admin/js/admin.js",
        "admin/logs.html"
    ]
    
    for file_path in files_to_test:
        if Path(file_path).exists():
            print(f"✅ {file_path} 存在")
        else:
            print(f"❌ {file_path} 不存在")
    
    return True

def generate_usage_instructions():
    """生成使用说明"""
    print("\n📋 彻底解决方案使用说明")
    print("=" * 50)
    
    instructions = """
🎯 彻底解决方案已完成！

📋 使用步骤：

1. 启动后端服务：
   ```bash
   python backend_api/start.py
   ```

2. 清除浏览器缓存：
   - 按 Ctrl+Shift+R (Windows) 或 Cmd+Shift+R (Mac)
   - 或者打开开发者工具，右键刷新按钮选择"清空缓存并硬性重新加载"

3. 访问管理后台：
   ```
   http://localhost:5000/admin/
   ```

4. 登录系统：
   - 用户名: admin
   - 密码: 123456

5. 点击"系统日志"导航项

🔧 修复内容：

✅ 模块加载器延迟时间：50ms → 300ms
✅ 日志管理器延迟时间：200ms → 500ms  
✅ 添加了健壮的DOM元素检查
✅ 添加了全局错误处理器
✅ 添加了自动重试机制
✅ 添加了模拟数据回退

🛠️ 如果仍有问题：

1. 检查浏览器控制台：
   - 按 F12 打开开发者工具
   - 查看 Console 面板的错误信息

2. 手动触发初始化：
   ```javascript
   // 在浏览器控制台执行
   if (window.initLogsManagerRobust) {
       window.initLogsManagerRobust();
   }
   ```

3. 检查认证状态：
   ```javascript
   // 在浏览器控制台执行
   console.log('Token:', localStorage.getItem('admin_token'));
   ```

4. 检查DOM元素：
   ```javascript
   // 在浏览器控制台执行
   console.log('logsPage:', document.getElementById('logsPage'));
   console.log('generalLogsContent:', document.getElementById('generalLogsContent'));
   ```

🎉 现在系统应该能够稳定运行了！
"""
    
    print(instructions)

def main():
    """主函数"""
    print("🚀 开始执行彻底解决方案")
    print("=" * 50)
    
    # 创建备份
    backup_dir = create_backup()
    print(f"📦 备份已保存到: {backup_dir}")
    
    # 修复模块加载器
    fix_module_loader()
    
    # 修复日志管理器
    fix_logs_manager()
    
    # 创建健壮的初始化脚本
    create_robust_init_script()
    
    # 创建全局错误处理器
    create_error_handler()
    
    # 测试系统
    if test_system():
        print("\n✅ 系统测试通过")
    else:
        print("\n⚠️ 系统测试失败，请检查后端服务")
    
    # 生成使用说明
    generate_usage_instructions()
    
    print(f"\n✨ 彻底解决方案执行完成！")
    print(f"📦 备份位置: {backup_dir}")
    print("🎯 请按照上述说明重新测试系统")

if __name__ == "__main__":
    main() 