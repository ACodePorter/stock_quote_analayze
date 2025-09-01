# 5日涨跌幅自动计算功能实现说明

## 📋 功能概述

在历史行情数据每日采集接口中集成了5日涨跌幅自动计算功能，用户无需再手动点击计算按钮，系统会在数据采集完成后自动计算并更新5日涨跌幅数据。

## 🎯 实现目标

- ✅ 历史行情数据采集完成后自动计算5日涨跌幅
- ✅ 支持批量计算和单日计算
- ✅ 完善的错误处理和日志记录
- ✅ 提供独立的手动计算工具
- ✅ 计算状态监控和查询

## 🏗️ 技术架构

### 1. 核心组件

#### 1.1 5日涨跌幅计算器 (`FiveDayChangeCalculator`)
- **位置**: `backend_core/data_collectors/tushare/five_day_change_calculator.py`
- **功能**: 核心计算逻辑，支持单日、批量、状态查询等操作
- **主要方法**:
  - `calculate_for_date()`: 为指定日期计算所有股票的5日涨跌幅
  - `calculate_batch_for_date_range()`: 批量计算日期范围
  - `get_calculation_status()`: 获取计算状态
  - `_calculate_single_stock_five_day_change()`: 单只股票计算

#### 1.2 历史行情采集器集成
- **位置**: `backend_core/data_collectors/tushare/historical.py`
- **修改**: 在数据采集完成后自动调用5日涨跌幅计算
- **特点**: 无缝集成，不影响原有采集流程

#### 1.3 独立计算脚本
- **位置**: `backend_core/data_collectors/tushare/calculate_five_day_change.py`
- **功能**: 支持命令行手动触发计算
- **模式**: 单日期、日期范围、最近N天、状态查询

### 2. 数据库设计

#### 2.1 字段结构
```sql
-- historical_quotes表新增字段
five_day_change_percent DECIMAL(8,2)  -- 5日涨跌幅百分比
```

#### 2.2 日志记录
```sql
-- historical_collect_operation_logs表记录计算日志
operation_type: 'five_day_change_calculation'
operation_desc: 包含计算统计信息
status: 'success' | 'partial_success' | 'error'
```

## 🔧 实现细节

### 1. 计算逻辑

#### 1.1 计算公式
```
5日涨跌幅 = (当前收盘价 - 5天前收盘价) / 5天前收盘价 × 100
```

#### 1.2 计算规则
- **时间定义**: 5个交易日（非自然日）
- **起始条件**: 从第6个交易日开始计算
- **数据要求**: 需要至少6天的历史数据
- **精度控制**: 结果保留2位小数
- **异常处理**: 处理除零、空值等异常情况

### 2. 自动集成流程

```python
# 历史行情数据采集完成后自动执行
if success_count > 0:
    try:
        self.logger.info("开始自动计算5日涨跌幅...")
        target_date = datetime.datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
        calculator = FiveDayChangeCalculator(session)
        calc_result = calculator.calculate_for_date(target_date)
        
        # 记录计算日志
        self._log_calculation_result(calc_result)
        
    except Exception as calc_error:
        self.logger.error(f"自动计算5日涨跌幅失败: {calc_error}")
        self._log_calculation_error(calc_error)
```

### 3. 错误处理机制

#### 3.1 计算异常处理
- 数据不足6天的股票跳过计算
- 收盘价无效的股票跳过计算
- 数据库操作异常回滚事务
- 详细的错误日志记录

#### 3.2 日志记录
- 成功/失败统计
- 详细错误信息
- 操作时间戳
- 影响记录数统计

## 📊 使用方法

### 1. 自动计算（推荐）

系统会在每日历史行情数据采集完成后自动计算5日涨跌幅，无需人工干预。

### 2. 手动计算

