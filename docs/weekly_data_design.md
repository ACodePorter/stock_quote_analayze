# A股周线数据采集系统设计文档

## 1. 需求分析

### 1.1 业务需求
- 为股票分析系统提供周线级别的K线数据
- 支持技术分析中的周线图表展示
- 提供周线级别的技术指标计算基础数据

### 1.2 功能需求
- **数据生成**: 基于日线数据自动生成周线数据
- **数据存储**: 将周线数据持久化到数据库
- **定时更新**: 每周自动更新最新的周线数据
- **历史回溯**: 支持批量生成历史周线数据
- **增量更新**: 支持增量更新，避免重复计算

### 1.3 非功能需求
- **性能**: 处理5000+股票的周线生成在10分钟内完成
- **准确性**: 周线数据计算准确，符合金融行业标准
- **可靠性**: 支持断点续传，异常情况下不丢失数据
- **可维护性**: 代码结构清晰，易于扩展和维护

## 2. 技术方案

### 2.1 方案选择

#### 方案A: 直接调用AKShare API获取周线数据
**优点**:
- 实现简单，直接调用API
- 数据来源可靠

**缺点**:
- 依赖外部API，可能受限于网络和API限制
- 无法自定义周线计算规则
- API可能不稳定或变更

#### 方案B: 基于日线数据生成周线数据 ✅ (采用)
**优点**:
- 完全自主可控，不依赖外部API
- 可以自定义计算规则
- 利用已有的日线数据，无需额外采集
- 性能可控，可以批量处理

**缺点**:
- 需要自己实现聚合逻辑
- 依赖日线数据的完整性

### 2.2 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    定时任务调度器                          │
│              (APScheduler - 每周六凌晨1点)                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              WeeklyDataGenerator                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  1. 获取股票列表                                    │  │
│  │  2. 查询日线数据 (historical_quotes)               │  │
│  │  3. 数据聚合 (pandas.resample)                     │  │
│  │  4. 计算技术指标                                    │  │
│  │  5. 保存周线数据 (weekly_quotes)                   │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   PostgreSQL 数据库                       │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │ historical_quotes│ ───▶ │  weekly_quotes   │        │
│  │   (日线数据)      │      │   (周线数据)      │        │
│  └──────────────────┘      └──────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### 2.3 数据流程

```
开始
  │
  ▼
获取股票列表
  │
  ▼
遍历每只股票
  │
  ├─▶ 查询日线数据 (start_date - 40天 to end_date)
  │     │
  │     ▼
  │   数据预处理
  │     │
  │     ├─▶ 转换为DataFrame
  │     ├─▶ 设置日期索引
  │     └─▶ 去除无效数据
  │     │
  │     ▼
  │   周线聚合 (resample('W-FRI'))
  │     │
  │     ├─▶ 开盘: first
  │     ├─▶ 最高: max
  │     ├─▶ 最低: min
  │     ├─▶ 收盘: last
  │     ├─▶ 成交量: sum
  │     └─▶ 成交额: sum
  │     │
  │     ▼
  │   计算技术指标
  │     │
  │     ├─▶ 涨跌幅 = (本周收盘 - 上周收盘) / 上周收盘 * 100
  │     ├─▶ 涨跌额 = 本周收盘 - 上周收盘
  │     └─▶ 振幅 = (本周最高 - 本周最低) / 上周收盘 * 100
  │     │
  │     ▼
  │   保存到数据库 (ON CONFLICT DO UPDATE)
  │     │
  └─────┘
  │
  ▼
记录操作日志
  │
  ▼
结束
```

## 3. 数据库设计

### 3.1 周线数据表 (weekly_quotes)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| code | TEXT | 股票代码 | PRIMARY KEY (1) |
| ts_code | TEXT | Tushare代码 (如: 000001.SZ) | |
| name | TEXT | 股票名称 | |
| market | TEXT | 市场 (SH/SZ) | |
| date | TEXT | 周线日期 (周五日期) | PRIMARY KEY (2) |
| open | REAL | 开盘价 | |
| high | REAL | 最高价 | |
| low | REAL | 最低价 | |
| close | REAL | 收盘价 | |
| volume | REAL | 成交量 | |
| amount | REAL | 成交额 | |
| change_percent | REAL | 涨跌幅 (%) | |
| change | REAL | 涨跌额 | |
| amplitude | REAL | 振幅 (%) | |
| turnover_rate | REAL | 换手率 (暂不计算) | |
| collected_source | TEXT | 数据来源 (generated_from_daily) | |
| collected_date | TIMESTAMP | 采集时间 | |

**索引设计**:
- 主键索引: (code, date)
- 建议添加: INDEX ON (date) - 用于按日期查询
- 建议添加: INDEX ON (code) - 用于按股票查询

