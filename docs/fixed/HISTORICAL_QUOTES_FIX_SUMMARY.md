# Historical Quotes 表修复总结

## 问题描述

生产环境的历史数据同步出现以下错误：

```
[SQL: INSERT INTO historical_quotes ... ON CONFLICT (code, date) DO UPDATE SET ...]
[parameters: {'code': '920799', ...}]
(Background on this error at: https://sqlalche.me/e/20/2j85)
2025-08-04 13:32:19,345 ERROR 采集单条数据失败: (psycopg2.errors.InFailedSqlTransaction) 错误: 当前事务被终止, 事务块结束之前的查询被忽略
```

## 问题分析

1. **主要问题**: `historical_quotes` 表缺少主键约束，导致 `ON CONFLICT` 操作失败
2. **次要问题**: 缺少性能优化索引
3. **根本原因**: 从SQLite迁移到PostgreSQL时，约束和索引没有正确创建

## 修复方案

### 1. Python修复脚本

**文件**: `fix_historical_quotes_table.py`

**功能**:
- 检查表结构和约束
- 删除重复数据
- 删除旧约束（SQLite迁移遗留）
- 添加主键约束 `(code, date)`
- 创建性能优化索引
- 更新表统计信息
- 测试ON CONFLICT插入操作

### 2. SQL修复脚本

**文件**: `database/fix_historical_quotes_table.sql`

**功能**: 提供手动执行的SQL语句，包含所有修复步骤

## 修复结果

### 修复前状态
- ❌ 缺少主键约束
- ❌ 缺少性能索引
- ❌ ON CONFLICT操作失败

### 修复后状态
- ✅ 主键约束: `historical_quotes_pkey PRIMARY KEY (code, date)`
- ✅ 性能索引:
  - `idx_historical_quotes_code`: 股票代码索引
  - `idx_historical_quotes_date`: 日期索引
  - `idx_historical_quotes_collected_date`: 采集时间索引
- ✅ ON CONFLICT操作正常

## 执行步骤

### 1. 运行Python脚本（推荐）
```bash
python fix_historical_quotes_table.py
```

### 2. 手动执行SQL（备选）
```bash
psql -h 192.168.31.237 -p 5446 -U postgres -d stock_analysis -f database/fix_historical_quotes_table.sql
```

## 验证方法

### 1. 检查约束
```sql
SELECT conname, contype, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'historical_quotes'::regclass;
```

### 2. 检查索引
```sql
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'historical_quotes';
```

### 3. 测试插入
```sql
INSERT INTO historical_quotes (
    code, name, market, date, open, high, low, close, 
    volume, amount, change_percent, collected_source
) VALUES (
    '000001', '平安银行', 'SZ', '20250801', 10.50, 10.80, 10.20, 10.60,
    1000000, 10600000, 2.5, 'test'
) ON CONFLICT (code, date) DO UPDATE SET
    name = EXCLUDED.name,
    market = EXCLUDED.market,
    open = EXCLUDED.open,
    high = EXCLUDED.high,
    low = EXCLUDED.low,
    close = EXCLUDED.close,
    volume = EXCLUDED.volume,
    amount = EXCLUDED.amount,
    change_percent = EXCLUDED.change_percent,
    collected_source = EXCLUDED.collected_source;
```

## 生产环境建议

### 1. 监控和维护
- 定期监控索引使用情况
- 定期清理历史数据
- 监控插入性能
- 考虑分区表优化大数据量

### 2. 性能优化
- 监控慢查询
- 定期更新表统计信息 (`ANALYZE historical_quotes`)
- 考虑批量插入减少事务冲突

### 3. 数据质量
- 定期检查重复数据
- 验证数据完整性
- 监控数据采集日志

## 相关文件

1. **修复脚本**:
   - `fix_historical_quotes_table.py` - Python修复脚本
   - `database/fix_historical_quotes_table.sql` - SQL修复脚本

2. **检查脚本**:
   - `check_historical_quotes_table.py` - 表结构检查脚本

3. **文档**:
   - `HISTORICAL_QUOTES_FIX_SUMMARY.md` - 本总结文档

## 注意事项

1. **备份**: 执行修复前建议备份数据库
2. **停机时间**: 修复过程可能需要几分钟，建议在低峰期执行
3. **回滚**: 如果出现问题，可以使用备份恢复
4. **测试**: 修复后建议在测试环境验证功能正常

## 联系信息

如有问题，请检查：
1. 数据采集代码的事务管理
2. 并发访问控制
3. 数据库连接池配置
4. 网络连接稳定性 