#!/usr/bin/env python3
"""
项目启动脚本
在项目根目录运行此脚本来启动后端服务
"""

import uvicorn
import sys
import os

# 添加backend_api目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend_api'))

if __name__ == "__main__":
    print("🚀 启动股票分析系统后端服务...")
    print(f"📁 当前工作目录: {os.getcwd()}")
    print(f"🐍 Python路径: {sys.path[0]}")
    
    try:
        # 启动FastAPI服务
        uvicorn.run(
            "main:app",  # 从backend_api目录导入main模块
            host="0.0.0.0",
            port=5000,
            reload=True,
            reload_dirs=["backend_api"],  # 只监听backend_api目录的变化
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"❌ 启动服务失败: {e}")
        sys.exit(1) 