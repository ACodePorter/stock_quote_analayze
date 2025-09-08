# 前端按钮功能权限认证使用指南

## 概述

前端页面级功能已实现权限认证，但页面内的按钮触发功能需要单独添加授权认证。本文档说明如何为按钮功能添加权限认证。

## 已实现的认证功能

### 1. 页面级认证
- 页面加载时自动检查登录状态
- 未登录用户自动跳转到登录页
- Token失效后自动清除本地存储并跳转登录页

### 2. 全局认证工具
- `authFetch()`: 带token的fetch请求，自动处理401错误
- `CommonUtils.auth.checkLogin()`: 检查登录状态
- `CommonUtils.auth.getUserInfo()`: 获取用户信息
- `CommonUtils.auth.logout()`: 登出功能

## 按钮功能认证实现

### 方法1: 手动检查认证（推荐用于复杂逻辑）

```javascript
async function exportHistory() {
    // 检查用户登录状态
    const userInfo = CommonUtils.auth.getUserInfo();
    if (!userInfo || !userInfo.id) {
        CommonUtils.showToast('请先登录后再导出数据', 'warning');
        return;
    }
    
    // 执行具体功能
    try {
        const response = await authFetch(url);
        if (!response.ok) {
            if (response.status === 401) {
                CommonUtils.showToast('登录已过期，请重新登录', 'error');
                CommonUtils.auth.logout();
                return;
            }
            throw new Error(`操作失败: ${response.status}`);
        }
        // 处理响应...
    } catch (error) {
        console.error('操作失败:', error);
        alert('操作失败: ' + error.message);
    }
}
```

### 方法2: 使用认证装饰器（推荐用于简单功能）

```javascript
// 同步函数认证
const protectedFunction = CommonUtils.requireAuth(function() {
    // 需要认证的功能代码
    console.log('用户已认证，执行功能');
});

// 异步函数认证
const protectedAsyncFunction = CommonUtils.requireAuthAsync(async function() {
    // 需要认证的异步功能代码
    const response = await authFetch(url);
    return response.json();
});
```

## 已添加认证的功能

### 历史行情页面
- ✅ 导出历史数据 (`exportHistory`)
- ✅ 计算5天涨跌幅 (`calculateFiveDayChange`)
- ✅ 计算10天涨跌幅 (`calculateTenDayChange`)
- ✅ 计算60天涨跌幅 (`calculateSixtyDayChange`)

### 行情中心页面
- ✅ 添加到自选股 (`addToWatchlist`)
- ✅ 从自选股删除 (`removeFromWatchlist`)

### 股票详情页面
- ✅ 添加到自选股 (`addToWatchlist`)
- ✅ 从自选股删除 (`removeFromWatchlist`)

## Token失效处理

`authFetch` 函数已自动处理token失效：

```javascript
async function authFetch(url, options = {}) {
    const token = localStorage.getItem('access_token');
    options.headers = options.headers || {};
    if (token) {
        options.headers['Authorization'] = 'Bearer ' + token;
    }
    
    const response = await fetch(url, options);
    
    // 检查401错误，自动处理token失效
    if (response.status === 401) {
        console.log('Token已失效，清除本地存储并跳转到登录页');
        localStorage.removeItem('access_token');
        localStorage.removeItem('userInfo');
        localStorage.removeItem('token');
        
        // 如果不在登录页面，跳转到登录页
        if (!window.location.pathname.includes('login.html') && 
            !window.location.pathname.includes('test-login.html')) {
            CommonUtils.showToast('登录已过期，请重新登录', 'error');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1000);
        }
    }
    
    return response;
}
```

## 最佳实践

1. **使用 `authFetch` 替代 `fetch`**: 所有需要认证的API请求都应使用 `authFetch`
2. **检查用户信息**: 在执行需要认证的功能前，先检查 `CommonUtils.auth.getUserInfo()`
3. **友好的错误提示**: 使用 `CommonUtils.showToast()` 显示用户友好的错误信息
4. **自动处理401**: 依赖 `authFetch` 的自动401处理，无需手动处理token失效

## 注意事项

- 所有需要认证的按钮功能都应该添加认证检查
- 使用 `authFetch` 而不是普通的 `fetch` 来发送请求
- 在认证失败时提供清晰的用户提示
- 避免在认证失败时执行敏感操作
