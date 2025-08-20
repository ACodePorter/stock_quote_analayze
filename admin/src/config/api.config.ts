// API配置文件
export const API_CONFIG = {
  // 开发环境
  development: {
    baseURL: 'http://localhost:5000/api/admin',
    timeout: 30000
  },
  // 生产环境
  production: {
    baseURL: 'http://192.168.31.237:5000/api/admin',
    timeout: 30000
  },
  // 测试环境
  test: {
    baseURL: 'http://localhost:5000/api/admin',
    timeout: 30000
  }
}

// 获取当前环境
const getCurrentEnv = (): keyof typeof API_CONFIG => {
  if (import.meta.env.DEV) return 'development'
  if (import.meta.env.PROD) return 'production'
  return 'development'
}

// 导出当前环境的配置
export const getApiConfig = () => {
  const env = getCurrentEnv()
  return API_CONFIG[env]
}
