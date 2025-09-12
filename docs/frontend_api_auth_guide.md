# 前端API调用登录失效处理指南

## 概述

前端JavaScript在触发后台服务调用时，需要判断是否登录失效。本文档说明如何正确使用API调用函数来处理登录失效。

## API调用函数

### 1. authFetch - 带认证的API调用

```javascript
// 自动添加Authorization头，处理401错误
const response = await authFetch(`${API_BASE_URL}/api/watchlist`);
```

**特点**：
- 自动添加 `Authorization: Bearer ${token}` 头
- 自动检测401错误并处理登录失效
- 自动清除本地存储并跳转登录页

### 2. smartFetch - 智能API调用

```javascript
// 根据URL自动判断是否需要认证
const response = await smartFetch(`${API_BASE_URL}/api/market/indices`);
```

**特点**：
- 自动判断API端点是否需要认证
- 需要认证的端点使用 `authFetch`
- 公开端点使用普通 `fetch`

### 3. 需要认证的API端点

以下API端点会自动使用认证：

```javascript
const authRequiredEndpoints = [
    '/api/watchlist',      // 自选股相关
    '/api/auth/',          // 认证相关
    '/api/analysis/',      // 分析相关
    '/api/stock/history',  // 历史行情
    '/api/trading_notes',  // 交易备注
    '/api/user/',          // 用户相关
    '/api/admin/'          // 管理相关
];
```

## 登录失效处理流程

### 1. 自动检测401错误

```javascript
if (response.status === 401) {
    console.log('Token已失效，清除本地存储并跳转到登录页');
    localStorage.removeItem('access_token');
    localStorage.removeItem('userInfo');
    localStorage.removeItem('token');
    
    // 跳转到登录页
    if (!window.location.pathname.includes('login.html')) {
        CommonUtils.showToast('登录已过期，请重新登录', 'error');
        window.location.href = 'login.html';
    }
}
```

### 2. 用户友好的错误提示

- 显示Toast提示："登录已过期，请重新登录"
- 自动跳转到登录页面
- 清除所有本地存储的认证信息

## 已更新的API调用

### 股票详情页面
- ✅ 股票分析API (`/api/analysis/stock/`)
- ✅ 实时行情API (`/api/stock/realtime_quote_by_code`)
- ✅ 财务数据API (`/api/stock/latest_financial`)

### 历史行情页面
- ✅ 历史行情API (`/api/stock/history`)
- ✅ 计算涨跌幅API (`/api/stock/history/calculate_*_day_change`)
- ✅ 交易备注API (`/api/trading_notes/*`)

### 自选股页面
- ✅ 自选股管理API (`/api/watchlist/*`)
- ✅ 分组管理API (`/api/watchlist/groups/*`)

## 使用建议

### 1. 优先使用 authFetch

```javascript
// 推荐：需要认证的API
const response = await authFetch(`${API_BASE_URL}/api/watchlist`);

// 不推荐：普通fetch（需要手动处理401）
const response = await fetch(`${API_BASE_URL}/api/watchlist`);
```

### 2. 公开API使用 smartFetch

```javascript
// 推荐：智能判断是否需要认证
const response = await smartFetch(`${API_BASE_URL}/api/market/indices`);

// 也可以：直接使用fetch（公开API）
const response = await fetch(`${API_BASE_URL}/api/market/indices`);
```

### 3. 错误处理

```javascript
try {
    const response = await authFetch(url);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    // 处理数据...
} catch (error) {
    console.error('API调用失败:', error);
    // 错误处理...
}
```

## 测试方法

### 测试登录失效处理

```javascript
// 在浏览器控制台中运行
CommonUtils.testApiLoginExpiry();
```

### 模拟登录失效

```javascript
// 清除认证信息
localStorage.removeItem('access_token');
localStorage.removeItem('userInfo');
localStorage.removeItem('token');

// 然后调用需要认证的API
const response = await authFetch(`${API_BASE_URL}/api/watchlist`);
```

## 注意事项

1. **不要混用**：避免在同一项目中混用 `fetch` 和 `authFetch`
2. **错误处理**：始终检查 `response.ok` 状态
3. **用户体验**：登录失效时提供清晰的提示信息
4. **安全性**：确保敏感API都使用认证调用

## 最佳实践

1. **统一使用**：所有需要认证的API都使用 `authFetch`
2. **智能判断**：不确定是否需要认证时使用 `smartFetch`
3. **错误处理**：完善的try-catch错误处理
4. **用户提示**：登录失效时提供友好的用户提示
