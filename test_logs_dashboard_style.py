#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试logs页面是否按照dashboard的实现方式正常工作
"""

import requests
import json
import time
from datetime import datetime

def test_backend_service():
    """测试后端服务是否正常运行"""
    try:
        response = requests.get('http://localhost:5000/api/admin/dashboard/stats', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            return True
        else:
            print(f"❌ 后端服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端服务连接失败: {e}")
        return False

def test_logs_api():
    """测试日志API是否正常"""
    try:
        # 测试日志统计API
        response = requests.get('http://localhost:5000/api/admin/logs/stats/historical_collect', timeout=5)
        if response.status_code == 200:
            print("✅ 日志统计API正常")
            return True
        else:
            print(f"❌ 日志统计API异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 日志API测试失败: {e}")
        return False

def generate_test_instructions():
    """生成测试指令"""
    instructions = f"""
📋 系统日志页面测试指令 (参考Dashboard实现方式)

🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 后端测试:
1. 后端服务状态: {'✅ 正常' if test_backend_service() else '❌ 异常'}
2. 日志API状态: {'✅ 正常' if test_logs_api() else '❌ 异常'}

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

4. 测试系统日志页面:
   - 点击"系统日志"菜单
   - 确认页面正常加载
   - 确认统计卡片显示数据
   - 确认日志表格显示内容
   - 测试标签页切换功能

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
"""
    
    print(instructions)
    
    # 保存到文件
    with open('logs_dashboard_style_test_instructions.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"\n📄 测试指令已保存到: logs_dashboard_style_test_instructions.txt")

if __name__ == "__main__":
    print("🚀 开始测试系统日志页面 (参考Dashboard实现方式)")
    print("=" * 60)
    
    generate_test_instructions()
    
    print("\n✅ 测试脚本执行完成") 