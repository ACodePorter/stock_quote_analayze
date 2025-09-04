# API路由规范标准

## 🎯 目标

统一所有API的命名和调用方式，确保前后端API路径一致，避免404错误。

## 📋 当前API路由分析

### 后端路由前缀现状

| 模块 | 文件路径 | 当前路由前缀 | 状态 |
|------|----------|-------------|------|
| 用户管理 | `user_manage.py` | `/api/users` | ✅ 正常 |
| 数据采集 | `data_collection_api.py` | `/api/data-collection` | ✅ 已修复 |
| 股票管理 | `stock_manage.py` | `/api/stock` | ✅ 正常 |
| 行情数据 | `quotes_routes.py` | `/api/quotes` | ✅ 正常 |
| 管理员用户 | `admin/users.py` | `/api/admin/users` | ✅ 正常 |
| 管理员行情 | `admin/quotes.py` | `/api/admin/quotes` | ✅ 正常 |
| 管理员仪表板 | `admin/dashboard.py` | `/api/admin/dashboard` | ✅ 正常 |
| 管理员日志 | `admin/logs.py` | `/api/admin/logs` | ✅ 正常 |
| 认证 | `auth_routes.py` | `/api/auth` | ✅ 正常 |
| 管理员认证 | `admin/auth.py` | `/api/admin/auth` | ✅ 正常 |
| 行情 | `market_routes.py` | `/api/market` | ✅ 正常 |
| 自选股 | `watchlist_manage.py` | `/api/watchlist` | ✅ 正常 |
| 交易笔记 | `trading_notes_routes.py` | `/api/trading_notes` | ✅ 正常 |
| 系统同步 | `app_complete.py` | `/api/sync` | ✅ 正常 |
| 股票历史 | `history_api.py` | `/api/stock/history` | ✅ 正常 |
| 资金流向 | `stock_fund_flow.py` | `/api/stock_fund_flow` | ✅ 正常 |
| 股票新闻 | `stock_news.py` | `/api/stock` | ⚠️ 需要区分 |
| 股票分析 | `stock_analysis_routes.py` | `/api/analysis` | ✅ 正常 |
| 操作日志 | `operation_logs.py` | `/api/admin/operation-logs` | ✅ 正常 |

## 🛠️ 统一规范

### 1. 路由前缀规范

**所有API路由必须遵循以下格式：**

```python
# ✅ 正确格式
router = APIRouter(prefix="/api/{module_name}", tags=["模块名称"])

# ❌ 错误格式
router = APIRouter(prefix="/{module_name}", tags=["模块名称"])  # 缺少 /api 前缀
router = APIRouter(prefix="/api/api/{module_name}", tags=["模块名称"])  # 重复 /api
```

### 2. 前端API配置规范

**前端基础URL配置：**

```typescript
// ✅ 正确配置
export const API_CONFIG = {
  development: {
    baseURL: 'http://localhost:5000',  // 开发环境
    timeout: 30000
  },
  production: {
    baseURL: 'https://www.icemaplecity.com',  // 生产环境，不包含 /api
    timeout: 30000
  }
}
```

**前端API调用方式：**

```typescript
// ✅ 正确调用
const response = await apiService.get('/api/users')  // 完整路径
const response = await apiService.get('/api/data-collection/tasks')  // 完整路径

// ❌ 错误调用
const response = await apiService.get('/users')  // 缺少 /api 前缀
```

### 3. 路径映射逻辑

**完整路径 = 前端基础URL + 后端路由前缀 + 具体端点**

| 组件 | 前端基础URL | 后端路由前缀 | 具体端点 | 完整URL |
|------|-------------|-------------|----------|---------|
| 用户管理 | `https://www.icemaplecity.com` | `/api/users` | `/list` | `https://www.icemaplecity.com/api/users/list` |
| 数据采集 | `https://www.icemaplecity.com` | `/api/data-collection` | `/tasks` | `https://www.icemaplecity.com/api/data-collection/tasks` |
| 管理员用户 | `https://www.icemaplecity.com` | `/api/admin/users` | `/list` | `https://www.icemaplecity.com/api/admin/users/list` |

## 🔧 需要修复的问题

### 1. 股票新闻API冲突

**问题**：`stock_news.py` 和 `stock_manage.py` 都使用 `/api/stock` 前缀

**解决方案**：修改股票新闻API前缀

```python
# 修改前
router = APIRouter(prefix="/api/stock", tags=["stock_news"])

# 修改后
router = APIRouter(prefix="/api/stock/news", tags=["stock_news"])
```

### 2. 前端API调用更新

需要更新前端调用股票新闻API的路径：

```typescript
// 修改前
const response = await apiService.get('/api/stock/news')

// 修改后
const response = await apiService.get('/api/stock/news')
```

## 📝 实施步骤

### 1. 修复股票新闻API冲突
```
