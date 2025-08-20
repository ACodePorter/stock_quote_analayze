// 环境配置测试脚本
// 用于验证当前环境配置是否正确

console.log('🚀 股票分析系统管理后台 - 环境配置测试');
console.log('==========================================');

// 模拟环境变量
const mockEnv = {
  DEV: false,
  PROD: true,
  MODE: 'production'
};

// 模拟 import.meta.env
const importMetaEnv = {
  DEV: mockEnv.DEV,
  PROD: mockEnv.PROD,
  MODE: mockEnv.MODE
};

// 环境检测逻辑
const isProduction = importMetaEnv.PROD;
const isDevelopment = importMetaEnv.DEV;
const current = isProduction ? 'production' : 'development';

// 环境配置
const ENV_CONFIG = {
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
};

// 获取当前环境配置
const getCurrentEnvConfig = () => {
  return ENV_CONFIG[current] || ENV_CONFIG.development;
};

// 测试结果
console.log('🌍 当前环境:', current);
console.log('🔗 API地址:', getCurrentEnvConfig().apiBaseUrl);
console.log('🐛 调试模式:', getCurrentEnvConfig().enableDebug);
console.log('📝 日志级别:', getCurrentEnvConfig().logLevel);

// 验证配置
const config = getCurrentEnvConfig();
if (config.apiBaseUrl.includes('icemaplecity.com')) {
  console.log('✅ 生产环境配置正确');
} else if (config.apiBaseUrl.includes('localhost')) {
  console.log('✅ 开发环境配置正确');
} else {
  console.log('❌ 环境配置异常');
}

console.log('\n📋 配置验证完成');
console.log('💡 提示: 在生产环境中，请确保:');
console.log('   1. 域名 www.icemaplecity.com 可以正常访问');
console.log('   2. HTTPS 证书配置正确');
console.log('   3. 后端API服务正在运行');
