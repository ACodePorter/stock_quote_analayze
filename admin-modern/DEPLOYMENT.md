# 生产环境部署说明

## 构建步骤

1. **安装依赖**
   ```bash
   npm install
   ```

2. **构建生产版本**
   ```bash
   npm run build
   ```

3. **检查构建结果**
   - 构建完成后，`dist` 目录包含所有静态资源
   - 确保 `dist/index.html` 中的资源路径使用 `/admin/` 前缀

## 部署配置

### 1. Nginx 配置

#### 关键配置点
```nginx
# 管理后台代理配置
location /admin/ {
    # 代理到8001端口，保持/admin路径
    proxy_pass http://admin_server/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Port $server_port;
    
    # 超时设置
    proxy_connect_timeout 30s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
    
    # 添加调试日志
    access_log logs/admin_access.log;
    error_log logs/admin_error.log;
}
```

#### 完整配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 管理后台代理
    location /admin/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. 前端配置

#### Vite 配置
```typescript
// vite.config.ts
export default defineConfig({
  // 生产环境使用 /admin/ 作为基础路径
  base: process.env.NODE_ENV === 'production' ? '/admin/' : '/',
  // ... 其他配置
})
```

#### 路由配置
```typescript
// src/router/index.ts
const router = createRouter({
  history: createWebHistory(process.env.NODE_ENV === 'production' ? '/admin/' : '/'),
  routes
})
```

### 3. 环境变量配置

创建 `.env.production` 文件：
```env
VITE_API_BASE_URL=https://your-domain.com/api/admin
```

## 部署步骤

1. **构建前端**
   ```bash
   cd admin-modern
   npm run build
   ```

2. **部署到服务器**
   - 将 `dist` 目录的内容上传到服务器的 `run/admin-modern` 目录
   - 确保目录结构正确

3. **启动服务**
   ```bash
   # 在 run/admin-modern 目录下启动服务
   python -m http.server 8001
   # 或者使用其他静态文件服务器
   ```

4. **配置Nginx**
   - 更新Nginx配置文件
   - 重新加载Nginx配置：`nginx -s reload`

## 常见问题解决

### 1. 静态资源404错误

**问题**：JS/CSS文件返回404错误
**解决方案**：
- 确保Nginx配置中的 `/admin/` 路径正确代理到8001端口
- 检查 `dist/index.html` 中的资源路径是否为 `/admin/assets/`
- 验证服务器是否正确配置了MIME类型

### 2. 路由问题

**问题**：刷新页面后出现404错误
**解决方案**：
- 确保前端路由配置使用了正确的基础路径
- 检查Nginx配置是否正确处理了所有 `/admin/` 路径

### 3. API请求失败

**问题**：API请求返回401或404错误
**解决方案**：
- 检查API服务器是否正常运行在5000端口
- 验证Nginx的API代理配置是否正确
- 确保CORS配置正确

## 验证方法

1. **访问管理后台**：`https://your-domain.com/admin/`
2. **检查静态资源**：确保所有JS/CSS文件都能正常加载
3. **测试路由**：尝试访问不同的页面路径
4. **检查API**：确保API请求能正常响应

## 部署检查清单

- [ ] 构建成功，无错误
- [ ] `dist` 目录包含所有必要文件
- [ ] 静态资源路径正确（`/admin/assets/`）
- [ ] Nginx配置正确
- [ ] 8001端口服务正常运行
- [ ] API服务正常运行（5000端口）
- [ ] 环境变量配置正确
- [ ] 路由重定向配置正确
- [ ] 缓存策略配置正确

## 性能优化建议

1. **启用Gzip压缩**
2. **配置静态资源缓存**
3. **使用CDN加速**
4. **启用HTTP/2**
5. **优化图片资源**