### 3.2 数据来源表 (historical_quotes)

周线数据生成依赖此表的日线数据，需要确保日线数据的完整性。

### 3.3 操作日志表 (historical_collect_operation_logs)

记录每次周线数据生成的操作日志，便于追踪和审计。

## 4. 核心算法设计

### 4.1 周线聚合算法

使用 pandas 的 `resample` 方法进行时间序列重采样：

```python
weekly_df = df.resample('W-FRI').agg({
    'open': 'first',    # 周开盘 = 本周第一个交易日的开盘价
    'high': 'max',      # 周最高 = 本周所有交易日的最高价
    'low': 'min',       # 周最低 = 本周所有交易日的最低价
    'close': 'last',    # 周收盘 = 本周最后一个交易日的收盘价
    'volume': 'sum',    # 周成交量 = 本周所有交易日成交量之和
    'amount': 'sum'     # 周成交额 = 本周所有交易日成交额之和
})
```

**时间标记说明**:
- `W-FRI`: 表示以每周五作为周线的标记日期
- 即使周五没有交易，pandas 也会将该周数据标记为该周五的日期
- 符合金融行业的周线标记习惯

### 4.2 技术指标计算

#### 涨跌幅计算
```python
change_percent = (本周收盘价 - 上周收盘价) / 上周收盘价 * 100
```

使用 pandas 的 `pct_change()` 方法：
```python
weekly_df['change_percent'] = weekly_df['close'].pct_change() * 100
```

#### 涨跌额计算
```python
change = 本周收盘价 - 上周收盘价
```

使用 pandas 的 `diff()` 方法：
```python
weekly_df['change'] = weekly_df['close'].diff()
```

#### 振幅计算
```python
amplitude = (本周最高价 - 本周最低价) / 上周收盘价 * 100
```

实现：
```python
weekly_df['pre_close'] = weekly_df['close'].shift(1)
weekly_df['amplitude'] = (weekly_df['high'] - weekly_df['low']) / weekly_df['pre_close'] * 100
```

### 4.3 数据查询优化

为了准确计算涨跌幅等指标，需要获取上一周的收盘价。因此在查询日线数据时，自动向前扩展查询范围：

```python
query_start_date = start_date - timedelta(days=40)
```

这样可以确保：
- 即使请求的起始日期是某月1号，也能获取到上一周的数据
- 40天的缓冲足以覆盖各种节假日情况

## 5. 接口设计

### 5.1 类接口

#### WeeklyDataGenerator

```python
class WeeklyDataGenerator:
    """基于日线数据生成周线数据"""
    
    def __init__(self):
        """初始化生成器，建立数据库连接"""
        
    def get_stock_list(self) -> List[Dict[str, str]]:
        """获取股票列表"""
        
    def generate_single_stock_weekly_data(
        self, 
        stock_code: str, 
        start_date: str, 
        end_date: str
    ) -> bool:
        """生成单只股票的周线数据"""
        
    def generate_weekly_data(
        self, 
        start_date: str, 
        end_date: str, 
        stock_codes: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """批量生成周线数据"""
```

### 5.2 命令行接口

```bash
# 基本用法
python weekly_collector.py <start_date> <end_date>

# 参数说明
# start_date: 开始日期，格式 YYYY-MM-DD
# end_date: 结束日期，格式 YYYY-MM-DD

# 可选参数
--stocks CODE1 CODE2 ...  # 指定股票代码列表
--test                     # 测试模式，只处理前5只股票

# 示例
python weekly_collector.py 2025-01-01 2025-11-30
python weekly_collector.py 2025-01-01 2025-11-30 --test
python weekly_collector.py 2025-01-01 2025-11-30 --stocks 000001 600000
```

### 5.3 定时任务接口

```python
def generate_weekly_data():
    """定时任务函数，每周六凌晨1点执行"""
    # 自动生成过去14天的周线数据
    # 确保覆盖最新完成的一周
```

## 6. 异常处理设计

### 6.1 异常分类

| 异常类型 | 处理策略 | 影响范围 |
|---------|---------|---------|
| 数据库连接失败 | 记录错误日志，退出程序 | 全局 |
| 单只股票无数据 | 跳过该股票，继续处理 | 单股票 |
| 数据格式错误 | 记录错误，跳过该数据 | 单条记录 |
| 计算结果为NaN | 存储为NULL | 单个字段 |

### 6.2 容错机制

1. **数据库事务**: 每只股票的数据作为一个事务提交
2. **断点续传**: 记录已处理的股票，支持中断后继续
3. **重试机制**: 对于临时性错误，自动重试
4. **日志记录**: 详细记录每个步骤的执行情况

### 6.3 数据校验

