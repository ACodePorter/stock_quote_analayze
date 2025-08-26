#!/usr/bin/env python3
"""
数据库连接测试脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入配置
DATABASE_CONFIG = {
    "url": "postgresql+psycopg2://postgres:qidianspacetime@192.168.31.237:5446/stock_analysis",
    "pool_size": 5,
    "max_overflow": 10,
    "echo": False
}

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import User

# 创建数据库引擎
engine = create_engine(
    DATABASE_CONFIG["url"],
    pool_size=DATABASE_CONFIG["pool_size"],
    max_overflow=DATABASE_CONFIG["max_overflow"],
    echo=DATABASE_CONFIG["echo"]
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    
    try:
        # 测试基本连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ 数据库连接成功")
            
            # 检查用户表是否存在
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"))
            table_exists = result.fetchone()[0]
            print(f"📋 用户表存在: {table_exists}")
            
            if table_exists:
                # 获取用户总数
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.fetchone()[0]
                print(f"👥 用户总数: {user_count}")
                
                # 获取用户状态统计
                result = conn.execute(text("SELECT status, COUNT(*) FROM users GROUP BY status"))
                status_stats = result.fetchall()
                print("📊 用户状态统计:")
                for status, count in status_stats:
                    print(f"   {status}: {count}")
                
                # 获取前几个用户
                result = conn.execute(text("SELECT id, username, email, status FROM users LIMIT 5"))
                users = result.fetchall()
                print("👤 前5个用户:")
                for user in users:
                    print(f"   ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 状态: {user[3]}")
                    
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    return True

def test_orm_queries():
    """测试ORM查询"""
    print("\n🔍 测试ORM查询...")
    
    try:
        db = SessionLocal()
        
        # 获取用户总数
        total_users = db.query(User).count()
        print(f"👥 ORM查询用户总数: {total_users}")
        
        # 获取活跃用户数
        active_users = db.query(User).filter(User.status == "active").count()
        print(f"✅ 活跃用户数: {active_users}")
        
        # 获取禁用用户数
        inactive_users = db.query(User).filter(User.status == "inactive").count()
        print(f"❌ 禁用用户数: {inactive_users}")
        
        # 获取暂停用户数
        suspended_users = db.query(User).filter(User.status == "suspended").count()
        print(f"⚠️ 暂停用户数: {suspended_users}")
        
        # 获取所有用户
        all_users = db.query(User).all()
        print(f"📋 所有用户: {len(all_users)}")
        for user in all_users[:3]:  # 只显示前3个
            print(f"   ID: {user.id}, 用户名: {user.username}, 状态: {user.status}")
            
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ ORM查询失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始数据库测试...")
    
    # 测试数据库连接
    if test_database_connection():
        # 测试ORM查询
        test_orm_queries()
    
    print("\n✨ 数据库测试完成")
