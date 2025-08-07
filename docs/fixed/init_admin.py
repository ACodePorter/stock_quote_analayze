#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化admin表和管理员账号
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend_api.database import SessionLocal, engine, Base
from backend_api.models import Admin
from backend_api.auth import get_password_hash
from sqlalchemy import inspect
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_admin_table():
    """初始化admin表"""
    logger.info("🔧 初始化admin表...")
    
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表创建完成")
        
        # 检查admin表是否存在
        inspector = inspect(engine)
        if inspector.has_table('admins'):
            logger.info("✅ admins表已存在")
        else:
            logger.error("❌ admins表创建失败")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"❌ 初始化admin表失败: {e}")
        return False

def create_default_admin():
    """创建默认管理员账号"""
    logger.info("👤 创建默认管理员账号...")
    
    db = SessionLocal()
    try:
        # 检查是否已存在管理员账号
        admin = db.query(Admin).filter(Admin.username == "admin").first()
        if admin:
            logger.info("✅ 默认管理员账号已存在")
            return True
        
        # 创建默认管理员账号
        admin = Admin(
            username="admin",
            password_hash=get_password_hash("123456"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        
        logger.info("✅ 默认管理员账号创建成功")
        logger.info("📋 账号信息:")
        logger.info("   - 用户名: admin")
        logger.info("   - 密码: 123456")
        logger.info("   - 角色: admin")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建默认管理员账号失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def verify_admin_login():
    """验证管理员登录"""
    logger.info("🔐 验证管理员登录...")
    
    db = SessionLocal()
    try:
        from backend_api.auth import authenticate_admin
        
        # 测试登录
        admin = authenticate_admin(db, "admin", "123456")
        if admin:
            logger.info("✅ 管理员登录验证成功")
            return True
        else:
            logger.error("❌ 管理员登录验证失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 验证管理员登录失败: {e}")
        return False
    finally:
        db.close()

def main():
    """主函数"""
    logger.info("🚀 开始初始化admin系统...")
    
    # 1. 初始化admin表
    if not init_admin_table():
        logger.error("❌ 初始化admin表失败")
        return
    
    # 2. 创建默认管理员账号
    if not create_default_admin():
        logger.error("❌ 创建默认管理员账号失败")
        return
    
    # 3. 验证管理员登录
    if not verify_admin_login():
        logger.error("❌ 验证管理员登录失败")
        return
    
    logger.info("""
🎉 Admin系统初始化完成！

📋 系统信息:
- 数据库表: ✅ 已创建
- 管理员账号: ✅ 已创建
- 登录验证: ✅ 正常

🔑 默认账号:
- 用户名: admin
- 密码: 123456
- 角色: admin

🌐 访问地址:
- 管理后台: http://localhost:8001
- 后端API: http://localhost:5000

💡 下一步:
1. 启动后端API服务: python -m backend_api.main
2. 启动管理后台: python start_admin_standalone.py
3. 访问管理后台进行登录
    """)

if __name__ == "__main__":
    main() 