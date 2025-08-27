# 历史换手率数据采集器使用说明

## 概述

历史换手率数据采集器（`HistoricalTurnoverRateCollector`）是专门用于补充Tushare历史行情数据中缺失的换手率信息的工具。该采集器通过AKShare接口获取历史换手率数据，并将其更新到现有的`historical_quotes`表中。

## 问题背景

- **Tushare历史行情接口**：提供完整的历史价格、成交量等数据，但缺少换手率字段
- **AKShare实时行情接口**：提供换手率数据，但主要用于实时数据
- **解决方案**：结合两个数据源，使用AKShare补充Tushare缺失的换手率数据

## 功能特性

### 1. 智能数据补充
- 自动识别数据库中缺失换手率数据的股票和日期
- 只更新需要补充的数据，避免重复采集
- 支持批量处理多个股票和多个日期

### 2. 灵活的时间范围
- 支持单日数据采集
- 支持时间段数据采集
- 支持最近N天缺失数据的自动采集

### 3. 错误处理和重试机制
- 内置重试机制，提高数据采集成功率
- 详细的日志记录，便于问题排查
- 优雅的信号处理，支持安全退出

### 4. 性能优化
- 请求频率控制，避免对数据源造成压力
- 批量数据库操作，提高更新效率
- 智能跳过周末等非交易日

## 使用方法

### 1. 基本使用

```python
from backend_core.data_collectors.akshare.historical_turnover_rate import HistoricalTurnoverRateCollector
from backend_core.config.config import DATA_COLLECTORS

# 初始化采集器
collector = HistoricalTurnoverRateCollector(DATA_COLLECTORS.get('akshare', {}))

# 采集最近30天缺失的换手率数据
success = collector.collect_missing_turnover_rate(30)
```

### 2. 单日数据采集

```python
# 为指定日期采集换手率数据
success = collector.collect_turnover_rate_for_date('2025-08-25')
```

### 3. 时间段数据采集

```python
# 为指定时间段采集换手率数据
success = collector.collect_turnover_rate_for_period('2025-08-20', '2025-08-26')
```

### 4. 运行采集器

```python
# 运行采集器（默认采集最近30天数据）
collector.run()
```

## 命令行使用

### 1. 启动采集器

```bash
# 在backend_core目录下
python start_turnover_rate_collector.py
```

### 2. 运行测试

```bash
# 运行测试脚本
python test_turnover_rate_collector.py
```

## 定时任务集成

历史换手率采集器已集成到主采集器的定时任务中：

- **执行频率**：每周一至周五上午10点
- **采集范围**：最近30天缺失的换手率数据
- **任务ID**：`akshare_turnover_rate`

## 数据流程

### 1. 数据识别
```sql
-- 查询缺失换手率数据的股票
SELECT DISTINCT code, name 
FROM historical_quotes 
WHERE date = '2025-08-25' 
  AND (turnover_rate IS NULL OR turnover_rate = 0)
```

### 2. 数据获取
- 使用AKShare的`stock_zh_a_hist`接口
- 获取指定股票在目标日期前后的历史数据
- 提取换手率字段并进行数据清洗

### 3. 数据更新
```sql
-- 更新换手率数据
UPDATE historical_quotes 
SET turnover_rate = :turnover_rate 
WHERE code = :code AND date = :date
```

## 配置说明

采集器使用AKShare的配置参数：

```python
DATA_COLLECTORS = {
    'akshare': {
        'max_retries': 3,        # 最大重试次数
        'retry_delay': 5,        # 重试延迟（秒）
        'timeout': 30,           # 请求超时时间（秒）
        'log_dir': 'logs',       # 日志目录
        'db_file': 'database/stock_analysis.db'  # 数据库文件路径
    }
}
```

## 日志和监控

### 1. 日志文件
- 主日志：`turnover_rate_collector.log`
- 测试日志：`test_turnover_rate.log`

### 2. 关键日志信息
- 数据采集开始和完成
- 成功/失败统计
- 错误详情和异常信息
- 性能指标（处理速度、成功率等）

## 注意事项

### 1. 数据源限制
- AKShare接口可能有访问频率限制
- 建议在生产环境中适当调整请求间隔
- 注意监控接口的稳定性和可用性

### 2. 数据质量
- 换手率数据可能存在精度差异
- 建议定期验证数据的准确性和一致性
- 对于异常数据，记录日志并标记

### 3. 性能考虑
- 大量历史数据补充可能需要较长时间
- 建议在系统负载较低时执行
- 可以考虑分批处理，避免单次处理过多数据

## 故障排除

### 1. 常见问题

**问题**：无法连接到AKShare接口
**解决**：检查网络连接，确认AKShare包版本，适当增加重试次数

**问题**：数据库更新失败
**解决**：检查数据库连接，确认表结构，查看详细错误日志

**问题**：换手率数据为空
**解决**：检查股票代码格式，确认数据源是否有该股票的数据

### 2. 调试方法

```python
# 启用调试日志
logging.getLogger().setLevel(logging.DEBUG)

# 测试单个股票
df = collector._fetch_stock_turnover_rate("000001", "2025-08-20", "2025-08-26")
print(df)
```

## 扩展功能

### 1. 数据验证
- 添加换手率数据的合理性检查
- 实现数据一致性验证
- 支持数据质量报告生成

### 2. 性能优化
- 实现并行数据采集
- 添加数据缓存机制
- 优化数据库查询性能

### 3. 监控告警
- 集成系统监控
- 添加异常告警机制
- 实现数据完整性检查

## 总结

历史换手率数据采集器通过混合数据源策略，有效解决了Tushare历史数据中换手率缺失的问题。该方案具有以下优势：

1. **风险低**：保持现有Tushare采集流程不变
2. **实施简单**：只需要新增换手率采集模块
3. **数据完整**：确保历史数据包含所有必要字段
4. **维护成本低**：不需要大幅修改现有代码结构

通过合理配置和监控，该采集器可以为系统提供完整、准确的历史换手率数据，满足股票分析的需求。
