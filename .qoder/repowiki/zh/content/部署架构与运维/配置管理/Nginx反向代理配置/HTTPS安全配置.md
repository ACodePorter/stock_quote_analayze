# HTTPS安全配置

<cite>
**本文档引用文件**  
- [nginx_complete.conf](file://nginx_complete.conf)
- [生产环境说明.md](file://生产环境说明.md)
- [docs/prod/nginx-ok-https.conf](file://docs/prod/nginx-ok-https.conf)
- [docs/fixed/nginx_ssl_fix.conf](file://docs/fixed/nginx_ssl_fix.conf)
</cite>

## 目录
1. [SSL证书与协议配置](#ssl证书与协议配置)  
2. [安全头配置说明](#安全头配置说明)  
3. [性能优化建议](#性能优化建议)  
4. [常见SSL问题排查](#常见ssl问题排查)

## SSL证书与协议配置

Nginx的HTTPS配置基于`nginx_complete.conf`文件中的SSL设置，确保了安全通信的建立。SSL证书路径、协议版本、加密套件、会话缓存和超时时间均经过精心配置，以满足现代安全标准。

### SSL证书路径配置

SSL证书和私钥的路径在配置文件中明确指定，确保Nginx能够正确加载并使用证书进行TLS握手。

- **证书文件路径**: `C:/work/stock_quote_analayze/tools/nginx/ssl/www.icemaplecity.com-chain.pem`  
- **私钥文件路径**: `C:/work/stock_quote_analayze/tools/nginx/ssl/www.icemaplecity.com-key.pem`

这些路径指向Let's Encrypt签发的证书链和对应的私钥文件，确保证书链完整，避免客户端因证书链不完整而产生安全警告。

### TLS协议与加密套件

TLS协议版本和加密套件的选择直接影响通信的安全性与兼容性。

- **启用的TLS版本**: 仅启用TLS 1.2和TLS 1.3，禁用不安全的SSLv3和TLS 1.0/1.1。
- **加密套件配置**:  
  ```
  ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
  ```
  该配置优先使用前向安全的ECDHE密钥交换算法，结合AES-GCM高强度加密，确保数据传输的机密性和完整性。

- **服务器优先选择加密套件**:  
  `ssl_prefer_server_ciphers on;`  
  此设置确保服务器在协商加密套件时拥有最终决定权，防止客户端选择弱加密算法。

### 会话缓存与超时设置

会话缓存可显著提升HTTPS性能，减少重复的TLS握手开销。

- **会话缓存配置**:  
  `ssl_session_cache shared:SSL:1m;`  
  使用共享内存缓存（1MB），可存储约4000个并发会话，适用于多worker进程环境。

- **会话超时时间**:  
  `ssl_session_timeout 5m;`  
  会话有效期为5分钟，平衡安全性与性能。过长的会话时间可能增加重放攻击风险，过短则影响性能。

**Section sources**  
- [nginx_complete.conf](file://nginx_complete.conf#L65-L70)

## 安全头配置说明

安全头是Web应用安全的重要组成部分，通过HTTP响应头向浏览器传达安全策略。结合`生产环境说明.md`中的服务器信息，以下为关键安全头的配置与意义。

### HSTS (HTTP Strict Transport Security)

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

- **作用**: 强制浏览器在一年内（31536000秒）仅通过HTTPS访问该域名及其子域名，防止中间人攻击和SSL剥离。
- **最佳实践**: 启用`includeSubDomains`确保所有子域名也受保护，建议搭配HSTS预加载列表使用。

### X-Frame-Options

```nginx
add_header X-Frame-Options DENY always;
```

- **作用**: 防止页面被嵌入到`<frame>`、`<iframe>`中，抵御点击劫持（Clickjacking）攻击。
- **取值说明**: `DENY`表示禁止任何网站嵌套，`SAMEORIGIN`允许同源嵌套。

### X-Content-Type-Options

```nginx
add_header X-Content-Type-Options nosniff always;
```

- **作用**: 禁止浏览器进行MIME类型嗅探，防止攻击者上传恶意文件并诱导浏览器执行。
- **意义**: 确保服务器声明的`Content-Type`被严格遵守，避免XSS风险。

### X-XSS-Protection

```nginx
add_header X-XSS-Protection "1; mode=block" always;
```

- **作用**: 启用浏览器的内置XSS过滤器，发现反射型XSS攻击时阻止页面加载。
- **配置说明**: `mode=block`会在检测到攻击时阻止整个页面渲染，比`mode=report`更安全。

**Section sources**  
- [nginx_complete.conf](file://nginx_complete.conf#L75-L78)  
- [生产环境说明.md](file://生产环境说明.md#L1-L187)

## 性能优化建议

### 启用HTTP/2

```nginx
listen 443 ssl;
http2 on;
```

- **优势**: HTTP/2支持多路复用、头部压缩，显著提升页面加载速度，尤其对资源密集型应用。
- **前提**: 必须启用HTTPS，且客户端支持HTTP/2。

### 合理设置会话缓存

- **缓存大小**: `shared:SSL:1m`适用于中小型应用。高并发场景可调整为`10m`或更大。
- **监控建议**: 定期检查Nginx状态，观察会话缓存命中率，优化缓存大小。

### 静态资源缓存

对前端静态资源（如JS、CSS、图片）配置长期缓存：

```nginx
location ~ ^/assets/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

- **效果**: 减少重复请求，提升用户体验，降低服务器负载。

**Section sources**  
- [nginx_complete.conf](file://nginx_complete.conf#L130-L135)

## 常见SSL问题排查

### 证书链不完整

- **现象**: 浏览器提示“您的连接不是私密连接”或“此网站的安全证书不完整”。
- **原因**: 仅部署了域名证书，未包含中间CA证书。
- **解决方案**: 使用`chain.pem`文件（包含域名证书+中间证书）作为`ssl_certificate`，确保完整证书链。

### 加密套件不匹配

- **现象**: 某些旧客户端（如IE8、Android 4.x）无法访问。
- **原因**: 服务器配置的加密套件过于严格，客户端不支持ECDHE或AES-GCM。
- **解决方案**: 在安全允许范围内，适度添加兼容性套件，如：
  ```
  ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:AES128-GCM-SHA256:HIGH:!aNULL:!MD5;
  ```

### 会话恢复失败

- **现象**: TLS握手频繁，性能下降。
- **原因**: `ssl_session_cache`未配置或大小不足，或负载均衡环境下未共享缓存。
- **解决方案**: 确保配置`shared:SSL:1m`以上缓存，并在集群环境中使用外部缓存（如Redis）同步会话。

### HSTS导致无法访问HTTP

- **现象**: 误配置HSTS后，无法通过HTTP访问测试环境。
- **解决方案**: 清除浏览器HSTS策略（Chrome: `chrome://net-internals/#hsts`），或等待`max-age`过期。

**Section sources**  
- [nginx_complete.conf](file://nginx_complete.conf#L65-L80)  
- [生产环境说明.md](file://生产环境说明.md#L1-L187)