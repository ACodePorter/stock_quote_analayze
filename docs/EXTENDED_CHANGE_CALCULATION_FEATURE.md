# Tushare历史行情数据采集程序 - 扩展涨跌幅计算功能

## 功能概述

本次更新为tushare历史行情数据采集程序增加了10天和60天涨幅计算功能，在原有的5日涨跌幅基础上，扩展支持了更全面的涨跌幅分析。

## 新增功能

### 1. 扩展涨跌幅计算器 (ExtendedChangeCalculator)

- **文件位置**: `backend_core/data_collectors/tushare/extended_change_calculator.py`
- **功能**: 支持5日、10日、60日涨跌幅的批量计算
- **主要方法**:
  - `calculate_for_date()`: 为指定日期计算所有股票的扩展涨跌幅
  - `calculate_batch_for_date_range()`: 批量计算日期范围内的涨跌幅
  - `get_calculation_status()`: 查询计算状态和完成率

### 2. 数据库表结构更新

- **表名**: `historical_quotes`
- **新增字段**:
  - `five_day_change_percent`: 5日涨跌幅 (REAL)
  - `ten_day_change_percent`: 10日涨跌幅 (REAL)  
  - `sixty_day_change_percent`: 60日涨跌幅 (REAL)

### 3. 自动计算集成

- **集成位置**: `backend_core/data_collectors/tushare/historical.py`
- **触发时机**: 历史行情数据采集完成后自动执行
- **计算逻辑**: 
  - 5日涨跌幅 = (当前收盘价 - 5日前收盘价) / 5日前收盘价 × 100
  - 10日涨跌幅 = (当前收盘价 - 10日前收盘价) / 10日前收盘价 × 100
  - 60日涨跌幅 = (当前收盘价 - 60日前收盘价) / 60日前收盘价 × 100

## 使用方法

### 1. 数据库迁移

首次使用前需要运行数据库迁移脚本：

```bash
# 方法1: 使用独立脚本
python run_migrate_extended_change_fields.py

# 方法2: 直接运行迁移模块
python -m backend_core.data_collectors.tushare.migrate_extended_change_fields
```

### 2. 历史行情数据采集

运行历史行情数据采集程序，涨跌幅计算会自动执行：

```bash
python -m backend_core.data_collectors.tushare.main --type historical --date 20241201
```

### 3. 手动计算涨跌幅

如果需要手动计算特定日期的涨跌幅：

```python
from backend_core.database.db import SessionLocal
from backend_core.data_collectors.tushare.extended_change_calculator import ExtendedChangeCalculator

session = SessionLocal()
calculator = ExtendedChangeCalculator(session)

# 计算指定日期的涨跌幅
result = calculator.calculate_for_date("2024-12-01")
print(f"计算结果: {result}")

# 批量计算日期范围
batch_result = calculator.calculate_batch_for_date_range("2024-12-01", "2024-12-07")
print(f"批量计算结果: {batch_result}")

session.close()
```

### 4. 测试功能

运行测试脚本验证功能：

```bash
python test/test_extended_change_calculation.py
```

## 技术实现

### 1. 计算逻辑

- **数据要求**: 至少需要61天的历史数据才能计算60日涨跌幅
- **数据排序**: 按日期升序排列，确保时间序列的正确性
- **精度控制**: 涨跌幅保留2位小数
- **异常处理**: 对无效数据（如收盘价为0或负数）进行过滤

### 2. 性能优化

- **批量更新**: 使用SQL UPDATE语句批量更新数据库
- **事务管理**: 合理的事务提交频率，避免长时间锁定
- **错误恢复**: 支持部分失败的情况，记录详细的错误信息

### 3. 日志记录

- **操作日志**: 记录每次计算的操作类型、影响行数、状态等
- **错误日志**: 详细记录计算失败的原因和具体股票代码
- **统计信息**: 提供计算完成率、成功/失败数量等统计信息

## 数据验证

### 1. 计算状态查询

```python
# 查询指定日期的计算状态
status = calculator.get_calculation_status("2024-12-01")
print(f"计算状态: {status}")
```

返回结果示例：
```json
{
    "date": "2024-12-01",
    "total_records": 5000,
    "five_day": {
        "calculated": 4800,
        "pending": 200,
        "completion_rate": 96.0
    },
    "ten_day": {
        "calculated": 4700,
        "pending": 300,
        "completion_rate": 94.0
    },
    "sixty_day": {
        "calculated": 4500,
        "pending": 500,
        "completion_rate": 90.0
    }
}
```

### 2. 数据查询示例

```sql
-- 查询某日期的涨跌幅数据
SELECT code, name, five_day_change_percent, ten_day_change_percent, sixty_day_change_percent
FROM historical_quotes 
WHERE date = '2024-12-01' 
AND five_day_change_percent IS NOT NULL
ORDER BY five_day_change_percent DESC
LIMIT 10;
```

## 注意事项

1. **数据依赖**: 计算60日涨跌幅需要至少61天的历史数据
2. **计算顺序**: 建议先确保有足够的历史数据再进行计算
3. **性能考虑**: 大量数据计算时可能需要较长时间，建议在非高峰期执行
4. **数据一致性**: 确保历史数据的连续性和完整性

## 更新日志

- **2024-12-01**: 初始版本，支持5日、10日、60日涨跌幅计算
- **功能**: 扩展涨跌幅计算器、数据库迁移、自动集成、测试脚本
