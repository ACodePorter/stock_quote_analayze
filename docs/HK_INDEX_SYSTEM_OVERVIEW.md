# 港股指数数据采集系统完整说明

## 系统概述

本系统实现了港股指数数据的完整采集、存储和查询功能，包括：
1. 全量港股指数实时行情采集
2. 港股指数基础信息管理
3. 港股指数历史行情数据归档

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      数据采集层                              │
├─────────────────────────────────────────────────────────────┤
│  AkShare API                                                │
│  ├─ stock_hk_index_spot_em (全量指数)                       │
│  └─ stock_hk_index_daily_sina (主要指数备用)                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    数据处理层                                │
├─────────────────────────────────────────────────────────────┤
│  HKIndexRealtimeCollector                                   │
│  ├─ 数据清洗和转换                                          │
│  ├─ 基础信息提取                                            │
│  └─ 实时行情处理                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    数据存储层                                │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL 数据库                                          │
│  ├─ hk_index_basic_info (基础信息表)                        │
│  ├─ hk_index_realtime_quotes (实时行情表)                   │
│  ├─ hk_index_historical_quotes (历史行情表)                 │
│  └─ hk_index_collect_operation_logs (操作日志表)            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    数据归档层                                │
├─────────────────────────────────────────────────────────────┤
│  HKIndexHistoricalCollector                                 │
│  └─ 每日17:05转存实时数据到历史表                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    API服务层                                 │
├─────────────────────────────────────────────────────────────┤
│  FastAPI                                                    │
│  └─ GET /api/market/hk-indices                              │
│     ├─ 查询当前日期数据                                     │
│     └─ 自动降级到最新日期                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    前端展示层                                │
├─────────────────────────────────────────────────────────────┤
│  Web界面                                                     │
│  └─ 港股指数实时行情展示                                    │
└─────────────────────────────────────────────────────────────┘
```

## 数据库设计

### 1. hk_index_basic_info (港股指数基础信息表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| code | TEXT | PK | 指数代码 |
| name | TEXT | NOT NULL | 指数名称 |
| english_name | TEXT | | 英文名称 |
| created_at | TIMESTAMP | | 创建时间 |
| updated_at | TIMESTAMP | | 更新时间 |

**用途**: 存储港股指数的基本信息，与行情数据分离

### 2. hk_index_realtime_quotes (港股指数实时行情表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| code | TEXT | PK | 指数代码 |
| trade_date | TEXT | PK | 交易日期 (YYYY-MM-DD) |
| name | TEXT | NOT NULL | 指数名称 |
| price | REAL | | 最新价/收盘价 |
| change | REAL | | 涨跌额 |
| pct_chg | REAL | | 涨跌幅(%) |
| open | REAL | | 开盘价 |
| pre_close | REAL | | 昨收价 |
| high | REAL | | 最高价 |
| low | REAL | | 最低价 |
| volume | REAL | | 成交量 |
| amount | REAL | | 成交额 |
| update_time | TEXT | | 更新时间 |
| collect_time | TEXT | | 采集时间 |

**用途**: 按日期存储实时行情数据，支持历史查询

### 3. hk_index_historical_quotes (港股指数历史行情表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| code | TEXT | PK | 指数代码 |
| date | TEXT | PK | 交易日期 (YYYY-MM-DD) |
| name | TEXT | NOT NULL | 指数名称 |
| open | REAL | | 开盘价 |
| high | REAL | | 最高价 |
| low | REAL | | 最低价 |
| close | REAL | | 收盘价 |
| volume | REAL | | 成交量 |
| amount | REAL | | 成交额 |
| change | REAL | | 涨跌额 |
| pct_chg | REAL | | 涨跌幅(%) |
| collected_source | TEXT | | 数据来源 |
| collected_date | TEXT | | 采集时间 |

**用途**: 长期存储历史行情数据，用于分析和回测

### 4. hk_index_collect_operation_logs (操作日志表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PK | 自增ID |
| operation_type | TEXT | NOT NULL | 操作类型 |
| operation_desc | TEXT | NOT NULL | 操作描述 |
| affected_rows | INTEGER | | 影响行数 |
| status | TEXT | NOT NULL | 状态 |
| error_message | TEXT | | 错误信息 |
| created_at | TIMESTAMP | | 创建时间 |

**用途**: 记录所有数据采集操作的日志

## 定时任务配置

### 实时行情采集

```python
scheduler.add_job(
    collect_hk_index_realtime,
    'cron',
    day_of_week='mon-fri',
    hour='9-12,13-16',
    minute='5,35',
    id='hk_index_realtime'
)
```

- **执行时间**: 周一至周五，9-12点和13-16点，每小时的第5分钟和第35分钟
- **频率**: 每30分钟一次
- **功能**: 采集全量港股指数实时行情

### 历史行情归档

```python
scheduler.add_job(
    collect_hk_index_historical,
    'cron',
    day_of_week='mon-fri',
    hour=17,
    minute=5,
    id='hk_index_historical'
)
```

- **执行时间**: 周一至周五，17:05
- **频率**: 每日一次
- **功能**: 将当天实时行情转存到历史行情表

## 数据流转

### 日内数据流

```
09:05 → 实时采集 → hk_index_basic_info + hk_index_realtime_quotes
09:35 → 实时采集 → 更新 hk_index_realtime_quotes
10:05 → 实时采集 → 更新 hk_index_realtime_quotes
...
16:35 → 实时采集 → 更新 hk_index_realtime_quotes (最后一次)
17:05 → 历史归档 → hk_index_realtime_quotes → hk_index_historical_quotes
```

### 数据保留策略

1. **基础信息表**: 永久保留，仅更新
2. **实时行情表**: 按日期保留，支持历史查询
3. **历史行情表**: 永久保留，用于长期分析

## API接口

### GET /api/market/hk-indices

获取港股指数数据

**请求参数**: 无

**返回格式**:
```json
{
  "success": true,
  "data": [
    {
      "code": "HSI",
      "name": "恒生指数",
      "current": 26095.05,
      "change": 62.45,
      "change_percent": 0.24,
      "volume": 0,
      "timestamp": "2025-12-03 16:00:00"
    }
  ]
}
```

**查询逻辑**:
1. 优先查询当前日期的数据
2. 如果当前日期无数据，查询最新日期的数据
3. 返回所有查询到的指数数据

## 核心组件

### 1. HKIndexRealtimeCollector

**文件**: `backend_core/data_collectors/akshare/hk_index_realtime.py`

**功能**:
- 从AkShare获取全量港股指数数据
- 分离基础信息和行情数据
- 批量写入数据库
- 支持多数据源降级

**关键方法**:
- `collect_realtime_quotes()`: 采集实时行情

### 2. HKIndexHistoricalCollector

**文件**: `backend_core/data_collectors/akshare/hk_index_historical_collector.py`

**功能**:
- 从实时行情表读取数据
- 转存到历史行情表
- 支持批量补采历史数据

**关键方法**:
- `collect_daily_to_historical(trade_date)`: 采集指定日期
- `collect_date_range(start_date, end_date)`: 批量采集

## 使用指南

### 手动采集实时数据

```python
from backend_core.data_collectors.akshare.hk_index_realtime import HKIndexRealtimeCollector

