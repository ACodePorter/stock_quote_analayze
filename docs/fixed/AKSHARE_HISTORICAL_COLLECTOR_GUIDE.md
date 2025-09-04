# Akshare历史数据采集程序使用说明

## 🎯 程序概述

`historical_collector.py` 是一个使用akshare库采集A股历史行情数据的程序，支持指定日期范围批量采集所有股票的历史数据。

## 📋 功能特性

### 1. 数据源
- **数据接口**: akshare.stock_zh_a_hist
- **数据格式**: 前复权数据
- **股票范围**: 从stock_basic_info表获取股票列表

### 2. 核心功能
- ✅ 支持指定日期范围采集
- ✅ 自动跳过已存在的数据
- ✅ 批量采集所有股票或指定股票
- ✅ 重试机制和错误处理
- ✅ 详细的日志记录
- ✅ 采集结果统计

### 3. 数据字段
采集的数据包含以下字段：
- 股票代码、名称、市场
- 开盘价、最高价、最低价、收盘价
- 前收盘价、成交量、成交额
- 涨跌幅、涨跌额、振幅、换手率
- 采集来源、采集时间

## 🚀 使用方法

### 1. 命令行使用

#### 基本用法
```bash
# 采集指定日期范围的所有股票
python backend_core/data_collectors/akshare/historical_collector.py 2025-08-01 2025-09-03

# 采集指定股票
python backend_core/data_collectors/akshare/historical_collector.py 2025-08-01 2025-09-03 --stocks 000001 000002 000858

# 测试模式（只采集前5只股票）
python backend_core/data_collectors/akshare/historical_collector.py 2025-08-01 2025-09-03 --test
```

#### 参数说明
- `start_date`: 开始日期 (YYYY-MM-DD格式)
- `end_date`: 结束日期 (YYYY-MM-DD格式)
- `--stocks`: 指定股票代码列表（可选）
- `--test`: 测试模式，只采集前5只股票（可选）

### 2. 程序化使用

```python
from backend_core.data_collectors.akshare.historical_collector import AkshareHistoricalCollector

# 创建采集器
collector = AkshareHistoricalCollector()

# 采集所有股票
result = collector.collect_historical_data("2025-08-01", "2025-09-03")

# 采集指定股票
result = collector.collect_historical_data("2025-08-01", "2025-09-03", ["000001", "000002"])

# 查看结果
print(f"总计股票: {result['total']}")
print(f"成功采集: {result['success']}")
print(f"采集失败: {result['failed']}")
print(f"新增数据: {result['collected']} 条")
print(f"跳过数据: {result['skipped']} 条")
```

## 📊 输出结果

### 1. 控制台输出
```
2025-09-04 10:45:23,687 - INFO - 开始批量采集历史行情数据: 2025-08-01 到 2025-09-03
2025-09-04 10:45:23,714 - INFO - 从数据库获取到 5417 只股票
2025-09-04 10:45:23,715 - INFO - 准备采集 5417 只股票的历史数据
2025-09-04 10:45:23,716 - INFO - 进度: 1/5417 - 采集股票 000001 (平安银行)
2025-09-04 10:45:25,123 - INFO - 股票 000001 采集到 23 条数据
2025-09-04 10:45:25,456 - INFO - 股票 000001 处理完成: 新增 23 条，跳过 0 条
...
2025-09-04 10:45:45,789 - INFO - 批量采集完成:
2025-09-04 10:45:45,790 - INFO -   - 总计股票: 5417
2025-09-04 10:45:45,791 - INFO -   - 成功采集: 5410
2025-09-04 10:45:45,792 - INFO -   - 采集失败: 7
2025-09-04 10:45:45,793 - INFO -   - 新增数据: 124591 条
2025-09-04 10:45:45,794 - INFO -   - 跳过数据: 0 条
```

### 2. 日志文件
程序会生成 `akshare_historical_collect.log` 日志文件，包含详细的采集过程信息。

### 3. 数据库日志
采集结果会记录到 `historical_collect_operation_logs` 表中。

## ⚙️ 配置说明

### 1. 数据库配置
程序使用 `backend_core.database.db.SessionLocal` 连接数据库，确保数据库配置正确。

### 2. 日志配置
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('akshare_historical_collect.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

### 3. 重试配置
- 最大重试次数: 3次
- 重试间隔: 递增延迟 (2秒, 4秒, 6秒)
- 请求间隔: 0.5-1.5秒随机延迟

## 🔧 测试验证

### 1. 运行测试脚本
```bash
python test/test_akshare_historical_collector.py
```

### 2. 测试内容
- 数据库连接检查
- akshare可用性检查
- 股票列表获取测试
- 单只股票采集测试
- 批量采集测试

## ⚠️ 注意事项

### 1. 数据重复处理
- 程序会自动检查已存在的数据
- 已存在的交易日数据会被跳过
- 不会重复插入相同的数据

### 2. 网络请求限制
- 添加了随机延迟避免请求过于频繁
- 建议在非交易时间进行大批量采集
- 避免对数据源造成过大压力

### 3. 错误处理
- 单只股票失败不影响其他股票采集
- 详细的错误日志记录
- 支持手动重试失败的股票

### 4. 性能考虑
- 大批量采集可能需要较长时间
- 建议分批采集或使用测试模式验证
- 可以根据需要调整请求间隔

## 📈 性能优化建议

### 1. 分批采集
```python
# 分批处理大量股票
all_stocks = collector.get_stock_list()
batch_size = 100

for i in range(0, len(all_stocks), batch_size):
    batch_stocks = all_stocks[i:i+batch_size]
    stock_codes = [stock['code'] for stock in batch_stocks]
    result = collector.collect_historical_data("2025-08-01", "2025-09-03", stock_codes)
    print(f"批次 {i//batch_size + 1} 完成")
```

### 2. 多进程采集
对于大量数据采集，可以考虑使用多进程并行处理，但需要注意：
- 数据库连接池配置
- 网络请求频率控制
- 错误处理和日志同步

## 🐛 常见问题

### 1. akshare连接失败
- 检查网络连接
- 确认akshare版本兼容性
- 尝试更新akshare: `pip install --upgrade akshare`

### 2. 数据库连接失败
- 检查数据库配置
- 确认数据库服务运行状态
- 验证数据库权限

### 3. 数据采集失败
- 检查股票代码格式
- 确认日期范围有效性
- 查看详细错误日志

### 4. 内存不足
- 减少批量处理数量
- 增加垃圾回收
- 使用分批处理

## 📞 技术支持

如果遇到问题，请：
1. 查看日志文件获取详细错误信息
2. 运行测试脚本验证环境配置
3. 检查网络连接和数据库状态
4. 参考常见问题解决方案

---

**程序版本**: 1.0.0  
**创建时间**: 2025-09-04  
**适用环境**: Python 3.7+, akshare, PostgreSQL
