# 周线数据系统快速开始指南

## 📋 目录

1. [系统概述](#系统概述)
2. [环境准备](#环境准备)
3. [快速开始](#快速开始)
4. [常见问题](#常见问题)
5. [相关文档](#相关文档)

## 系统概述

周线数据系统基于已有的日线数据，自动生成周线K线数据，用于技术分析和图表展示。

**核心特性**:
- ✅ 基于日线数据自动生成，无需外部API
- ✅ 每周自动更新，无需人工干预
- ✅ 支持历史数据批量生成
- ✅ 提供完整的API接口

## 环境准备

### 1. 系统要求

- **操作系统**: Windows / Linux / macOS
- **Python**: 3.8+
- **数据库**: PostgreSQL 12+

### 2. 依赖包

确保已安装以下Python包：

```bash
pip install pandas sqlalchemy psycopg2-binary
```

### 3. 数据库配置

在 `.env` 文件中配置数据库连接：

```ini
DB_TYPE=postgresql
DB_HOST=192.168.31.237
DB_PORT=5446
DB_NAME=stock_analysis
DB_USER=postgres
DB_PASSWORD=qidianspacetime
```

### 4. 数据准备

确保 `historical_quotes` 表中已有日线数据。可以通过以下SQL检查：

```sql
SELECT COUNT(*) FROM historical_quotes;
SELECT MIN(date), MAX(date) FROM historical_quotes;
```

## 快速开始

### 步骤1: 测试数据库连接

```bash
python -c "from backend_core.database.db import SessionLocal; print('数据库连接成功'); SessionLocal()"
```

如果看到"数据库连接成功"，说明配置正确。

### 步骤2: 测试模式运行

首次使用建议先运行测试模式，只处理前5只股票：

```bash
cd e:\wangxw\work\stock_quote_analayze
python backend_core/data_collectors/akshare/weekly_collector.py 2025-01-01 2025-11-30 --test
```

**预期输出**:
```
2025-11-30 15:00:00,000 - INFO - 开始生成周线数据: 2025-01-01 到 2025-11-30
2025-11-30 15:00:01,000 - INFO - 准备处理 5 只股票
2025-11-30 15:00:05,000 - INFO - 周线数据生成完成: {'total': 5, 'success': 5, 'failed': 0, 'generated_rows': 50}
```

### 步骤3: 验证生成的数据

使用SQL查询验证数据是否正确生成：

```sql
-- 查看生成的周线数据总数
SELECT COUNT(*) FROM weekly_quotes;

-- 查看某只股票的周线数据
SELECT * FROM weekly_quotes 
WHERE code = '000001' 
ORDER BY date DESC 
LIMIT 10;

-- 检查数据完整性
SELECT 
    COUNT(DISTINCT code) as stock_count,
    MIN(date) as earliest_week,
    MAX(date) as latest_week,
    COUNT(*) as total_weeks
FROM weekly_quotes;
```

### 步骤4: 生成完整历史数据

测试通过后，生成所有股票的周线数据：

```bash
# 生成2025年的周线数据
python backend_core/data_collectors/akshare/weekly_collector.py 2025-01-01 2025-11-30

# 或者生成更长时间范围的数据
python backend_core/data_collectors/akshare/weekly_collector.py 2020-01-01 2025-11-30
```

**注意**: 
- 首次生成可能需要较长时间（取决于股票数量和时间范围）
- 建议从近期数据开始，逐步扩展到历史数据

### 步骤5: 启动定时任务

启动定时任务调度器，实现每周自动更新：

```bash
python -m backend_core.data_collectors.main
```

定时任务会在每周六凌晨1点自动生成最新的周线数据。

## 使用示例

### 示例1: 生成指定股票的周线数据

```bash
python backend_core/data_collectors/akshare/weekly_collector.py 2025-01-01 2025-11-30 --stocks 000001 600000 000002
```

### 示例2: 查询周线数据

```python
from backend_core.database.db import SessionLocal
from sqlalchemy import text

session = SessionLocal()

# 查询某只股票的周线数据
query = text("""
    SELECT date, open, high, low, close, volume, change_percent
    FROM weekly_quotes
    WHERE code = :code
    ORDER BY date DESC
    LIMIT 20
""")

result = session.execute(query, {'code': '000001'})
for row in result:
    print(f"日期: {row[0]}, 开盘: {row[1]}, 收盘: {row[4]}, 涨跌幅: {row[6]}%")

session.close()
```

### 示例3: 通过API获取周线数据

```bash
# 启动API服务
python start_backend_api.py

# 调用API
curl "http://localhost:5000/api/quotes/weekly/000001?start_date=2025-01-01&end_date=2025-11-30"
```

## 常见问题

### Q1: 数据库连接失败

**错误信息**: `Connection refused (0x0000274D/10061)`

**解决方法**:
1. 检查PostgreSQL服务是否运行
2. 验证数据库配置（主机、端口、用户名、密码）
3. 检查防火墙设置

```bash
# Windows检查PostgreSQL服务
sc query postgresql-x64-12

# 启动服务
sc start postgresql-x64-12
```

### Q2: 没有生成数据

**可能原因**:
1. 日线数据不存在
2. 日期范围内没有交易数据

**解决方法**:
```sql
-- 检查日线数据
SELECT COUNT(*) FROM historical_quotes WHERE code = '000001';

-- 检查日期范围
SELECT MIN(date), MAX(date) FROM historical_quotes WHERE code = '000001';
```

### Q3: 涨跌幅为NULL

**原因**: 第一周的数据无法计算涨跌幅（缺少上一周的收盘价）

**这是正常现象**，可以忽略或在查询时过滤：

```sql
SELECT * FROM weekly_quotes 
WHERE code = '000001' 
  AND change_percent IS NOT NULL
ORDER BY date DESC;
```

### Q4: 生成速度慢

**优化建议**:
1. 缩小日期范围，分批生成
2. 使用 `--stocks` 参数只生成部分股票
3. 检查数据库性能，添加索引

```sql
-- 添加索引优化查询
CREATE INDEX IF NOT EXISTS idx_historical_quotes_code_date 
ON historical_quotes(code, date);

CREATE INDEX IF NOT EXISTS idx_weekly_quotes_code_date 
ON weekly_quotes(code, date);
```

### Q5: 如何重新生成数据

如果需要重新生成某只股票的周线数据：

```sql
-- 删除旧数据
DELETE FROM weekly_quotes WHERE code = '000001';

-- 重新生成
python backend_core/data_collectors/akshare/weekly_collector.py 2025-01-01 2025-11-30 --stocks 000001
```

或者直接运行（会自动覆盖）：

```bash
python backend_core/data_collectors/akshare/weekly_collector.py 2025-01-01 2025-11-30 --stocks 000001
```

## 数据验证

### 验证周线数据的正确性

```python
import pandas as pd
from backend_core.database.db import SessionLocal
from sqlalchemy import text

def validate_weekly_data(stock_code, week_date):
    """验证某一周的数据是否正确"""
    session = SessionLocal()
    
    # 获取周线数据
    weekly_query = text("""
        SELECT date, open, high, low, close, volume, amount
        FROM weekly_quotes
        WHERE code = :code AND date = :date
    """)
    weekly = session.execute(weekly_query, {
        'code': stock_code,
        'date': week_date
    }).fetchone()
    
    # 获取该周的日线数据
    # 假设week_date是周五，向前推7天
    week_start = pd.to_datetime(week_date) - pd.Timedelta(days=6)
    daily_query = text("""
        SELECT date, open, high, low, close, volume, amount
        FROM historical_quotes
        WHERE code = :code 
          AND date >= :start_date 
          AND date <= :end_date
        ORDER BY date ASC
    """)
    daily_data = session.execute(daily_query, {
        'code': stock_code,
        'start_date': week_start.strftime('%Y-%m-%d'),
        'end_date': week_date
    }).fetchall()
    
    if not daily_data:
        print(f"该周没有日线数据")
        return
    
    # 验证
    print(f"周线数据: {weekly}")
    print(f"日线数据条数: {len(daily_data)}")
    print(f"周开盘应为: {daily_data[0][1]} (实际: {weekly[1]})")
    print(f"周收盘应为: {daily_data[-1][4]} (实际: {weekly[4]})")
    print(f"周最高应为: {max(d[2] for d in daily_data)} (实际: {weekly[2]})")
    print(f"周最低应为: {min(d[3] for d in daily_data)} (实际: {weekly[3]})")
    print(f"周成交量应为: {sum(d[5] for d in daily_data)} (实际: {weekly[5]})")
    
    session.close()

# 使用示例
validate_weekly_data('000001', '2025-11-28')
```

## 监控与维护

### 查看生成日志

```bash
# 查看日志文件
tail -f weekly_generation.log

# 或在Windows上
type weekly_generation.log
```

### 查看操作记录

```sql
SELECT * FROM historical_collect_operation_logs
WHERE operation_type = 'generate_weekly_from_daily'
ORDER BY created_at DESC
LIMIT 10;
```

### 定期检查数据完整性

建议每月运行一次数据完整性检查：

```sql
-- 检查是否有缺失的周
WITH RECURSIVE weeks AS (
    SELECT DATE '2025-01-05' AS week_date  -- 第一个周五
    UNION ALL
    SELECT week_date + INTERVAL '7 days'
    FROM weeks
    WHERE week_date < CURRENT_DATE
)
SELECT w.week_date, COUNT(q.date) as stock_count
FROM weeks w
LEFT JOIN weekly_quotes q ON w.week_date = q.date
GROUP BY w.week_date
HAVING COUNT(q.date) < 5000  -- 假设有5000只股票
ORDER BY w.week_date DESC;
```

## 性能优化建议

### 1. 批量生成策略

对于大量历史数据，建议分批生成：

```bash
# 按年份分批
python weekly_collector.py 2020-01-01 2020-12-31
python weekly_collector.py 2021-01-01 2021-12-31
python weekly_collector.py 2022-01-01 2022-12-31
python weekly_collector.py 2023-01-01 2023-12-31
python weekly_collector.py 2024-01-01 2024-12-31
python weekly_collector.py 2025-01-01 2025-11-30
```

### 2. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_historical_quotes_code_date ON historical_quotes(code, date);
CREATE INDEX idx_weekly_quotes_date ON weekly_quotes(date);

-- 定期清理和优化
VACUUM ANALYZE weekly_quotes;
VACUUM ANALYZE historical_quotes;
```

### 3. 并发处理

如果需要更快的处理速度，可以修改代码支持多进程：

```python
from multiprocessing import Pool

def generate_for_stocks_batch(stock_codes):
    generator = WeeklyDataGenerator()
    return generator.generate_weekly_data(start_date, end_date, stock_codes)

# 将股票列表分成多个批次
batch_size = 100
stock_batches = [stocks[i:i+batch_size] for i in range(0, len(stocks), batch_size)]

# 并发处理
with Pool(processes=4) as pool:
    results = pool.map(generate_for_stocks_batch, stock_batches)
```

## 相关文档

- 📘 [系统设计文档](./weekly_data_design.md) - 详细的技术设计
- 📗 [API接口文档](./weekly_data_api.md) - API使用说明
- 📙 [实施总结文档](./weekly_data_implementation.md) - 实施细节

## 技术支持

如遇到问题，请：

1. 查看日志文件 `weekly_generation.log`
2. 检查数据库连接和数据完整性
3. 参考常见问题部分
4. 查阅相关设计文档

---

**最后更新**: 2025-11-30  
**版本**: 1.0.0
