# AKShare连接问题解决方案

## 问题分析

经过测试发现，`stock_zh_a_spot_em` 调用失败的主要原因是：

1. **SSL连接错误**：`[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol`
2. **连接被重置**：`Remote end closed connection without response`
3. **IP封禁或频率限制**：所有AKShare数据源都无法正常访问

## 解决方案

### 1. 增强的AKShare采集器

我已经创建了增强的AKShare采集器，包含以下功能：

#### 文件位置：
- `backend_core/data_collectors/akshare/enhanced_base.py` - 增强的基础采集器
- `backend_core/data_collectors/akshare/enhanced_realtime.py` - 增强的实时行情采集器

#### 主要功能：
1. **SSL连接优化**：
   - 自定义SSL上下文
   - 支持SSL验证开关
   - 连接重试机制

2. **代理支持**：
   - 代理池轮换
   - 支持HTTP/HTTPS代理
   - 自动代理切换

3. **User-Agent轮换**：
   - 多个浏览器User-Agent
   - 自动轮换避免检测

4. **随机延迟**：
   - 1-3秒随机延迟
   - 避免频率过高被限制

5. **多数据源回退**：
   - `stock_zh_a_spot_em` (主要)
   - `stock_sh_a_spot_em` (上海)
   - `stock_sz_a_spot_em` (深圳)
   - `stock_bj_a_spot_em` (北京)

### 2. 配置更新

更新了 `backend_core/config/config.py`，添加了增强配置：

```python
'akshare': {
    'max_retries': 3,
    'retry_delay': 5,
    'timeout': 30,
    'log_dir': str(ROOT_DIR / 'backend_core' / 'logs'),
    'db_file': str(DB_DIR / 'stock_analysis.db'),
    'max_connection_errors': 10,
    # 增强配置
    'proxy_pool': [],  # 代理池配置
    'random_delay_range': (1, 3),  # 随机延迟范围
    'ssl_verify': False,  # SSL验证开关
    'use_fallback_sources': True,  # 是否使用备用数据源
}
```

## 使用建议

### 1. 立即可用的解决方案

由于当前网络环境下AKShare数据源都被限制，建议：

1. **使用代理服务**：
   ```python
   # 在配置中添加代理
   'proxy_pool': [
       {'http': 'http://proxy1:port', 'https': 'https://proxy1:port'},
       {'http': 'http://proxy2:port', 'https': 'https://proxy2:port'},
   ]
   ```

2. **使用VPN或更换网络环境**

3. **考虑其他数据源**：
   - Tushare（需要Token）
   - 新浪财经API
   - 腾讯财经API
   - 东方财富API

### 2. 测试脚本

创建了测试脚本验证解决方案：
- `test/test_enhanced_akshare_simple.py` - 简化测试
- `test/test_enhanced_akshare_collector.py` - 完整测试

### 3. 使用方法

```python
from backend_core.data_collectors.akshare.enhanced_realtime import EnhancedRealtimeQuoteCollector

# 创建采集器
collector = EnhancedRealtimeQuoteCollector()

# 采集实时行情数据
success = collector.collect_quotes()
```

## 备用方案

### 1. 使用Tushare

如果AKShare持续无法使用，可以考虑切换到Tushare：

```python
import tushare as ts

# 设置Token
ts.set_token('your_token')
pro = ts.pro_api()

# 获取实时行情
df = pro.daily_basic(ts_code='', trade_date='20231201')
```

### 2. 使用其他数据源

可以考虑集成其他财经数据API：
- 新浪财经
- 腾讯财经
- 网易财经
- 和讯财经

## 监控和维护

1. **日志监控**：
   - 检查 `backend_core/logs/` 目录下的日志文件
   - 监控连接错误和重试情况

2. **定期测试**：
   - 定期运行测试脚本验证数据源可用性
   - 及时更新代理配置

3. **数据源切换**：
   - 根据网络环境动态切换数据源
   - 实现数据源健康检查

## 总结

虽然当前网络环境下AKShare数据源被限制，但通过增强的采集器和多种备用方案，可以确保数据采集的稳定性。建议：

1. 配置代理服务解决连接问题
2. 考虑集成多个数据源
3. 实现自动故障转移机制
4. 定期监控和维护数据采集服务
