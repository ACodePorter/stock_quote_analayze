# 🚀 股票分析软件启动指南

## 📋 系统要求

- **Python 3.8+** (推荐3.9或更高版本)
- **现代浏览器** (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- **网络连接** (用于获取实时股票数据)
- **Windows/Linux/macOS** (跨平台支持)

## ⚡ 快速启动 (推荐)

### 方法一：一键启动脚本

```bash
# 1. 启动后端服务 (在新的终端窗口)
python start_backend_api.py

# 2. 启动前端服务 (在另一个终端窗口)
python start_frontend.py
```

启动成功后：
- 后端API: `http://localhost:5000`
- 前端应用: `http://localhost:8000` (自动寻找可用端口)
- 会自动打开浏览器到登录页面

### 方法二：分步启动

#### 第一步：安装依赖

```bash
# 安装后端依赖
pip install -r requirements.txt

# 或安装开发环境依赖
pip install -r requirements-dev.txt
```

#### 第二步：启动后端服务

```bash
# 使用启动脚本 (推荐)
python start_backend_api.py

# 或直接启动
cd backend_api
python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

#### 第三步：启动前端服务

```bash
# 使用启动脚本 (推荐)
python start_frontend.py

# 或使用Python内置服务器
cd frontend
python -m http.server 8000
```

#### 第四步：访问应用

打开浏览器，访问: `http://localhost:8000/login.html`

## 🎯 功能演示

### 1. 用户注册/登录
- 访问登录页面
- 注册新账户或使用测试账户
- 登录成功后进入主界面

### 2. 浏览股票行情
- 查看市场指数 (上证、深证、创业板等)
- 浏览股票列表和涨跌幅排行
- 查看实时行情数据

### 3. 管理自选股
- 搜索并添加股票到自选股
- 创建自选股分组
- 查看自选股列表和历史数据

### 4. 查看个股详情
- 点击任意股票进入详情页
- 查看K线图和技术指标 (MA、EMA、布林带)
- 查看基本面信息和智能分析

### 5. 智能分析
- 查看系统推荐和买卖建议
- 获取阻力位/支撑位分析
- 查看预测分析和技术指标

### 6. 财经资讯
- 浏览最新财经新闻
- 查看研报和公告
- 下载PDF研报 (支持防盗链处理)

### 7. 历史数据
- 查看股票历史行情
- 导出历史数据 (支持Excel格式)
- 计算5天、10天、60天涨跌幅

### 8. 管理后台
- 访问 `http://localhost:8001` 进入管理后台
- 用户管理、数据统计、系统监控

## 🛠️ 故障排除

### 问题1：后端启动失败

**错误信息**: `ModuleNotFoundError: No module named 'fastapi'`

**解决方案**:
```bash
pip install -r requirements.txt
```

**错误信息**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # macOS/Linux

# 或更改端口
python start_backend_api.py --port 5001
```

**错误信息**: `ImportError: attempted relative import with no known parent package`

**解决方案**:
```bash
# 使用启动脚本而不是直接运行main.py
python start_backend_api.py
```

### 问题2：前端无法连接后端

**现象**: 页面显示但数据加载失败

**解决方案**:
1. 确认后端服务已启动
2. 检查浏览器控制台错误
3. 验证API地址配置：
   ```javascript
   // 在 frontend/js/config.js 中检查
   // 开发环境: http://localhost:5000
   // 生产环境: 相对路径
   ```

### 问题3：跨域错误 (CORS)

**错误信息**: `Access to fetch at 'http://localhost:5000' from origin 'http://localhost:8000' has been blocked by CORS policy`

**解决方案**: 后端已配置CORS，如仍有问题，检查FastAPI-CORS配置：
```bash
pip install fastapi[all]
```

### 问题4：数据库错误

**错误信息**: `no such table: users`

**解决方案**: 数据库会自动初始化，如仍有问题：
```bash
# 删除数据库文件重新初始化
rm database/stock_analysis.db
python start_backend_api.py
```

### 问题5：研报下载失败

**错误信息**: `访问受限 - 您的请求已被该站点的安全策略拦截`

**解决方案**: 系统已实现PDF重定向功能，自动绕过防盗链限制。

### 问题6：登录失效处理

**现象**: 操作时提示"登录已过期"

**解决方案**: 系统会自动跳转到登录页面，重新登录即可。

## 📱 浏览器兼容性

### 推荐浏览器
- **Chrome 90+** ✅ 完全支持
- **Firefox 88+** ✅ 完全支持  
- **Safari 14+** ✅ 完全支持
- **Edge 90+** ✅ 完全支持

### 不支持的浏览器
- Internet Explorer (所有版本) ❌
- Chrome < 70 ❌
- Firefox < 65 ❌

## 🔧 高级配置

### 修改端口配置

**后端端口** (默认5000):
```python
# 在 start_backend_api.py 中修改
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=5001,  # 修改端口
    reload=True
)
```

**前端端口** (默认8000):
```python
# 在 start_frontend.py 中修改
port = find_available_port(8001)  # 修改起始端口
```

**更新API地址**:
```javascript
// 在 frontend/js/config.js 中修改
case 'development':
    return 'http://localhost:5000';  // 修改为对应端口
