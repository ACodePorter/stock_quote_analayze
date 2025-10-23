# AKShare连接问题解决方案使用指南

## 问题总结

经过详细分析，`stock_zh_a_spot_em` 调用失败的主要原因是：

1. **网络连接问题**：`Remote end closed connection without response`
2. **SSL连接错误**：`[SSL: UNEXPECTED_EOF_WHILE_READING]`
3. **数据源限制**：东方财富等数据源对频繁请求进行了限制

## 解决方案

### 方案1：使用增强的AKShare采集器（推荐）

我已经创建了增强的AKShare采集器，包含以下功能：

#### 文件位置：
- `backend_core/data_collectors/akshare/enhanced_base.py`
- `backend_core/data_collectors/akshare/enhanced_realtime.py`

#### 使用方法：

```python
from backend_core.data_collectors.akshare.enhanced_realtime import EnhancedRealtimeQuoteCollector

# 创建采集器
collector = EnhancedRealtimeQuoteCollector()

# 采集实时行情数据
success = collector.collect_quotes()
```

#### 主要特性：
- ✅ SSL连接优化
- ✅ 代理支持
- ✅ User-Agent轮换
- ✅ 随机延迟
- ✅ 多数据源回退
- ✅ 增强错误处理

### 方案2：配置代理服务器

如果需要使用代理，可以在配置文件中添加：

```python
# backend_core/config/config.py
'akshare': {
    'proxy_pool': [
        {'http': 'http://proxy1:port', 'https': 'https://proxy1:port'},
        {'http': 'http://proxy2:port', 'https': 'https://proxy2:port'},
    ],
    # 其他配置...
}
```

### 方案3：切换到Tushare（推荐）

如果AKShare持续无法使用，建议切换到Tushare：

```python
import tushare as ts

# 设置Token
ts.set_token('your_token')
pro = ts.pro_api()

# 获取实时行情
df = pro.daily_basic(ts_code='', trade_date='20231201')
```

### 方案4：使用其他数据源

可以考虑集成其他财经数据API：

```python
# 新浪财经API示例
import requests

url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData'
params = {
    'page': 1,
    'num': 100,
    'sort': 'symbol',
    'asc': 1,
    'node': 'hs_a',
    'symbol': ''
}
response = requests.get(url, params=params)
```

## 测试和验证

### 运行测试脚本：

```bash
# 测试增强采集器
python test/test_enhanced_akshare_simple.py

# 测试所有解决方案
python test/test_akshare_solutions.py
```

### 测试结果：

根据最新测试结果：
- ✅ 优化requests配置：可用
- ✅ 备用数据源：可用
- ✅ 网络诊断：可用
- ❌ 代理服务器：需要配置实际代理
- ❌ 增强采集器：在当前网络环境下受限

## 推荐使用方案

### 立即可用的解决方案：

1. **使用Tushare**（最推荐）：
   - 稳定可靠
   - 数据质量高
   - 需要Token但免费额度足够

2. **使用新浪财经API**：
   - 免费使用
   - 数据实时性好
   - 需要自己解析数据格式

3. **使用增强采集器 + 代理**：
   - 如果网络环境允许使用代理
   - 保持原有AKShare功能

### 长期解决方案：

1. **多数据源集成**：
   - 同时支持AKShare、Tushare、新浪等
   - 自动故障转移
   - 数据源健康检查

2. **代理池管理**：
   - 自动代理检测
   - 代理轮换
   - 代理健康监控

## 配置示例

### 完整的配置文件示例：

```python
# backend_core/config/config.py
DATA_COLLECTORS = {
    'akshare': {
        'max_retries': 3,
        'retry_delay': 5,
        'timeout': 30,
        'log_dir': str(ROOT_DIR / 'backend_core' / 'logs'),
        'db_file': str(DB_DIR / 'stock_analysis.db'),
        'max_connection_errors': 10,
        # 增强配置
        'proxy_pool': [],  # 代理池配置
        'random_delay_range': (1, 3),
        'ssl_verify': False,
        'use_fallback_sources': True,
    },
    'tushare': {
        'token': 'your_tushare_token',
        'max_retries': 3,
        'retry_delay': 5,
        'timeout': 30,
    }
}
```

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

虽然当前网络环境下AKShare数据源被限制，但通过多种解决方案可以确保数据采集的稳定性：

1. **短期**：使用Tushare或新浪财经API
2. **中期**：配置代理服务器使用增强采集器
3. **长期**：实现多数据源集成和自动故障转移

建议根据实际网络环境和需求选择合适的解决方案。