```python
# 数据完整性校验
if df.empty:
    logger.warning(f"股票 {stock_code} 无数据")
    return True

# 数据有效性校验
weekly_df.dropna(subset=['open', 'close'], inplace=True)

# NaN值处理
data['change_percent'] = float(row['change_percent']) if pd.notna(row['change_percent']) else None
```

## 7. 性能优化设计

### 7.1 批量处理

- 按股票批量处理，每只股票一次性生成所有周线数据
- 使用 `ON CONFLICT DO UPDATE` 减少数据库交互

### 7.2 查询优化

```sql
-- 使用索引优化查询
SELECT date, open, high, low, close, volume, amount, name
FROM historical_quotes
WHERE code = :code 
  AND date >= :start_date 
  AND date <= :end_date
ORDER BY date ASC
```

### 7.3 内存优化

- 逐股票处理，避免一次性加载所有数据
- 及时释放不再使用的 DataFrame

### 7.4 进度监控

```python
# 每100只股票输出一次进度
if i % 100 == 0:
    logger.info(f"已处理 {i}/{len(stocks)} 只股票")
```

## 8. 测试方案

### 8.1 单元测试

```python
# 测试周线聚合逻辑
def test_weekly_aggregation():
    # 准备测试数据
    # 验证聚合结果
    
# 测试技术指标计算
def test_technical_indicators():
    # 验证涨跌幅、振幅计算
    
# 测试异常处理
def test_error_handling():
    # 验证各种异常情况的处理
```

### 8.2 集成测试

```bash
# 测试模式：处理前5只股票
python weekly_collector.py 2025-11-01 2025-11-30 --test

# 验证数据正确性
SELECT * FROM weekly_quotes WHERE code = '000001' ORDER BY date DESC LIMIT 10;
```

### 8.3 性能测试

- 测试处理5000只股票的总耗时
- 监控内存使用情况
- 验证数据库性能

## 9. 部署方案

### 9.1 环境要求

- Python 3.8+
- PostgreSQL 12+
- pandas 1.3+
- SQLAlchemy 1.4+

### 9.2 配置文件

`.env` 文件配置：
```ini
DB_TYPE=postgresql
DB_HOST=192.168.31.237
DB_PORT=5446
DB_NAME=stock_analysis
DB_USER=postgres
DB_PASSWORD=qidianspacetime
```

### 9.3 部署步骤

1. 确保数据库服务运行正常
2. 确保日线数据已采集完整
3. 运行测试模式验证功能
4. 启动定时任务调度器

```bash
# 1. 测试数据库连接
python -c "from backend_core.database.db import SessionLocal; SessionLocal()"

# 2. 测试模式运行
python backend_core/data_collectors/akshare/weekly_collector.py 2025-11-01 2025-11-30 --test

# 3. 启动定时任务
python -m backend_core.data_collectors.main
```

## 10. 监控与维护

### 10.1 日志监控

- 应用日志: `weekly_generation.log`
- 操作日志: `historical_collect_operation_logs` 表

### 10.2 数据质量监控

```sql
-- 检查周线数据完整性
SELECT 
    COUNT(DISTINCT code) as stock_count,
    MIN(date) as earliest_date,
    MAX(date) as latest_date,
    COUNT(*) as total_records
FROM weekly_quotes;

-- 检查异常数据
SELECT * FROM weekly_quotes 
WHERE close IS NULL OR open IS NULL;
```

### 10.3 定期维护

- 每月检查数据完整性
- 定期清理过期日志
- 监控数据库性能

## 11. 扩展性设计

### 11.1 支持其他周期

可以扩展支持月线、季线等：

```python
# 月线
monthly_df = df.resample('M').agg({...})

# 季线
quarterly_df = df.resample('Q').agg({...})
```

### 11.2 支持更多技术指标

- MACD
- KDJ
- RSI
- 布林带

### 11.3 支持其他市场

- 港股周线
- 美股周线
- 期货周线

## 12. 风险评估

| 风险 | 影响 | 概率 | 应对措施 |
|-----|------|------|---------|
| 日线数据不完整 | 高 | 中 | 增加数据完整性检查 |
| 数据库连接失败 | 高 | 低 | 增加重试机制 |
| 计算结果错误 | 高 | 低 | 增加数据校验 |
| 性能不达标 | 中 | 低 | 优化查询和批处理 |

## 13. 总结

本设计文档详细描述了A股周线数据采集系统的设计方案，采用"基于日线数据生成周线数据"的技术路线，具有以下特点：

- ✅ **自主可控**: 不依赖外部API
- ✅ **性能优异**: 批量处理，高效聚合
- ✅ **准确可靠**: 符合金融行业标准
- ✅ **易于维护**: 代码结构清晰，文档完善
- ✅ **可扩展性**: 支持扩展到其他周期和市场

该系统已完成开发并通过初步测试，待数据库环境就绪后即可投入生产使用。
