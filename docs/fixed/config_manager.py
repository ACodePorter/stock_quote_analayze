#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境配置管理脚本
统一管理所有模块的环境变量配置
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigManager:
    """环境配置管理器"""
    
    def __init__(self, env_file: str = ".env"):
        """
        初始化配置管理器
        
        Args:
            env_file: 环境变量文件路径
        """
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / env_file
        self.config = {}
        self.load_environment()
    
    def load_environment(self):
        """加载环境变量"""
        # 加载.env文件
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logger.info(f"✅ 已加载环境变量文件: {self.env_file}")
        else:
            logger.warning(f"⚠️  环境变量文件不存在: {self.env_file}")
        
        # 加载系统环境变量
        self._load_system_env()
    
    def _load_system_env(self):
        """加载系统环境变量"""
        self.config = {
            # 环境配置
            'ENVIRONMENT': os.getenv('ENVIRONMENT', 'development'),
            'DEBUG': os.getenv('DEBUG', 'true').lower() == 'true',
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            
            # 数据库配置
            'DB_TYPE': os.getenv('DB_TYPE', 'postgresql'),
            'DB_HOST': os.getenv('DB_HOST', '192.168.31.237'),
            'DB_PORT': int(os.getenv('DB_PORT', '5446')),
            'DB_NAME': os.getenv('DB_NAME', 'stock_analysis'),
            'DB_USER': os.getenv('DB_USER', 'postgres'),
            'DB_PASSWORD': os.getenv('DB_PASSWORD', 'qidianspacetime'),
            'DB_POOL_SIZE': int(os.getenv('DB_POOL_SIZE', '5')),
            'DB_MAX_OVERFLOW': int(os.getenv('DB_MAX_OVERFLOW', '10')),
            'SQLITE_DB_PATH': os.getenv('SQLITE_DB_PATH', 'database/stock_analysis.db'),
            
            # Redis配置
            'REDIS_HOST': os.getenv('REDIS_HOST', 'localhost'),
            'REDIS_PORT': int(os.getenv('REDIS_PORT', '6379')),
            'REDIS_DB': int(os.getenv('REDIS_DB', '0')),
            'REDIS_PASSWORD': os.getenv('REDIS_PASSWORD', ''),
            
            # API服务配置
            'API_HOST': os.getenv('API_HOST', '0.0.0.0'),
            'API_PORT': int(os.getenv('API_PORT', '5000')),
            'API_WORKERS': int(os.getenv('API_WORKERS', '4')),
            'API_RELOAD': os.getenv('API_RELOAD', 'true').lower() == 'true',
            
            # JWT配置
            'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production'),
            'JWT_ALGORITHM': os.getenv('JWT_ALGORITHM', 'HS256'),
            'JWT_ACCESS_TOKEN_EXPIRE_MINUTES': int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '1440')),
            'JWT_REFRESH_TOKEN_EXPIRE_DAYS': int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', '30')),
            
            # CORS配置
            'CORS_ALLOW_ORIGINS': os.getenv('CORS_ALLOW_ORIGINS', 'http://localhost:8000,http://localhost:8001'),
            'CORS_ALLOW_CREDENTIALS': os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true',
            'CORS_ALLOW_METHODS': os.getenv('CORS_ALLOW_METHODS', 'GET,POST,PUT,DELETE,OPTIONS'),
            'CORS_ALLOW_HEADERS': os.getenv('CORS_ALLOW_HEADERS', '*'),
            
            # 前端配置
            'FRONTEND_HOST': os.getenv('FRONTEND_HOST', '0.0.0.0'),
            'FRONTEND_PORT': int(os.getenv('FRONTEND_PORT', '8000')),
            'ADMIN_HOST': os.getenv('ADMIN_HOST', '0.0.0.0'),
            'ADMIN_PORT': int(os.getenv('ADMIN_PORT', '8001')),
            'ADMIN_BASE_URL': os.getenv('ADMIN_BASE_URL', 'http://localhost:8001'),
            
            # 数据采集配置
            'TUSHARE_TOKEN': os.getenv('TUSHARE_TOKEN', '9701deb356e76d8d9918d797aff060ce90bd1a24339866c02444014f'),
            'TUSHARE_TIMEOUT': int(os.getenv('TUSHARE_TIMEOUT', '30')),
            'TUSHARE_MAX_RETRIES': int(os.getenv('TUSHARE_MAX_RETRIES', '3')),
            'TUSHARE_RETRY_DELAY': int(os.getenv('TUSHARE_RETRY_DELAY', '5')),
            
            'AKSHARE_TIMEOUT': int(os.getenv('AKSHARE_TIMEOUT', '30')),
            'AKSHARE_MAX_RETRIES': int(os.getenv('AKSHARE_MAX_RETRIES', '3')),
            'AKSHARE_RETRY_DELAY': int(os.getenv('AKSHARE_RETRY_DELAY', '5')),
            
            'ENABLE_TUSHARE': os.getenv('ENABLE_TUSHARE', 'true').lower() == 'true',
            'ENABLE_AKSHARE': os.getenv('ENABLE_AKSHARE', 'true').lower() == 'true',
            'ENABLE_SINA': os.getenv('ENABLE_SINA', 'false').lower() == 'true',
            
            # 日志配置
            'LOG_DIR': os.getenv('LOG_DIR', 'logs'),
            'LOG_FILE_MAX_SIZE': os.getenv('LOG_FILE_MAX_SIZE', '100MB'),
            'LOG_FILE_BACKUP_COUNT': int(os.getenv('LOG_FILE_BACKUP_COUNT', '5')),
            'LOG_FORMAT': os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            
            # 安全配置
            'PASSWORD_SALT_ROUNDS': int(os.getenv('PASSWORD_SALT_ROUNDS', '12')),
            'SESSION_SECRET_KEY': os.getenv('SESSION_SECRET_KEY', 'your-session-secret-key'),
            'SESSION_EXPIRE_HOURS': int(os.getenv('SESSION_EXPIRE_HOURS', '24')),
            
            # 文件上传配置
            'UPLOAD_MAX_SIZE': os.getenv('UPLOAD_MAX_SIZE', '10MB'),
            'UPLOAD_ALLOWED_EXTENSIONS': os.getenv('UPLOAD_ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx'),
            
            # 性能配置
            'CACHE_ENABLED': os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            'CACHE_TTL': int(os.getenv('CACHE_TTL', '3600')),
            'CACHE_MAX_SIZE': int(os.getenv('CACHE_MAX_SIZE', '1000')),
            
            'DB_CONNECTION_POOL_SIZE': int(os.getenv('DB_CONNECTION_POOL_SIZE', '10')),
            'DB_CONNECTION_POOL_TIMEOUT': int(os.getenv('DB_CONNECTION_POOL_TIMEOUT', '30')),
            'DB_CONNECTION_POOL_RECYCLE': int(os.getenv('DB_CONNECTION_POOL_RECYCLE', '3600')),
            
            # 监控配置
            'HEALTH_CHECK_ENABLED': os.getenv('HEALTH_CHECK_ENABLED', 'true').lower() == 'true',
            'HEALTH_CHECK_INTERVAL': int(os.getenv('HEALTH_CHECK_INTERVAL', '60')),
            'METRICS_ENABLED': os.getenv('METRICS_ENABLED', 'false').lower() == 'true',
            'METRICS_PORT': int(os.getenv('METRICS_PORT', '9090')),
        }
        
        logger.info(f"✅ 已加载 {len(self.config)} 个配置项")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        db_type = self.get('DB_TYPE', 'postgresql')
        
        if db_type == 'postgresql':
            return f"postgresql+psycopg2://{self.get('DB_USER')}:{self.get('DB_PASSWORD')}@{self.get('DB_HOST')}:{self.get('DB_PORT')}/{self.get('DB_NAME')}"
        elif db_type == 'sqlite':
            return f"sqlite:///{self.get('SQLITE_DB_PATH')}"
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")
    
    def get_cors_origins(self) -> list:
        """获取CORS允许的源"""
        origins = self.get('CORS_ALLOW_ORIGINS', 'http://localhost:8000,http://localhost:8001')
        return [origin.strip() for origin in origins.split(',')]
    
    def get_cors_methods(self) -> list:
        """获取CORS允许的方法"""
        methods = self.get('CORS_ALLOW_METHODS', 'GET,POST,PUT,DELETE,OPTIONS')
        return [method.strip() for method in methods.split(',')]
    
    def get_cors_headers(self) -> list:
        """获取CORS允许的头部"""
        headers = self.get('CORS_ALLOW_HEADERS', '*')
        return [header.strip() for header in headers.split(',')] if headers != '*' else ['*']
    
    def get_upload_extensions(self) -> list:
        """获取允许上传的文件扩展名"""
        extensions = self.get('UPLOAD_ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx')
        return [ext.strip() for ext in extensions.split(',')]
    
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.get('ENVIRONMENT', 'development') == 'production'
    
    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.get('ENVIRONMENT', 'development') == 'development'
    
    def is_testing(self) -> bool:
        """判断是否为测试环境"""
        return self.get('ENVIRONMENT', 'development') == 'testing'
    
    def print_config(self):
        """打印当前配置"""
        logger.info("📋 当前配置:")
        for key, value in self.config.items():
            # 隐藏敏感信息
            if 'password' in key.lower() or 'secret' in key.lower() or 'token' in key.lower():
                value = '*' * len(str(value)) if value else None
            logger.info(f"  {key}: {value}")
    
    def validate_config(self) -> bool:
        """验证配置"""
        logger.info("🔍 验证配置...")
        
        errors = []
        
        # 检查必要的配置
        required_configs = [
            'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
            'JWT_SECRET_KEY', 'API_PORT', 'FRONTEND_PORT', 'ADMIN_PORT'
        ]
        
        for config in required_configs:
            if not self.get(config):
                errors.append(f"缺少必要配置: {config}")
        
        # 检查端口配置
        ports = [self.get('API_PORT'), self.get('FRONTEND_PORT'), self.get('ADMIN_PORT')]
        if len(set(ports)) != len(ports):
            errors.append("端口配置冲突")
        
        # 检查数据库配置
        if self.get('DB_TYPE') == 'postgresql':
            if not all([self.get('DB_HOST'), self.get('DB_PORT'), self.get('DB_NAME')]):
                errors.append("PostgreSQL配置不完整")
        
        if errors:
            logger.error("❌ 配置验证失败:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("✅ 配置验证通过")
        return True
    
    def create_env_file(self, template_file: str = "env_example.txt"):
        """从模板创建.env文件"""
        template_path = self.project_root / template_file
        
        if not template_path.exists():
            logger.error(f"❌ 模板文件不存在: {template_path}")
            return False
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ 已创建.env文件: {self.env_file}")
            return True
        except Exception as e:
            logger.error(f"❌ 创建.env文件失败: {e}")
            return False

def main():
    """主函数"""
    logger.info("🚀 启动配置管理器...")
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 打印配置
    config_manager.print_config()
    
    # 验证配置
    if not config_manager.validate_config():
        logger.error("❌ 配置验证失败，请检查环境变量")
        return
    
    # 测试数据库URL
    try:
        db_url = config_manager.get_database_url()
        logger.info(f"🔗 数据库URL: {db_url}")
    except Exception as e:
        logger.error(f"❌ 数据库URL生成失败: {e}")
    
    # 测试CORS配置
    cors_origins = config_manager.get_cors_origins()
    logger.info(f"🌐 CORS允许的源: {cors_origins}")
    
    logger.info("✅ 配置管理器启动完成")

if __name__ == "__main__":
    main() 