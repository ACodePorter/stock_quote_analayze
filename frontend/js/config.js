// 环境配置
const Config = {
    // 检测当前环境
    getEnvironment() {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol;
        
        // 生产环境检测
        if (hostname === 'www.icemaplecity.com' || hostname === 'icemaplecity.com' || hostname === 'erp.icemaplecity.com') {
            return 'production';
        }
        
        // 开发环境检测
        if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.')) {
            return 'development';
        }
        
        // 默认返回开发环境
        return 'development';
    },
    
    // 获取API基础URL
    getApiBaseUrl() {
        const environment = this.getEnvironment();
        
        switch (environment) {
            case 'production':
                // 生产环境使用相对路径，让浏览器自动处理协议和域名
                return '';
            case 'development':
            default:
                // 开发环境使用具体的IP和端口
                return 'http://localhost:5000';
        }
    },
    
    // 获取完整的API URL
    getApiUrl(path) {
        const baseUrl = this.getApiBaseUrl();
        const apiPath = path.startsWith('/') ? path : `/${path}`;
        
        if (baseUrl) {
            return `${baseUrl}${apiPath}`;
        } else {
            // 生产环境使用相对路径
            return apiPath;
        }
    },
    
    // 获取当前环境信息
    getEnvironmentInfo() {
        return {
            environment: this.getEnvironment(),
            hostname: window.location.hostname,
            protocol: window.location.protocol,
            apiBaseUrl: this.getApiBaseUrl()
        };
    }
};

// 导出配置
window.Config = Config;