```

### 环境配置

**开发环境**:
- 后端: `http://localhost:5000`
- 前端: `http://localhost:8000`
- 数据库: PostgreSQL 

**生产环境**:
- 后端: 相对路径API
- 前端: 静态文件服务
- 数据库: PostgreSQL 

### 数据库配置

**查看数据库内容**:
```bash
cd database
sqlite3 stock_analysis.db
.tables
SELECT * FROM users;
.quit
```

**重置数据库**:
```bash
rm database/stock_analysis.db
python start_backend_api.py  # 会自动重新创建
```

## 📊 数据源

系统使用以下数据源：
- **Akshare**: 实时股票数据、历史数据、新闻公告
- **东方财富**: 研报数据、资金流向
- **本地数据库**: 用户数据、自选股、交易记录

## 🚀 性能优化

### 前端优化
- 启用浏览器缓存
- 图片懒加载
- 异步数据加载
- 响应式设计

### 后端优化
- 数据库索引优化
- API缓存机制
- 异步处理
- 错误重试机制

## 📞 技术支持

### 常见问题
1. **数据更新频率？** - 实时数据每30秒刷新一次
2. **支持实时数据吗？** - 支持，使用Akshare实时API
3. **能否部署到服务器？** - 支持，参考部署文档
4. **研报下载问题？** - 已实现防盗链处理，自动重定向

### 获得帮助
- 查看项目README.md
- 检查浏览器开发者工具
- 查看终端错误信息
- 查看日志文件: `app.log`, `auth.log`

## 🎉 开始使用

1. **启动服务** - 按照上述步骤启动前后端服务
2. **注册账户** - 在登录页面注册新用户
3. **探索功能** - 从首页开始探索各个功能模块
4. **添加自选股** - 搜索并添加感兴趣的股票
5. **查看分析** - 体验智能分析和预测功能
6. **下载研报** - 查看和下载最新研报

## 🔍 项目结构

```
stock_quote_analayze/
├── backend_api/          # 后端API服务
│   ├── main.py          # FastAPI主应用
│   ├── auth_routes.py   # 认证路由
│   ├── stock/           # 股票相关API
│   └── admin/           # 管理后台API
├── frontend/            # 前端应用
│   ├── login.html       # 登录页面
│   ├── index.html       # 首页
│   ├── stock.html       # 股票详情页
│   └── js/              # JavaScript文件
├── database/            # 数据库文件
├── start_backend_api.py # 后端启动脚本
├── start_frontend.py    # 前端启动脚本
└── requirements.txt     # 依赖包列表
```

---

🎯 **提示**: 第一次启动可能需要几秒钟初始化数据库，请耐心等待。

✨ **体验建议**: 建议使用Chrome或Firefox浏览器获得最佳体验。

🔧 **开发提示**: 使用 `python start_backend_api.py` 和 `python start_frontend.py` 启动服务，支持热重载。