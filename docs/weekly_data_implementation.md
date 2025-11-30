# A股周线数据采集方案实施总结

## 方案变更

根据用户要求，已将周线数据采集方案从"直接从AKShare API获取周线数据"改为"基于日线数据生成周线数据"。

## 已完成的工作

### 1. 创建周线数据生成器
**文件**: `backend_core/data_collectors/akshare/weekly_collector.py`

**核心功能**:
- 从 `historical_quotes` 表读取日线数据
- 使用 pandas 的 `resample('W-FRI')` 方法将日线数据聚合为周线数据
- 周线数据的聚合规则:
  - **开盘价**: 取该周第一个交易日的开盘价
  - **最高价**: 取该周所有交易日的最高价
  - **最低价**: 取该周所有交易日的最低价
  - **收盘价**: 取该周最后一个交易日的收盘价
  - **成交量**: 该周所有交易日成交量之和
  - **成交额**: 该周所有交易日成交额之和
  - **涨跌幅**: 基于前一周收盘价计算
  - **振幅**: (本周最高 - 本周最低) / 上周收盘 * 100

**数据存储**:
- 表名: `weekly_quotes`
- 主键: (code, date)
- 使用 `ON CONFLICT DO UPDATE` 实现数据更新

### 2. 集成到定时任务调度器
**文件**: `backend_core/data_collectors/main.py`

**调度配置**:
- 任务名称: `generate_weekly_data`
- 执行时间: 每周六凌晨 1:00
- 数据范围: 自动生成过去14天的周线数据

**任务函数**:
```python
def generate_weekly_data():
    """生成周线数据任务"""
    try:
        today = datetime.now()
        end_date = today.strftime('%Y-%m-%d')
        start_date = (today - timedelta(days=14)).strftime('%Y-%m-%d')
        
        logging.info(f"[定时任务] 周线数据生成开始，日期范围: {start_date} - {end_date}")
        result = weekly_generator.generate_weekly_data(start_date, end_date)
        logging.info(f"[定时任务] 周线数据生成完成: {result}")
    except Exception as e:
        logging.error(f"[定时任务] 周线数据生成异常: {e}")
```

## 技术实现细节

### 数据查询优化
为了准确计算涨跌幅等指标，生成器会自动向前多查询40天的数据:
```python
query_start_date = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=40)).strftime('%Y-%m-%d')
```

### 周线标记
- 使用 `W-FRI` (每周五) 作为周线的标记日期
- 即使周五没有交易，pandas 也会将该周的数据标记为该周五的日期

### 数据完整性
- 自动跳过没有日线数据的股票
- 对于计算结果为 NaN 的字段（如第一周的涨跌幅），存储为 NULL

## 使用方法

### 手动执行
```bash
# 生成指定日期范围的周线数据
python backend_core/data_collectors/akshare/weekly_collector.py 2025-01-01 2025-11-30

# 测试模式（只处理前5只股票）
python backend_core/data_collectors/akshare/weekly_collector.py 2025-01-01 2025-11-30 --test

# 指定股票代码
python backend_core/data_collectors/akshare/weekly_collector.py 2025-01-01 2025-11-30 --stocks 000001 600000
```

### 自动执行
启动定时任务调度器后，系统会在每周六凌晨1点自动生成周线数据:
```bash
python -m backend_core.data_collectors.main
```

## 注意事项

### 1. 数据库连接
- 确保 PostgreSQL 数据库服务正在运行
- 检查 `.env` 文件中的数据库配置是否正确
- 默认连接: `postgresql://postgres:qidianspacetime@192.168.31.237:5446/stock_analysis`

### 2. 数据依赖
- 周线数据生成依赖于 `historical_quotes` 表中的日线数据
- 确保日线数据已经采集完整

### 3. 性能考虑
- 每100只股票输出一次进度日志
- 使用批量提交减少数据库交互
- 自动跳过无数据的股票以提高效率

## 下一步工作

1. **测试验证**: 确保数据库连接正常后，运行测试模式验证数据生成的正确性
2. **数据校验**: 对比生成的周线数据与实际周线数据，验证聚合逻辑的准确性
3. **API接口**: 如需要，可以在 `backend_api` 中添加周线数据查询接口
4. **前端展示**: 在前端页面中添加周线K线图展示功能

## 日志文件
- 生成日志: `weekly_generation.log`
- 操作记录: 存储在 `historical_collect_operation_logs` 表中

## 数据表结构
```sql
CREATE TABLE weekly_quotes (
    code TEXT,
    ts_code TEXT,
    name TEXT,
    market TEXT,
    date TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    amount REAL,
    change_percent REAL,
    change REAL,
    amplitude REAL,
    turnover_rate REAL,
    collected_source TEXT,
    collected_date TIMESTAMP,
    PRIMARY KEY (code, date)
);
```