#### 2.1 命令行工具
```bash
# 计算指定日期的5日涨跌幅
python backend_core/data_collectors/tushare/calculate_five_day_change.py --mode date --date 2025-01-01

# 计算日期范围
python backend_core/data_collectors/tushare/calculate_five_day_change.py --mode range --start-date 2025-01-01 --end-date 2025-01-31

# 计算最近30天
python backend_core/data_collectors/tushare/calculate_five_day_change.py --mode recent --days 30

# 查看计算状态
python backend_core/data_collectors/tushare/calculate_five_day_change.py --mode status --date 2025-01-01
```

#### 2.2 编程接口
```python
from backend_core.data_collectors.tushare.five_day_change_calculator import FiveDayChangeCalculator
from backend_core.database.db import SessionLocal

session = SessionLocal()
calculator = FiveDayChangeCalculator(session)

# 计算单日
result = calculator.calculate_for_date("2025-01-01")

# 批量计算
result = calculator.calculate_batch_for_date_range("2025-01-01", "2025-01-31")

# 查看状态
status = calculator.get_calculation_status("2025-01-01")
```

### 3. 测试验证

运行集成测试脚本：
```bash
python test/test_five_day_change_integration.py
```

## 📈 性能优化

### 1. 数据库优化
- 批量更新减少数据库交互
- 事务管理确保数据一致性
- 索引优化提升查询性能

### 2. 计算优化
- 只计算需要更新的记录
- 内存友好的数据处理
- 并发安全的计算逻辑

### 3. 日志优化
- 异步日志记录
- 日志级别控制
- 日志文件轮转

## 🔍 监控和维护

### 1. 计算状态监控
```sql
-- 查看指定日期的计算状态
SELECT 
    COUNT(*) as total_records,
    COUNT(five_day_change_percent) as calculated_records,
    COUNT(*) - COUNT(five_day_change_percent) as pending_records,
    ROUND(COUNT(five_day_change_percent) * 100.0 / COUNT(*), 2) as completion_rate
FROM historical_quotes 
WHERE date = '2025-01-01';
```

### 2. 操作日志查询
```sql
-- 查看5日涨跌幅计算日志
SELECT 
    operation_desc,
    affected_rows,
    status,
    created_at
FROM historical_collect_operation_logs 
WHERE operation_type = 'five_day_change_calculation'
ORDER BY created_at DESC;
```

### 3. 错误排查
- 检查日志文件中的错误信息
- 验证数据库连接和权限
- 确认历史数据完整性

## 🚀 部署说明

### 1. 环境要求
- Python 3.7+
- PostgreSQL数据库
- 已安装项目依赖包

### 2. 数据库准备
确保`historical_quotes`表已添加`five_day_change_percent`字段：
```sql
-- 如果字段不存在，执行以下SQL
ALTER TABLE historical_quotes ADD COLUMN five_day_change_percent DECIMAL(8,2);
```

### 3. 配置检查
- 确认数据库连接配置正确
- 验证Tushare API token有效
- 检查日志目录权限

## 📝 更新日志

### v1.0.0 (2025-01-01)
- ✅ 实现5日涨跌幅自动计算功能
- ✅ 集成到历史行情数据采集流程
- ✅ 提供独立的手动计算工具
- ✅ 完善错误处理和日志记录
- ✅ 添加测试验证脚本

## 🔮 未来规划

### 1. 功能扩展
- 支持更多时间周期的涨跌幅计算（3日、10日等）
- 添加技术指标计算（MA、MACD等）
- 支持自定义计算公式

### 2. 性能优化
- 并行计算支持
- 缓存机制优化
- 增量计算优化

### 3. 监控增强
- 实时计算状态监控
- 计算性能指标统计
- 异常告警机制

## 📞 技术支持

如遇到问题，请检查：
1. 数据库连接和权限
2. 历史数据完整性
3. 日志文件中的错误信息
4. 系统资源使用情况

---

**注意**: 此功能已完全集成到现有的历史行情数据采集流程中，用户无需进行任何额外配置即可享受自动计算功能。
