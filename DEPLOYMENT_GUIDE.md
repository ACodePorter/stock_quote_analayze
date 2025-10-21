# 股票分析系统部署指南

## 快速部署

### 1. 环境要求
- Python 3.8+
- PostgreSQL 12+
- 操作系统: Windows/Linux/macOS
- 内存: 4GB+
- 磁盘空间: 2GB+

### 2. 数据库配置
系统使用PostgreSQL数据库，请确保：
- PostgreSQL服务已启动
- 数据库连接参数正确（见deploy_config.json）
- 用户具有创建数据库和表的权限

### 3. 一键部署
```bash
# 运行部署脚本
python deploy.py

# 启动系统
python start_system.py
```

### 4. 手动部署
```bash
# 安装依赖
pip install -r requirements.txt
pip install -r backend_core/requirements.txt
pip install -r backend_api/requirements.txt

# 初始化PostgreSQL数据库
python init_postgresql_db.py

# 运行数据库迁移
python migrate_db.py

# 启动服务
python start_system.py
```

## Docker部署

### 1. 构建镜像
```bash
docker build -t stock-analyzer .
```

### 2. 运行容器
```bash
docker run -d -p 5000:5000 -p 8000:8000 -p 8001:8001 stock-analyzer
```

### 3. 使用Docker Compose
```bash
docker-compose up -d
```

## 访问地址

- 登录页面: http://localhost:8000/login.html
- 首页: http://localhost:8000/index.html
- 后端API: http://localhost:5000
- 管理后台: http://localhost:8001/

## 配置说明

编辑 `deploy_config.json` 文件来修改配置:

```json
{
  "python_version": "3.8",
  "ports": {
    "backend": 5000,
    "frontend": 8000,
    "admin": 8001
  },
  "database": {
    "type": "sqlite",
    "path": "database/stock_analysis.db"
  },
  "services": {
    "backend": true,
    "frontend": true,
    "admin": true,
    "data_collector": true
  }
}
```

## 故障排除

### 1. 端口冲突
修改 `deploy_config.json` 中的端口配置

### 2. 依赖安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 清理缓存
pip cache purge

# 重新安装
pip install -r requirements.txt
```

### 3. 数据库问题
```bash
# 检查数据库连接
python test_db_connection.py

# 重新初始化数据库
python migrate_db.py
```

### 4. 权限问题
```bash
# Linux/macOS设置执行权限
chmod +x start.sh start_backend.sh start_frontend.sh
```

## 生产环境部署

### 1. 使用Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend_api.main:app
```

### 2. 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 使用Supervisor管理进程
```ini
[program:stock-analyzer]
command=python /path/to/stock_analyzer/start_system.py
directory=/path/to/stock_analyzer
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/stock-analyzer.log
```

## 监控和维护

### 1. 日志查看
```bash
tail -f deploy.log
tail -f logs/app.log
```

### 2. 性能监控
- 使用 `htop` 监控系统资源
- 使用 `netstat -tulpn` 检查端口占用
- 使用 `df -h` 检查磁盘空间

### 3. 备份
```bash
# 备份数据库
cp database/stock_analysis.db backup/stock_analysis_$(date +%Y%m%d).db

# 备份配置文件
cp deploy_config.json backup/
```

## 技术支持

如遇问题请检查:
1. Python版本是否符合要求
2. 依赖包是否正确安装
3. 端口是否被占用
4. 数据库文件权限
5. 网络连接是否正常

更多信息请查看项目README.md文件。
