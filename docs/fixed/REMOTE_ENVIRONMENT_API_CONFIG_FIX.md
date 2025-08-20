# 远程环境API配置修复总结

## 问题描述
在远程环境中运行时，前端应用出现以下错误：
```
POST http://localhost:5000/api/admin/auth/login net::ERR_CONNECTION_REFUSED
No auth token found for request: /auth/login
```

## 问题原因分析
1. **本地地址配置错误**：前端配置为连接到 `localhost:5000`，这在远程环境中无法访问
2. **环境配置缺失**：缺少针对不同环境的配置文件
3. **API地址硬编码**：API基础URL被硬编码为本地地址

## 解决方案

### 1. 创建环境配置文件
创建了 `admin/src/config/environment.ts` 文件，提供环境检测和配置管理：

```typescript
export const ENV_CONFIG = {
  development: {
    apiBaseUrl: 'http://localhost:5000/api/admin',
    enableDebug: true,
    logLevel: 'debug'
  },
  production: {
    apiBaseUrl: 'https://www.icemaplecity.com/api/admin',
    enableDebug: false,
    logLevel: 'info'
  }
}
```

### 2. 更新API服务配置
修改了 `admin/src/services/api.ts` 文件：
- 导入环境配置模块
- 使用环境检测自动选择正确的API地址
- 添加环境信息日志输出

### 3. 创建环境部署脚本
提供了两个环境配置脚本：
- `admin/deploy-env.sh` (Linux/Mac)
- `admin/deploy-env.bat` (Windows)

## 使用方法

### 配置生产环境
```bash
# Linux/Mac
./deploy-env.sh production

# Windows
deploy-env.bat production
```

### 配置开发环境
```bash
# Linux/Mac
./deploy-env.sh development

# Windows
deploy-env.bat development
```

## 配置后的效果
- ✅ 自动检测当前环境
- ✅ 根据环境选择正确的API地址
- ✅ 支持开发和生产环境切换
- ✅ 提供环境信息日志输出

## 注意事项
1. **环境变量优先级**：`VITE_API_BASE_URL` 环境变量会覆盖默认配置
2. **重新构建**：修改环境配置后需要重新构建项目
3. **生产环境域名**：生产环境使用 `https://www.icemaplecity.com` 域名
4. **HTTPS支持**：确保生产环境支持HTTPS协议
5. **CORS配置**：后端API已配置允许来自生产域名的跨域请求

## 修复日期
2024年12月19日

## 相关文件
- `admin/src/config/environment.ts` - 环境配置
- `admin/src/services/api.ts` - API服务配置
- `admin/deploy-env.sh` - Linux/Mac环境配置脚本
- `admin/deploy-env.bat` - Windows环境配置脚本
