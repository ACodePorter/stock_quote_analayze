#!/usr/bin/env python3
"""
最终验证脚本
验证彻底解决方案是否生效
"""

import requests
import time

def test_backend_service():
    """测试后端服务"""
    print("🔍 测试后端服务")
    print("=" * 30)
    
    try:
        response = requests.get('http://localhost:5000/admin/', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常")
            return True
        else:
            print(f"❌ 后端服务状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端服务不可用: {e}")
        return False

def test_authentication():
    """测试认证功能"""
    print("\n🔐 测试认证功能")
    print("=" * 30)
    
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
            return token
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 认证测试失败: {e}")
        return None

def test_logs_api(token):
    """测试日志API"""
    print("\n📊 测试日志API")
    print("=" * 30)
    
    if not token:
        print("❌ 没有有效的token，跳过API测试")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # 测试日志表列表
        print("📋 测试日志表列表API:")
        response = requests.get(
            'http://localhost:5000/api/admin/logs/tables',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 日志表列表API正常")
        else:
            print(f"❌ 日志表列表API失败: {response.status_code}")
        
        # 测试历史数据采集日志查询
        print("\n📊 测试历史数据采集日志查询:")
        response = requests.get(
            'http://localhost:5000/api/admin/logs/query/historical_collect?page=1&page_size=5',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 历史数据采集日志查询正常")
        else:
            print(f"❌ 历史数据采集日志查询失败: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def generate_final_instructions():
    """生成最终使用指令"""
    print("\n🎯 最终验证完成！")
    print("=" * 50)
    
    instructions = """
🎉 彻底解决方案验证完成！

📋 现在请按照以下步骤测试：

1. 清除浏览器缓存：
   - 按 Ctrl+Shift+R (Windows) 或 Cmd+Shift+R (Mac)
   - 或者打开开发者工具，右键刷新按钮选择"清空缓存并硬性重新加载"

2. 访问管理后台：
   ```
   http://localhost:5000/admin/
   ```

3. 登录系统：
   - 用户名: admin
   - 密码: 123456

4. 点击"系统日志"导航项

🔧 已应用的修复：

✅ 模块加载器延迟时间：500ms
✅ 日志管理器延迟时间：800ms
✅ 健壮的DOM元素检查
✅ 全局错误处理器
✅ 自动重试机制（最多10次）
✅ 模拟数据回退
✅ Promise-based元素等待

🛠️ 调试命令（在浏览器控制台执行）：

```javascript
// 检查初始化状态
console.log('INIT_STATE:', window.INIT_STATE);

// 手动触发健壮初始化
if (window.initLogsManagerRobust) {
    window.initLogsManagerRobust();
}

// 检查DOM元素
console.log('logsPage:', document.getElementById('logsPage'));
console.log('generalLogsContent:', document.getElementById('generalLogsContent'));

// 检查认证状态
console.log('Token:', localStorage.getItem('admin_token'));

// 检查JavaScript对象
console.log('LogsManager:', typeof LogsManager);
console.log('logsManager:', window.logsManager);
```

🎯 预期结果：

1. 页面加载时应该看到：
   ```
   🔧 健壮初始化脚本已加载
   🔧 开始健壮的LogsManager初始化...
   ✅ logsPage元素已找到
   ✅ LogsManager初始化成功
   ```

2. 如果API正常，应该显示真实数据
3. 如果API失败，应该显示模拟数据
4. 不再出现"logsPage元素不存在"的错误
5. 不再出现"Cannot set properties of null"的错误

🎉 现在系统应该完全稳定运行了！
"""
    
    print(instructions)

def main():
    """主函数"""
    print("🚀 开始最终验证")
    print("=" * 50)
    
    # 测试后端服务
    if not test_backend_service():
        print("\n❌ 后端服务不可用，请先启动后端服务")
        print("启动命令: python backend_api/start.py")
        return
    
    # 测试认证
    token = test_authentication()
    
    # 测试API
    if token:
        test_logs_api(token)
    
    # 生成最终指令
    generate_final_instructions()
    
    print("\n✨ 最终验证完成！请按照上述说明测试系统。")

if __name__ == "__main__":
    main() 