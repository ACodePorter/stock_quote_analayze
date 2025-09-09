#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5天升跌值计算系统启动脚本
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("🚀 5天升跌值计算系统启动器")
    print("=" * 60)
    print("📊 股票历史数据5天升跌%自动计算工具")
    print("🔧 支持单只股票和批量计算")
    print("📈 提供Web界面和API接口")
    print("=" * 60)

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8+")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 检查必要文件
    required_files = [
        "backend_api/main.py",
        "backend_api/trading_notes_routes.py",
        "backend_api/services/five_day_change_calculator.py",
        "frontend/five_day_change_calculator.html",
        "database/add_five_day_change_field.sql"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ 所有必要文件检查通过")
    
    # 检查依赖包
    try:
        import fastapi
        import sqlalchemy
        import requests
        print("✅ 主要依赖包检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def check_database():
    """检查数据库连接"""
    print("🔍 检查数据库连接...")
    
    try:
        # 这里可以添加数据库连接测试
        # 暂时跳过，实际使用时需要实现
        print("⚠️  数据库连接检查跳过（需要配置数据库连接）")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def start_backend_service():
    """启动后端服务"""
    print("🚀 启动后端API服务...")
    
    try:
        # 切换到backend_api目录
        os.chdir("backend_api")
        
        # 启动FastAPI服务
        cmd = [sys.executable, "main.py"]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务启动
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ 后端服务启动成功")
            return process
        else:
            print("❌ 后端服务启动失败")
            return None
            
    except Exception as e:
        print(f"❌ 启动后端服务异常: {e}")
        return None

def open_web_interface():
    """打开Web界面"""
    print("🌐 打开Web界面...")
    
    try:
        # 等待服务完全启动
        time.sleep(5)
        
        # 打开浏览器
        url = "http://localhost:8000/frontend/five_day_change_calculator.html"
        webbrowser.open(url)
        print(f"✅ Web界面已打开: {url}")
        
    except Exception as e:
        print(f"❌ 打开Web界面失败: {e}")

def run_tests():
    """运行测试"""
    print("🧪 运行功能测试...")
    
    try:
        # 运行测试脚本
        test_script = "test_five_day_change_calculation.py"
        if Path(test_script).exists():
            print(f"运行测试脚本: {test_script}")
            result = subprocess.run([sys.executable, test_script], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 测试运行成功")
                print("测试输出:")
                print(result.stdout)
            else:
                print("❌ 测试运行失败")
                print("错误输出:")
                print(result.stderr)
        else:
            print("⚠️  测试脚本不存在，跳过测试")
            
    except Exception as e:
        print(f"❌ 运行测试异常: {e}")

def show_usage_info():
    """显示使用说明"""
    print("\n" + "=" * 60)
    print("📖 使用说明")
    print("=" * 60)
    print("1. 后端API服务已启动在: http://localhost:8000")
    print("2. Web界面已打开，可以进行以下操作:")
    print("   - 计算单只股票的5天升跌%")
    print("   - 批量计算所有股票的5天升跌%")
    print("   - 监控计算状态和进度")
    print("   - 查看操作日志")
    print("3. API文档: http://localhost:8000/docs")
    print("4. 按 Ctrl+C 停止服务")
    print("=" * 60)

def main():
    """主函数"""
    print_banner()
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败，请解决上述问题后重试")
        return
    
    # 检查数据库
    if not check_database():
        print("⚠️  数据库检查失败，但继续启动（某些功能可能不可用）")
    
    # 启动后端服务
    backend_process = start_backend_service()
    if not backend_process:
        print("❌ 后端服务启动失败，系统无法运行")
        return
    
    try:
        # 打开Web界面
        open_web_interface()
        
        # 显示使用说明
        show_usage_info()
        
        # 运行测试（可选）
        run_tests()
        
        print("\n🎉 5天升跌值计算系统启动完成！")
        print("系统正在运行中，请勿关闭此终端窗口...")
        
        # 保持服务运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 收到停止信号，正在关闭服务...")
        
        # 停止后端服务
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
            print("✅ 后端服务已停止")
        
        print("👋 系统已关闭，再见！")
        
    except Exception as e:
        print(f"\n❌ 系统运行异常: {e}")
        
        # 停止后端服务
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        
        print("系统已停止")

if __name__ == "__main__":
    main()
