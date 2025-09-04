# 生产环境部署配置（后端不改方案）

## 当前架构
- **前端访问地址**: `https://www.icemaplecity.com/admin` → 8001端口
- **API服务端口**: 5000端口
- **数据采集API路由**: `/data-collection`

## 问题分析
生产环境中前端请求 `https://www.icemaplecity.com/data-collection/...` 返回404，说明反向代理配置可能有问题。

## 解决方案

### 方案一：配置反向代理（推荐）
在生产环境的反向代理配置中添加API路由转发：

```nginx
# Nginx配置示例
server {
    listen 443 ssl;
    server_name www.icemaplecity.com;
    
    # 前端静态文件
    location /admin {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # API服务转发
    location /data-collection {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 其他API路由
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 方案二：修改前端配置
如果无法修改反向代理，可以修改前端配置指向正确的API地址：

```typescript
// 生产环境配置
production: {
  baseURL: 'http://localhost:5000',  // 直接访问API服务
  timeout: 30000
}
```

### 方案三：使用环境变量
通过环境变量配置API地址：

```bash
# .env.production
VITE_API_BASE_URL=http://localhost:5000
```

## 验证步骤

1. **检查API服务状态**：
   ```bash
   curl http://localhost:5000/data-collection/stock-list
   ```

2. **检查反向代理配置**：
   ```bash
   curl https://www.icemaplecity.com/data-collection/stock-list
   ```

3. **重新构建前端**：
   ```bash
   cd admin
   npm run build
   ```

## 注意事项

1. **CORS配置**：确保API服务允许前端域名访问
2. **防火墙**：确保5000端口对外开放
3. **SSL证书**：生产环境建议使用HTTPS
4. **日志监控**：监控API服务的访问日志

## 常见问题

### Q: 生产环境API返回404
A: 检查反向代理配置是否正确转发了API路由

### Q: CORS错误
A: 检查API服务的CORS配置，确保允许前端域名访问

### Q: 连接超时
A: 检查API服务是否正常运行，以及网络连通性
