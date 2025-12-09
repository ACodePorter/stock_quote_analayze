# 长下影线策略参数化 - 错误排查指南

## 错误现象
前端显示 `[object Object]` 错误

## 已修复的问题

### 1. 前端错误处理 ✅
**文件**: `frontend/js/screening.js`

**问题**: 错误对象没有正确转换为字符串
**修复**: 
```javascript
// 修复前
errorMessage.textContent = `加载失败: ${error.message}`;

// 修复后
const errorMsg = error.message || error.toString() || '未知错误';
errorMessage.textContent = `加载失败: ${errorMsg}`;
```

## 排查步骤

### 步骤1: 检查后端服务是否运行
```powershell
# 检查端口5000是否被监听
netstat -ano | findstr :5000
```

### 步骤2: 测试API是否正常
```powershell
# 进入backend_api目录
cd e:\wangxw\股票分析软件\编码\stock_quote_analayze\backend_api

# 运行测试脚本
python test_long_shadow_params.py
```

### 步骤3: 检查浏览器控制台
1. 打开浏览器开发者工具（F12）
2. 切换到 Console 标签
3. 查看完整的错误信息
4. 切换到 Network 标签
5. 点击"刷新筛选"按钮
6. 查看API请求的详细信息

### 步骤4: 检查后端日志
```powershell
# 查看后端日志
Get-Content "e:\wangxw\股票分析软件\编码\stock_quote_analayze\backend_api\app.log" -Tail 50
```

## 可能的问题和解决方案

### 问题1: 后端服务未启动
**症状**: 连接被拒绝
**解决**: 
```powershell
cd e:\wangxw\股票分析软件\编码\stock_quote_analayze\backend_api
python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### 问题2: 参数类型错误
**症状**: 422 Unprocessable Entity
**检查**: 
- 参数是否在允许范围内
- 参数类型是否正确（数字vs字符串）

**前端参数读取**:
```javascript
const lowerShadowRatio = document.getElementById('lowerShadowRatio')?.value || 1.0;
```
注意：`input.value` 返回的是字符串，但URL参数会自动转换

### 问题3: 数据库连接问题
**症状**: 500 Internal Server Error
**检查**: 
- 数据库是否运行
- 数据库连接配置是否正确

### 问题4: 缺少历史数据
**症状**: 返回空结果
**检查**: 
- 数据库中是否有足够的历史数据
- 日期范围是否正确

### 问题5: 浏览器缓存
**症状**: 修改后的代码不生效
**解决**: 
- 强制刷新: Ctrl + Shift + R
- 清除缓存: Ctrl + Shift + Delete

## 调试技巧

### 1. 查看API请求URL
在浏览器控制台中，应该能看到类似这样的URL：
```
http://localhost:5000/api/screening/long-lower-shadow-strategy?lower_shadow_ratio=1.0&upper_shadow_ratio=0.3&min_amplitude=0.02&recent_days=2
```

### 2. 直接在浏览器中测试API
将上面的URL直接粘贴到浏览器地址栏，查看返回结果

### 3. 使用curl测试
```powershell
curl "http://localhost:5000/api/screening/long-lower-shadow-strategy?lower_shadow_ratio=1.5&upper_shadow_ratio=0.25&min_amplitude=0.03&recent_days=3"
```

### 4. 检查参数是否正确传递
在 `screening.js` 中添加调试日志：
```javascript
console.log('参数值:', {
    lowerShadowRatio,
    upperShadowRatio,
    minAmplitude,
    recentDays
});
console.log('完整URL:', url);
```

## 常见错误信息

### "[object Object]"
**原因**: JavaScript错误对象没有正确转换为字符串
**已修复**: ✅

### "422 Unprocessable Entity"
**原因**: 参数验证失败
**检查**: 
- 参数是否超出范围
- 参数类型是否正确

### "500 Internal Server Error"
**原因**: 后端代码错误
**检查**: 
- 后端日志
- 数据库连接
- 代码逻辑

### "Failed to fetch"
**原因**: 网络连接问题
**检查**: 
- 后端服务是否运行
- 端口是否正确
- 防火墙设置

## 验证清单

- [ ] 后端服务正在运行（端口5000）
- [ ] 前端代码已更新（强制刷新）
- [ ] 参数输入框显示正常
- [ ] 参数值在允许范围内
- [ ] API URL构造正确
- [ ] 浏览器控制台无错误
- [ ] 后端日志无错误

## 测试步骤

1. **打开页面**: http://localhost:8000/screening.html
2. **切换到长下影线策略标签**
3. **检查参数配置区域是否显示**
4. **尝试修改参数值**
5. **点击预设按钮测试**
6. **点击"刷新筛选"按钮**
7. **查看结果或错误信息**

## 预期结果

成功时应该看到：
- 参数配置区域正常显示
- 可以输入和修改参数
- 预设按钮可以快速设置参数
- 点击刷新后显示筛选结果
- 结果中包含符合条件的股票列表

## 联系信息

如果问题仍然存在，请提供：
1. 浏览器控制台的完整错误信息
2. Network标签中API请求的详细信息
3. 后端日志的相关部分
4. 使用的参数值
