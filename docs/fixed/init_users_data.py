"""
初始化用户数据脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend_api.database import get_db
from backend_api.models import User
from backend_api.auth import get_password_hash
from datetime import datetime

def create_sample_users():
    """创建示例用户数据"""
    db = next(get_db())
    
    # 检查是否已有用户
    existing_users = db.query(User).count()
    if existing_users > 1:  # 假设至少有一个admin用户
        print("用户数据已存在，跳过初始化")
        return
    
    sample_users = [
        {
            "username": "admin",
            "email": "admin@example.com", 
            "password": "123456",
            "status": "active",
            "role": "admin"
        },
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "password123",
            "status": "active", 
            "role": "user"
        },
        {
            "username": "jane_smith",
            "email": "jane@example.com",
            "password": "password123",
            "status": "active",
            "role": "user"
        },
        {
            "username": "bob_wilson",
            "email": "bob@example.com", 
            "password": "password123",
            "status": "inactive",
            "role": "user"
        },
        {
            "username": "alice_brown",
            "email": "alice@example.com",
            "password": "password123", 
            "status": "suspended",
            "role": "guest"
        }
    ]
    
    for user_data in sample_users:
        # 检查用户是否已存在
        existing = db.query(User).filter(
            (User.username == user_data["username"]) | 
            (User.email == user_data["email"])
        ).first()
        
        if not existing:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                status=user_data["status"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(user)
            print(f"创建用户: {user_data['username']}")
        else:
            print(f"用户已存在: {user_data['username']}")
    
    try:
        db.commit()
        print("用户数据初始化完成")
    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_users()