collector = HKIndexRealtimeCollector()
result = collector.collect_realtime_quotes()
print(f"采集了 {len(result)} 条数据")
```

### 手动归档历史数据

```python
from backend_core.data_collectors.akshare.hk_index_historical_collector import HKIndexHistoricalCollector

collector = HKIndexHistoricalCollector()

# 采集当天
result = collector.collect_daily_to_historical()

# 采集指定日期
result = collector.collect_daily_to_historical('2025-12-03')

# 批量采集
result = collector.collect_date_range('2025-11-01', '2025-11-30')
```

### 测试脚本

```bash
# 测试实时采集
python test\test_hk_index_collection.py

# 测试历史归档
python test\test_hk_index_historical.py
```

## 监控和维护

### 查看采集日志

```sql
-- 查看最近的采集记录
SELECT * FROM hk_index_collect_operation_logs
ORDER BY created_at DESC
LIMIT 20;

-- 查看失败的采集
SELECT * FROM hk_index_collect_operation_logs
WHERE status = 'error'
ORDER BY created_at DESC;

-- 统计采集成功率
SELECT 
    operation_type,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as failed
FROM hk_index_collect_operation_logs
GROUP BY operation_type;
```

### 数据质量检查

```sql
-- 检查数据完整性
SELECT 
    code,
    name,
    COUNT(DISTINCT trade_date) as trading_days
FROM hk_index_realtime_quotes
GROUP BY code, name
ORDER BY code;

-- 检查最新数据时间
SELECT 
    code,
    name,
    MAX(trade_date) as latest_date,
    MAX(update_time) as latest_update
FROM hk_index_realtime_quotes
GROUP BY code, name;

-- 检查历史数据覆盖
SELECT 
    MIN(date) as earliest_date,
    MAX(date) as latest_date,
    COUNT(DISTINCT date) as total_days
FROM hk_index_historical_quotes;
```

## 相关文档

1. [港股指数全量采集功能更新说明](HK_INDEX_FULL_COLLECTION_UPDATE.md)
2. [港股指数历史行情采集功能](HK_INDEX_HISTORICAL_COLLECTION.md)

## 注意事项

1. **网络依赖**: 数据采集依赖AkShare接口，建议配置网络代理
2. **数据时效**: 实时数据每30分钟更新一次
3. **存储空间**: 历史数据会持续增长，需定期监控存储空间
4. **错误处理**: 采集失败会自动记录日志，不影响其他任务

## 后续优化方向

1. 添加数据质量监控和告警
2. 实现数据缓存机制提高查询效率
3. 支持更多维度的数据分析
4. 添加数据导出和备份功能
5. 实现数据可视化展示
