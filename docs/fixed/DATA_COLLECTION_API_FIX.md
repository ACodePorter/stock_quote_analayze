# 数据采集API 404错误修复说明

## 🚨 问题描述

远程生产环境中，用户管理功能API能正常调用，但数据采集页面API返回404错误：

```
GET https://www.icemaplecity.com/api/data-collection/tasks 404 (Not Found)
GET https://www.icemaplecity.com/api/data-collection/current-task 404 (Not Found)
```

## 🔍 问题分析

### 根本原因
通过分析所有API路由，发现了**API路由前缀不一致**的问题：

1. **用户管理API**：
   - 前端调用：`/api/users`
   - 后端路由：`/api/users` (user_manage.py)
   - 完整路径：`https://www.icemaplecity.com/api/users` ✅ 正常

2. **数据采集API**（修复前）：
   - 前端调用：`/data-collection/...` (缺少 `/api` 前缀)
   - 后端路由：`/api/data-collection/...`
   - 完整路径：`https://www.icemaplecity.com/data-collection/...` ❌ 404错误

**问题根源**：前端代码中的API调用路径缺少 `/api` 前缀，与后端路由不匹配。

## 🛠️ 彻底解决方案

### 统一API路由规范

**目标**：所有API路由统一为 `/api/*` 格式，确保前后端路径一致。

### 1. 修正前端API调用路径

**修改文件**：`admin/src/views/DataCollectView.vue`

**修改内容**：
```typescript
// 修复前
const response = await axios.post(`${API_BASE}/data-collection/historical`, requestData)
const response = await axios.get(`${API_BASE}/data-collection/tasks`)
const response = await axios.get(`${API_BASE}/data-collection/current-task`)
await axios.delete(`${API_BASE}/data-collection/tasks/${taskId}`)

// 修复后
const response = await axios.post(`${API_BASE}/api/data-collection/historical`, requestData)
const response = await axios.get(`${API_BASE}/api/data-collection/tasks`)
const response = await axios.get(`${API_BASE}/api/data-collection/current-task`)
await axios.delete(`${API_BASE}/api/data-collection/tasks/${taskId}`)
```

### 2. 确保后端路由前缀正确

**修改文件**：`backend_api/stock/data_collection_api.py`

**修改内容**：
```python
# 确保路由前缀正确
router = APIRouter(prefix="/api/data-collection", tags=["数据采集"])
```

### 3. 确保前端API配置正确

**修改文件**：`admin/src/config/api.ts`

**修改内容**：
```typescript
// 确保生产环境baseURL不包含 /api 前缀
production: {
  baseURL: 'https://www.icemaplecity.com',  // 不包含 /api
  timeout: 30000
}
```

## 📋 部署步骤

### 1. 重新构建前端
```bash
cd admin
npm run build
```

### 2. 上传dist目录
将 `admin/dist` 目录上传到远程服务器

### 3. 重启后端服务
确保后端服务使用新的路由配置

### 4. 验证修复
访问数据采集页面，检查浏览器控制台：
- ✅ 应该看到成功的API调用
- ✅ 不再出现404错误

## 🔧 技术细节

### API路由对比

| 功能模块 | 前端调用路径 | 后端路由前缀 | 完整URL | 状态 |
|---------|-------------|-------------|---------|------|
| 用户管理 | `/api/users` | `/api/users` | `/api/users` | ✅ 正常 |
| 数据采集(修复前) | `/data-collection` | `/api/data-collection` | `/data-collection` | ❌ 404 |
| 数据采集(修复后) | `/api/data-collection` | `/api/data-collection` | `/api/data-collection` | ✅ 正常 |

### 路径映射逻辑

**统一后的路径映射**：
- 前端基础URL：`https://www.icemaplecity.com`
- 后端路由前缀：`/api/*`
- 最终完整路径：`https://www.icemaplecity.com/api/*`

**示例**：
- 用户管理：`https://www.icemaplecity.com` + `/api/users` = `/api/users`
- 数据采集：`https://www.icemaplecity.com` + `/api/data-collection` = `/api/data-collection`

## ✅ 验证方法

### 1. 本地测试
```bash
# 启动后端服务
python backend_api/main.py

# 启动前端服务
cd admin && npm run dev

# 访问数据采集页面
http://localhost:8001/datacollect
```

### 2. 生产环境测试
```bash
# 访问生产环境
https://www.icemaplecity.com/admin

# 打开浏览器控制台，检查API调用
# 应该看到成功的请求，不再有404错误
```

## 📝 注意事项

1. **路由层级一致性**：所有API路由都遵循 `/api/*` 格式
2. **前端基础URL**：`https://www.icemaplecity.com` 不包含 `/api` 前缀
3. **后端路由前缀**：统一包含 `/api` 前缀
4. **缓存清理**：部署后可能需要清理浏览器缓存
5. **后端重启**：修改后端路由后需要重启服务

## 🎯 总结

通过统一API路由规范，解决了数据采集API的404错误问题：

- **后端路由**：统一为 `/api/*` 格式
- **前端配置**：基础URL不包含 `/api` 前缀
- **路径映射**：`前端基础URL + 后端路由前缀 = 完整API路径`

这样确保了所有API的命名和调用方式保持一致，避免了路由冲突和404错误。
