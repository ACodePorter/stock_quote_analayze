#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 backend_api 配置以使用环境变量
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config_manager import ConfigManager

def update_backend_api_config():
    """更新backend_api配置"""
    print("🔧 更新backend_api配置...")
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 读取原始配置文件
    config_file = project_root / "backend_api" / "config.py"
    
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    # 读取原始内容
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建新的配置内容
    new_content = '''"""
backend_api配置文件
使用环境变量管理配置
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_CONFIG = {
    "url": os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres:qidianspacetime@192.168.31.237:5446/stock_analysis'),
    "pool_size": int(os.getenv('DB_POOL_SIZE', '5')),
    "max_overflow": int(os.getenv('DB_MAX_OVERFLOW', '10')),
    "echo": os.getenv('DEBUG', 'false').lower() == 'true'
}

# JWT配置
JWT_CONFIG = {
    "secret_key": os.getenv('JWT_SECRET_KEY', 'your-secret-key-here'),
    "algorithm": os.getenv('JWT_ALGORITHM', 'HS256'),
    "access_token_expire_minutes": int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '1440'))
}

# API配置
API_CONFIG = {
    "title": "股票分析系统API",
    "description": "股票分析系统的后端API服务",
    "version": "1.0.0",
    "host": os.getenv('API_HOST', '0.0.0.0'),
    "port": int(os.getenv('API_PORT', '5000')),
    "workers": int(os.getenv('API_WORKERS', '4')),
    "reload": os.getenv('API_RELOAD', 'true').lower() == 'true'
}

# CORS配置
CORS_CONFIG = {
    "allow_origins": [origin.strip() for origin in os.getenv('CORS_ALLOW_ORIGINS', 'http://localhost:8000,http://localhost:8001').split(',')],
    "allow_credentials": os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true',
    "allow_methods": [method.strip() for method in os.getenv('CORS_ALLOW_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(',')],
    "allow_headers": [header.strip() for header in os.getenv('CORS_ALLOW_HEADERS', '*').split(',')] if os.getenv('CORS_ALLOW_HEADERS', '*') != '*' else ['*']
}

# 安全配置
SECURITY_CONFIG = {
    "password_salt_rounds": int(os.getenv('PASSWORD_SALT_ROUNDS', '12')),
    "session_secret_key": os.getenv('SESSION_SECRET_KEY', 'your-session-secret-key'),
    "session_expire_hours": int(os.getenv('SESSION_EXPIRE_HOURS', '24'))
}

# 文件上传配置
UPLOAD_CONFIG = {
    "max_size": os.getenv('UPLOAD_MAX_SIZE', '10MB'),
    "allowed_extensions": [ext.strip() for ext in os.getenv('UPLOAD_ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx').split(',')]
}

# 日志配置
LOG_CONFIG = {
    "level": os.getenv('LOG_LEVEL', 'INFO'),
    "dir": os.getenv('LOG_DIR', 'logs'),
    "file_max_size": os.getenv('LOG_FILE_MAX_SIZE', '100MB'),
    "file_backup_count": int(os.getenv('LOG_FILE_BACKUP_COUNT', '5')),
    "format": os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
}

# 环境配置
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

# 打印配置信息（开发环境）
if DEBUG:
    print("数据库连接URL:", DATABASE_CONFIG["url"])
    print("API配置:", API_CONFIG)
    print("CORS配置:", CORS_CONFIG)
'''
    
    # 备份原文件
    backup_file = config_file.with_suffix('.py.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已备份原配置文件: {backup_file}")
    
    # 写入新配置
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 已更新配置文件: {config_file}")
    return True

def update_backend_core_config():
    """更新backend_core配置"""
    print("🔧 更新backend_core配置...")
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 读取原始配置文件
    config_file = project_root / "backend_core" / "config" / "config.py"
    
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    # 读取原始内容
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建新的配置内容
    new_content = '''#配置文件
#含各个模块的配置信息
#使用环境变量管理配置

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent

# 数据库目录 - 使用相对路径
DB_DIR = ROOT_DIR / 'database'
DB_DIR.mkdir(parents=True, exist_ok=True)

# Tushare配置
TUSHARE_CONFIG = {
    'token': os.getenv('TUSHARE_TOKEN', '9701deb356e76d8d9918d797aff060ce90bd1a24339866c02444014f'),
    'max_retries': int(os.getenv('TUSHARE_MAX_RETRIES', '3')),
    'timeout': int(os.getenv('TUSHARE_TIMEOUT', '30')),
    'retry_delay': int(os.getenv('TUSHARE_RETRY_DELAY', '5'))
}

# 数据采集器配置
DATA_COLLECTORS = {
    'tushare': {
        'max_retries': int(os.getenv('TUSHARE_MAX_RETRIES', '3')),
        'retry_delay': int(os.getenv('TUSHARE_RETRY_DELAY', '5')),
        'timeout': int(os.getenv('TUSHARE_TIMEOUT', '30')),
        'log_dir': str(ROOT_DIR / 'backend_core' / 'logs'),
        'db_file': str(DB_DIR / 'stock_analysis.db'),
        'max_connection_errors': 10,
        'token': TUSHARE_CONFIG['token']
    },
    'akshare': {
        'max_retries': int(os.getenv('AKSHARE_MAX_RETRIES', '3')),
        'retry_delay': int(os.getenv('AKSHARE_RETRY_DELAY', '5')),
        'timeout': int(os.getenv('AKSHARE_TIMEOUT', '30')),
        'log_dir': str(ROOT_DIR / 'backend_core' / 'logs'),
        'db_file': str(DB_DIR / 'stock_analysis.db'),
        'max_connection_errors': 10,
    }
}

# 数据采集开关
ENABLE_TUSHARE = os.getenv('ENABLE_TUSHARE', 'true').lower() == 'true'
ENABLE_AKSHARE = os.getenv('ENABLE_AKSHARE', 'true').lower() == 'true'
ENABLE_SINA = os.getenv('ENABLE_SINA', 'false').lower() == 'true'

# 环境配置
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

# 创建必要的目录
for dir_path in [
    ROOT_DIR / 'backend_core' / 'logs',
    ROOT_DIR / 'backend_core' / 'data',
    ROOT_DIR / 'backend_core' / 'models'
]:
    dir_path.mkdir(parents=True, exist_ok=True)
'''
    
    # 备份原文件
    backup_file = config_file.with_suffix('.py.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已备份原配置文件: {backup_file}")
    
    # 写入新配置
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 已更新配置文件: {config_file}")
    return True

def update_admin_config():
    """更新admin配置"""
    print("🔧 更新admin配置...")
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 读取原始配置文件
    config_file = project_root / "admin" / "config.js"
    
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    # 读取原始内容
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建新的配置内容
    new_content = '''// 管理后台独立配置文件
// 完全独立于frontend目录的配置
// 使用环境变量管理配置

// 从环境变量获取配置（通过后端API传递）
const getEnvConfig = () => {
    // 默认配置
    const defaultConfig = {
        API_BASE_URL: 'http://localhost:5000/api/admin',
        API_TIMEOUT: 30000,
        API_RETRY_TIMES: 3,
        ADMIN_BASE_URL: 'http://localhost:8001',
        PAGINATION_DEFAULT_PAGE_SIZE: 20,
        REFRESH_AUTO_REFRESH_INTERVAL: 30000,
        UPLOAD_MAX_FILE_SIZE: 10 * 1024 * 1024,
        THEME_PRIMARY_COLOR: '#1890ff'
    };
    
    // 尝试从后端获取环境变量配置
    try {
        const envConfig = window.ENV_CONFIG || {};
        return { ...defaultConfig, ...envConfig };
    } catch (error) {
        console.warn('无法获取环境变量配置，使用默认配置:', error);
        return defaultConfig;
    }
};

const envConfig = getEnvConfig();

const ADMIN_CONFIG = {
    // API配置
    API: {
        BASE_URL: envConfig.API_BASE_URL,
        TIMEOUT: envConfig.API_TIMEOUT,
        RETRY_TIMES: envConfig.API_RETRY_TIMES
    },
    
    // 认证配置
    AUTH: {
        TOKEN_KEY: 'admin_token',
        REFRESH_TOKEN_KEY: 'admin_refresh_token',
        LOGIN_URL: '/admin/',
        LOGOUT_URL: '/api/admin/auth/logout'
    },
    
    // 分页配置
    PAGINATION: {
        DEFAULT_PAGE_SIZE: envConfig.PAGINATION_DEFAULT_PAGE_SIZE,
        PAGE_SIZE_OPTIONS: [10, 20, 50, 100]
    },
    
    // 数据刷新配置
    REFRESH: {
        AUTO_REFRESH_INTERVAL: envConfig.REFRESH_AUTO_REFRESH_INTERVAL,
        MANUAL_REFRESH_ENABLED: true
    },
    
    // 文件上传配置
    UPLOAD: {
        MAX_FILE_SIZE: envConfig.UPLOAD_MAX_FILE_SIZE,
        ALLOWED_TYPES: ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx']
    },
    
    // 主题配置
    THEME: {
        PRIMARY_COLOR: envConfig.THEME_PRIMARY_COLOR,
        SUCCESS_COLOR: '#52c41a',
        WARNING_COLOR: '#faad14',
        ERROR_COLOR: '#f5222d',
        INFO_COLOR: '#1890ff'
    },
    
    // 功能开关
    FEATURES: {
        USER_MANAGEMENT: true,
        DATA_MANAGEMENT: true,
        SYSTEM_MONITORING: true,
        DATA_EXPORT: true,
        BULK_OPERATIONS: true
    },
    
    // 默认用户信息
    DEFAULT_USER: {
        USERNAME: 'admin',
        PASSWORD: '123456',
        ROLE: 'admin'
    },
    
    // 错误消息
    MESSAGES: {
        LOGIN_SUCCESS: '登录成功',
        LOGIN_FAILED: '登录失败，请检查用户名和密码',
        LOGOUT_SUCCESS: '已退出登录',
        SAVE_SUCCESS: '保存成功',
        DELETE_SUCCESS: '删除成功',
        OPERATION_FAILED: '操作失败',
        NETWORK_ERROR: '网络错误，请稍后重试',
        UNAUTHORIZED: '未授权访问',
        FORBIDDEN: '访问被拒绝',
        NOT_FOUND: '资源不存在',
        SERVER_ERROR: '服务器内部错误'
    },
    
    // 日期格式
    DATE_FORMATS: {
        DISPLAY: 'YYYY-MM-DD HH:mm:ss',
        DATE_ONLY: 'YYYY-MM-DD',
        TIME_ONLY: 'HH:mm:ss'
    },
    
    // 数据格式化
    FORMAT: {
        CURRENCY: {
            SYMBOL: '¥',
            DECIMALS: 2
        },
        PERCENTAGE: {
            DECIMALS: 2,
            SUFFIX: '%'
        },
        NUMBER: {
            THOUSANDS_SEPARATOR: ',',
            DECIMALS: 2
        }
    }
};

// 导出配置
window.ADMIN_CONFIG = ADMIN_CONFIG;

// 工具函数
const AdminUtils = {
    // 获取API完整URL
    getApiUrl: (endpoint) => {
        return `${ADMIN_CONFIG.API.BASE_URL}${endpoint}`;
    },
    
    // 获取认证头
    getAuthHeaders: () => {
        const token = localStorage.getItem(ADMIN_CONFIG.AUTH.TOKEN_KEY);
        return {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        };
    },
    
    // 格式化货币
    formatCurrency: (amount) => {
        const { SYMBOL, DECIMALS } = ADMIN_CONFIG.FORMAT.CURRENCY;
        return `${SYMBOL}${parseFloat(amount).toFixed(DECIMALS)}`;
    },
    
    // 格式化百分比
    formatPercentage: (value) => {
        const { DECIMALS, SUFFIX } = ADMIN_CONFIG.FORMAT.PERCENTAGE;
        return `${parseFloat(value).toFixed(DECIMALS)}${SUFFIX}`;
    },
    
    // 格式化数字
    formatNumber: (num) => {
        const { THOUSANDS_SEPARATOR, DECIMALS } = ADMIN_CONFIG.FORMAT.NUMBER;
        return parseFloat(num).toLocaleString('zh-CN', {
            minimumFractionDigits: DECIMALS,
            maximumFractionDigits: DECIMALS
        });
    },
    
    // 检查用户权限
    hasPermission: (permission) => {
        const userRole = localStorage.getItem('admin_user_role');
        return userRole === 'admin' || userRole === permission;
    },
    
    // 获取用户信息
    getUserInfo: () => {
        return {
            username: localStorage.getItem('admin_username'),
            role: localStorage.getItem('admin_user_role'),
            token: localStorage.getItem(ADMIN_CONFIG.AUTH.TOKEN_KEY)
        };
    },
    
    // 清除用户信息
    clearUserInfo: () => {
        localStorage.removeItem(ADMIN_CONFIG.AUTH.TOKEN_KEY);
        localStorage.removeItem(ADMIN_CONFIG.AUTH.REFRESH_TOKEN_KEY);
        localStorage.removeItem('admin_username');
        localStorage.removeItem('admin_user_role');
    }
};

// 导出工具函数
window.AdminUtils = AdminUtils;
'''
    
    # 备份原文件
    backup_file = config_file.with_suffix('.js.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已备份原配置文件: {backup_file}")
    
    # 写入新配置
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 已更新配置文件: {config_file}")
    return True

def main():
    """主函数"""
    print("🚀 开始更新各模块配置...")
    
    # 更新backend_api配置
    if update_backend_api_config():
        print("✅ backend_api配置更新成功")
    else:
        print("❌ backend_api配置更新失败")
    
    # 更新backend_core配置
    if update_backend_core_config():
        print("✅ backend_core配置更新成功")
    else:
        print("❌ backend_core配置更新失败")
    
    # 更新admin配置
    if update_admin_config():
        print("✅ admin配置更新成功")
    else:
        print("❌ admin配置更新失败")
    
    print("""
🎉 配置更新完成！

📋 下一步操作:
1. 复制 env_example.txt 为 .env 文件
2. 修改 .env 文件中的配置项
3. 运行 python config_manager.py 验证配置
4. 重启各服务以应用新配置

🔧 注意事项:
- 所有敏感信息现在通过环境变量管理
- 开发和生产环境可以使用不同的.env文件
- 配置文件已备份，可以随时回滚
    """)

if __name__ == "__main__":
    main() 