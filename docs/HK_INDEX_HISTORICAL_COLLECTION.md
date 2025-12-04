# 港股指数历史行情数据采集功能

## 功能概述

实现每日休市后自动将港股指数实时行情数据转存到历史行情表，用于历史数据分析和查询。

## 实现方案

### 数据流程

```
实时行情表 (hk_index_realtime_quotes)
         ↓
    [每日17:05执行]
         ↓
历史行情表 (hk_index_historical_quotes)
```

### 核心逻辑

1. **数据源**: 从 `hk_index_realtime_quotes` 表读取当天的实时行情数据
2. **数据转换**: 将实时行情字段映射到历史行情字段
3. **数据存储**: 使用 UPSERT 方式写入 `hk_index_historical_quotes` 表
4. **执行时间**: 每日17:05（港股休市后）

## 主要文件

### 1. 数据采集器 (`hk_index_historical_collector.py`)

**HKIndexHistoricalCollector** 类

#### 主要方法

**collect_daily_to_historical(trade_date=None)**
- 功能：将指定日期的实时行情转存到历史行情表
- 参数：
  - `trade_date`: 交易日期（YYYY-MM-DD），默认为当天
- 返回：包含成功/失败统计的字典

**collect_date_range(start_date, end_date)**
- 功能：批量采集指定日期范围的历史行情
- 参数：
  - `start_date`: 开始日期（YYYY-MM-DD）
  - `end_date`: 结束日期（YYYY-MM-DD）
- 返回：包含总体统计信息的字典

#### 字段映射

| 实时行情字段 | 历史行情字段 | 说明 |
|------------|------------|------|
| code | code | 指数代码 |
| name | name | 指数名称 |
| trade_date | date | 交易日期 |
| open | open | 开盘价 |
| high | high | 最高价 |
| low | low | 最低价 |
| price | close | 收盘价 |
| volume | volume | 成交量 |
| amount | amount | 成交额 |
| change | change | 涨跌额 |
| pct_chg | pct_chg | 涨跌幅 |
| - | collected_source | 数据来源（固定为'realtime_quotes'） |
| - | collected_date | 采集时间 |

### 2. 定时任务配置 (`main.py`)

#### 任务函数

```python
def collect_hk_index_historical():
    """港股指数历史行情采集定时任务"""
    try:
        logging.info("[定时任务] 港股指数历史行情采集开始...")
        result = hk_index_historical_collector.collect_daily_to_historical()
        if result and result.get('success', 0) > 0:
            logging.info(f"[定时任务] 港股指数历史行情采集完成: {result.get('message', '')}")
        else:
            logging.warning(f"[定时任务] 港股指数历史行情采集失败: {result.get('message', '未知错误')}")
    except Exception as e:
        logging.error(f"[定时任务] 港股指数历史行情采集异常: {e}")
```

#### 调度配置

```python
scheduler.add_job(
    collect_hk_index_historical, 
    'cron', 
    day_of_week='mon-fri',  # 周一至周五
    hour=17,                 # 17点
    minute=5,                # 5分
    id='hk_index_historical'
)
```

## 使用方法

### 1. 手动执行

#### 采集当天数据

```python
from backend_core.data_collectors.akshare.hk_index_historical_collector import HKIndexHistoricalCollector

collector = HKIndexHistoricalCollector()
result = collector.collect_daily_to_historical()
print(result)
```

#### 采集指定日期数据

```python
result = collector.collect_daily_to_historical('2025-12-03')
print(result)
```

#### 批量采集历史数据

```python
result = collector.collect_date_range('2025-11-01', '2025-11-30')
print(result)
```

### 2. 测试脚本

```bash
cd e:\wangxw\股票分析软件\编码\stock_quote_analayze
python test\test_hk_index_historical.py
```

### 3. 定时任务

定时任务已集成到主数据采集程序中，会自动运行：
- **执行时间**: 周一至周五 17:05
- **任务ID**: `hk_index_historical`

## 返回数据格式

### 成功返回

```json
{
  "success": 344,
  "failed": 0,
  "skipped": 0,
  "trade_date": "2025-12-03",
  "message": "成功转存344条历史行情数据"
}
```

### 失败返回

```json
{
  "success": 0,
  "failed": 0,
  "skipped": 0,
  "error": "错误信息",
  "message": "采集失败: 错误信息"
}
```

### 无数据返回

```json
{
  "success": 0,
  "failed": 0,
  "skipped": 0,
  "message": "未找到日期 2025-12-03 的实时行情数据"
}
```

## 数据库操作

### 查询历史行情

```sql
-- 查询指定指数的历史行情
SELECT * FROM hk_index_historical_quotes
WHERE code = 'HSI'
ORDER BY date DESC
LIMIT 30;

-- 查询指定日期的所有指数
SELECT * FROM hk_index_historical_quotes
WHERE date = '2025-12-03'
ORDER BY code;

-- 统计历史数据量
SELECT code, name, COUNT(*) as days
FROM hk_index_historical_quotes
GROUP BY code, name
ORDER BY code;
```

### 数据更新策略

使用 `ON CONFLICT DO UPDATE` 实现 UPSERT：
- 如果记录不存在：插入新记录
- 如果记录已存在：更新所有字段

## 优势特点

1. **自动化**: 每日定时自动执行，无需人工干预
2. **数据完整**: 保留所有港股指数的历史数据
3. **幂等性**: 支持重复执行，不会产生重复数据
4. **可追溯**: 记录数据来源和采集时间
5. **批量处理**: 支持批量补采历史数据

## 注意事项

1. **执行时间**
   - 17:05执行，确保当天实时行情已采集完成
   - 仅在交易日（周一至周五）执行

2. **数据依赖**
   - 依赖于实时行情表的数据
   - 如果实时行情表无数据，历史采集会失败

3. **数据覆盖**
   - 同一日期的数据会被覆盖（更新）
   - 适合修正当天数据

4. **错误处理**
   - 采集失败会记录到操作日志表
   - 不影响其他定时任务的执行

## 监控和日志

### 操作日志

所有操作都会记录到 `hk_index_collect_operation_logs` 表：

```sql
SELECT * FROM hk_index_collect_operation_logs
WHERE operation_type = 'hk_index_historical_collect'
ORDER BY created_at DESC
LIMIT 10;
```

### 日志字段

- `operation_type`: 操作类型（hk_index_historical_collect）
- `operation_desc`: 操作描述
- `affected_rows`: 影响行数
- `status`: 状态（success/partial_success/error）
- `error_message`: 错误信息
- `created_at`: 创建时间

## 相关文件

- `backend_core/data_collectors/akshare/hk_index_historical_collector.py` - 历史行情采集器
- `backend_core/data_collectors/main.py` - 定时任务配置
- `test/test_hk_index_historical.py` - 测试脚本
- `backend_api/models.py` - 数据库模型

## 后续优化建议

1. 添加数据质量检查（如检查是否有缺失日期）
2. 支持数据补采提醒
3. 添加数据统计分析功能
4. 实现数据导出功能
