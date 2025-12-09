# 低九策略调试指南

## 问题现象
点击"刷新筛选"按钮后，显示"正在筛选股票，请稍候..."，但没有触发后台API调用。

## 调试步骤

### 1. 检查浏览器控制台
1. 打开浏览器开发者工具（F12）
2. 切换到 Console（控制台）标签
3. 刷新页面（Ctrl+Shift+R 清除缓存）
4. 点击"低九策略"标签
5. 点击"刷新筛选"按钮

### 2. 查看控制台日志
应该看到以下日志（按顺序）：

```
[低九策略] 找到 X 个刷新按钮
[低九策略] 绑定按钮: refreshBtn-low-nine, 策略: low-nine
[低九策略] 按钮被点击: low-nine
[低九策略] loadScreeningResults 被调用, strategy = low-nine
[低九策略] 最终使用的策略: low-nine
[低九策略] 使用的suffix: low-nine
[低九策略] API URL: http://xxx/api/screening/low-nine-strategy
[低九策略] 开始发送请求...
[低九策略] 收到响应, status: 200
[低九策略] 解析结果: {...}
```

### 3. 可能的问题和解决方案

#### 问题1: 没有看到任何日志
**原因**: JavaScript文件没有正确加载或被缓存
**解决**: 
- 强制刷新页面（Ctrl+Shift+R）
- 检查Network标签，确认screening.js已加载
- 检查screening.js文件路径是否正确

#### 问题2: 看到"找到 X 个刷新按钮"但X不包括低九策略
**原因**: 按钮还没有渲染到DOM中
**解决**: 
- 检查HTML中是否正确添加了低九策略的按钮
- 确认按钮有class="refresh-btn"和data-strategy="low-nine"

#### 问题3: 看到绑定日志，但点击后没有"按钮被点击"日志
**原因**: 事件监听器没有正确绑定
**解决**: 
- 检查是否有JavaScript错误
- 确认按钮元素存在且可点击

#### 问题4: 看到API URL但没有"开始发送请求"
**原因**: 代码在URL构造后出错
**解决**: 
- 检查控制台是否有错误信息
- 检查authFetch函数是否存在

#### 问题5: 请求发送但status不是200
**原因**: 后端API出错
**解决**: 
- 检查后端服务是否运行
- 检查API路由是否正确注册
- 查看后端日志

#### 问题6: 收到响应但解析失败
**原因**: 响应格式不正确
**解决**: 
- 查看响应内容
- 检查后端返回的数据格式

### 4. 检查后端服务

#### 检查后端是否运行
```powershell
# 检查进程
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# 或者访问API健康检查端点
curl http://localhost:5000/
```

#### 检查API端点
```powershell
# 直接测试API
curl http://localhost:5000/api/screening/low-nine-strategy
```

#### 查看后端日志
检查 `backend_api/app.log` 文件，查找相关错误信息。

### 5. 网络检查

打开开发者工具的Network标签：
1. 刷新页面
2. 点击"刷新筛选"
3. 查看是否有请求发送到 `/api/screening/low-nine-strategy`
4. 检查请求状态码和响应内容

### 6. 常见错误

#### CORS错误
```
Access to fetch at 'http://...' from origin 'http://...' has been blocked by CORS policy
```
**解决**: 检查后端CORS配置

#### 401 Unauthorized
```
status: 401
```
**解决**: 检查认证token是否有效

#### 500 Internal Server Error
```
status: 500
```
**解决**: 查看后端日志，检查数据库连接和策略代码

#### Network Error
```
Failed to fetch
```
**解决**: 
- 检查后端服务是否运行
- 检查API_BASE_URL配置是否正确
- 检查网络连接

## 快速修复建议

1. **清除浏览器缓存**: Ctrl+Shift+Delete
2. **重启后端服务**: 停止并重新启动FastAPI服务
3. **检查配置文件**: 确认 `frontend/js/config.js` 中的API_BASE_URL正确
4. **验证路由注册**: 确认 `backend_api/main.py` 中已包含stock_screening_router

## 联系信息
如果问题仍然存在，请提供：
1. 浏览器控制台的完整日志
2. Network标签的请求详情
3. 后端日志文件内容
