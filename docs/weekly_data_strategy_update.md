# 周线数据采集策略调整说明

## 策略变更

### 原策略
- **执行时间**: 每周六凌晨 1:00
- **数据范围**: 生成过去14天的周线数据
- **更新频率**: 每周一次

### 新策略 ✅
- **执行时间**: 每日收盘后晚上 18:00 (工作日)
- **数据范围**: 只更新当前周的数据
- **更新频率**: 每日一次
- **更新方式**: 覆盖写入

## 策略优势

### 1. 实时性更强
- 每天更新当前周的数据，反映最新市场情况
- 用户可以看到本周截至今日的K线数据
- 无需等到周末才能看到本周数据

### 2. 数据更准确
- 每日更新确保数据与日线数据保持同步
- 避免周末一次性处理可能出现的数据遗漏

### 3. 资源利用更合理
- 每天只处理当前周的数据，计算量小
- 避免周末集中处理大量历史数据

## 技术实现

### 1. 新增方法

在 `WeeklyDataGenerator` 类中新增了 `generate_current_week_data` 方法：

```python
def generate_current_week_data(self, stock_codes: Optional[List[str]] = None) -> Dict[str, any]:
    """
    生成当前周的周线数据（每日更新模式）
    计算本周一到今天的数据，覆盖写入
    """
    try:
        from datetime import datetime, timedelta
        
        today = datetime.now()
        
        # 计算本周一的日期
        days_since_monday = today.weekday()  # 0=周一, 6=周日
        monday = today - timedelta(days=days_since_monday)
        
        # 为了计算涨跌幅，需要获取上周的数据
        # 向前扩展40天确保能获取到上周收盘价
        start_date = (monday - timedelta(days=40)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        logger.info(f"开始生成当前周线数据: 本周一 {monday.strftime('%Y-%m-%d')} 到今天 {end_date}")
        
        # 调用通用生成方法
        result = self.generate_weekly_data(start_date, end_date, stock_codes)
        
        logger.info(f"当前周线数据生成完成: {result}")
        return result
        
    except Exception as e:
        logger.error(f"生成当前周线数据失败: {e}")
        return {'total': 0, 'success': 0, 'failed': 1}
```

### 2. 定时任务调整

在 `main.py` 中修改了定时任务配置：

```python
# 周线数据生成任务，每日收盘后晚上6点更新当前周数据
scheduler.add_job(
    generate_weekly_data,
    'cron',
    day_of_week='mon-fri',
    hour=18,
    minute=0,
    id='generate_weekly',
)
```

**变更点**:
- `day_of_week`: 从 `sat` 改为 `mon-fri`
- `hour`: 从 `1` 改为 `18`
- 函数内部调用 `generate_current_week_data()` 而不是 `generate_weekly_data(start_date, end_date)`

## 数据处理逻辑

### 当前周的定义
- **周一到周五**: 从本周一到今天
- **周六周日**: 不执行（因为没有交易）

### 数据计算范围
```
查询范围: 本周一 - 40天 到 今天
生成范围: 本周一 到 今天（但只保存本周五的数据）
```

**为什么向前查询40天？**
- 为了准确计算涨跌幅，需要上周的收盘价
- 40天的缓冲足以覆盖各种节假日情况

### 数据覆盖机制

使用 `ON CONFLICT DO UPDATE` 实现覆盖写入：

```sql
INSERT INTO weekly_quotes
(code, ts_code, name, market, date, open, high, low, close, 
 volume, amount, change_percent, change, amplitude, turnover_rate, 
 collected_source, collected_date)
VALUES (...)
ON CONFLICT(code, date) DO UPDATE SET
open=excluded.open, high=excluded.high, low=excluded.low, close=excluded.close,
volume=excluded.volume, amount=excluded.amount, change_percent=excluded.change_percent,
change=excluded.change, amplitude=excluded.amplitude, collected_date=excluded.collected_date
```

## 使用示例

### 手动执行当前周数据生成

```bash
# 方式1: 直接调用新方法（推荐）
python -c "from backend_core.data_collectors.akshare.weekly_collector import WeeklyDataGenerator; WeeklyDataGenerator().generate_current_week_data()"

# 方式2: 使用命令行工具（会生成更多数据）
python backend_core/data_collectors/akshare/weekly_collector.py 2025-11-24 2025-11-30
```

### 查询当前周数据

```sql
-- 查看当前周的数据（假设今天是周三）
SELECT * FROM weekly_quotes 
WHERE code = '000001' 
  AND date >= DATE_TRUNC('week', CURRENT_DATE)
ORDER BY date DESC;

-- 查看最新的周线数据
SELECT * FROM weekly_quotes 
WHERE code = '000001' 
ORDER BY date DESC 
LIMIT 1;
```

## 数据展示效果

### 周一
- 显示本周一的数据（开盘=周一开盘，收盘=周一收盘）

### 周二
- 更新为周一+周二的数据（开盘=周一开盘，收盘=周二收盘）

### 周三
- 更新为周一+周二+周三的数据（开盘=周一开盘，收盘=周三收盘）

### 周四
- 更新为周一到周四的数据

### 周五
- 更新为完整一周的数据（开盘=周一开盘，收盘=周五收盘）

### 周六、周日
- 保持周五的数据不变（不执行更新）

## 注意事项

### 1. 节假日处理
- 如果周一是节假日，本周一的日期会自动调整为本周第一个交易日
- pandas 的 `resample('W-FRI')` 会自动处理

### 2. 数据一致性
- 每天晚上6点更新，确保日线数据已经采集完成
- 建议日线数据采集时间在下午4:30之前完成

### 3. 性能考虑
- 每天只处理当前周的数据，性能开销很小
- 预计处理5000只股票需要5-10分钟

### 4. 历史数据
- 历史周线数据仍需要手动生成
- 使用命令行工具生成历史数据：
  ```bash
  python backend_core/data_collectors/akshare/weekly_collector.py 2020-01-01 2025-11-30
  ```

## 监控建议

### 1. 日志监控
每天检查日志，确保任务正常执行：

```bash
# 查看最新日志
tail -f weekly_generation.log

# 查看今天的日志
grep "$(date +%Y-%m-%d)" weekly_generation.log
```

### 2. 数据完整性检查

```sql
-- 检查今天是否更新了数据
SELECT 
    COUNT(DISTINCT code) as stock_count,
    MAX(collected_date) as latest_update
FROM weekly_quotes
WHERE date = DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '4 days';  -- 本周五

-- 如果今天是周三，应该能看到本周五的数据（但数据是周一到周三的聚合）
```

### 3. 异常告警
建议设置告警机制：
- 如果任务执行失败，发送邮件或短信通知
- 如果生成的股票数量异常（如少于4000只），发送告警

## 回滚方案

如果新策略出现问题，可以快速回滚到原策略：

### 1. 修改定时任务

```python
# 恢复为每周六执行
scheduler.add_job(
    generate_weekly_data,
    'cron',
    day_of_week='sat',
    hour=1,
    minute=0,
    id='generate_weekly',
)
```

### 2. 修改任务函数

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

## 总结

新策略的核心优势是**实时性**和**准确性**，通过每日更新当前周的数据，用户可以实时看到本周的K线走势，而不需要等到周末。这对于技术分析和决策支持非常重要。

---

**生效日期**: 2025-11-30  
**版本**: 2.0.0  
**状态**: 已实施 ✅
