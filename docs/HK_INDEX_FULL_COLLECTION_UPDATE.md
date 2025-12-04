# 港股指数全量采集功能更新说明

## 更新概述

本次更新对港股指数数据采集功能进行了重大改进，实现了全量数据采集和分表存储。

## 主要变更

### 1. 数据库模型更新 (backend_api/models.py)

#### 新增表模型

**HKIndexBasicInfo** - 港股指数基础信息表
- `code`: 指数代码 (主键)
- `name`: 指数名称
- `english_name`: 英文名称
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### 修改表模型

**HKIndexRealtimeQuotes** - 港股指数实时行情表
- 修改主键：`(code, trade_date)` 联合主键
- 新增字段：`trade_date` - 交易日期，格式：YYYY-MM-DD
- 支持按日期存储历史实时行情数据

### 2. 数据采集器更新 (backend_core/data_collectors/akshare/hk_index_realtime.py)

#### 功能增强

1. **全量数据采集**
   - 从akshare获取所有港股指数数据（不仅限于4个主要指数）
   - 优先使用 `stock_hk_index_spot_em` 接口获取全量数据
   - 失败时自动切换到 `stock_hk_index_daily_sina` 接口获取主要指数

2. **分表存储**
   - 基础信息写入 `hk_index_basic_info` 表
   - 实时行情按日期写入 `hk_index_realtime_quotes` 表
   - 支持数据更新（使用 ON CONFLICT DO UPDATE）

3. **事务处理优化**
   - 使用批量提交减少事务次数
   - 改进错误处理和回滚机制
   - 记录详细的操作日志

### 3. 后端API更新 (backend_api/market_routes.py)

#### 查询逻辑优化

**get_hk_market_indices** 接口更新：
- 优先查询当前日期的行情数据
- 如果当前日期无数据，自动查询最新日期的数据
- 支持返回全量港股指数数据（不限于4个主要指数）

```python
# 查询逻辑
1. 查询当前日期 (YYYY-MM-DD) 的所有港股指数
2. 如果无数据，查询最新交易日期的数据
3. 返回所有查询到的指数数据
```

## 数据流程

```
1. 数据采集
   ↓
   从akshare获取全量港股指数数据
   ↓
2. 数据分类
   ├─ 基础信息 → hk_index_basic_info 表
   └─ 实时行情 → hk_index_realtime_quotes 表 (按日期)
   ↓
3. 数据存储
   ├─ 新数据：INSERT
   └─ 已存在：UPDATE
   ↓
4. API查询
   ├─ 查询当前日期数据
   └─ 无数据则查询最新日期
   ↓
5. 前端展示
   └─ 显示所有港股指数
```

## 表结构设计

### hk_index_basic_info (基础信息表)

| 字段 | 类型 | 说明 |
|------|------|------|
| code | TEXT (PK) | 指数代码 |
| name | TEXT | 指数名称 |
| english_name | TEXT | 英文名称 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### hk_index_realtime_quotes (实时行情表)

| 字段 | 类型 | 说明 |
|------|------|------|
| code | TEXT (PK) | 指数代码 |
| trade_date | TEXT (PK) | 交易日期 |
| name | TEXT | 指数名称 |
| price | REAL | 最新价 |
| change | REAL | 涨跌额 |
| pct_chg | REAL | 涨跌幅 |
| open | REAL | 开盘价 |
| pre_close | REAL | 昨收价 |
| high | REAL | 最高价 |
| low | REAL | 最低价 |
| volume | REAL | 成交量 |
| amount | REAL | 成交额 |
| update_time | TEXT | 更新时间 |
| collect_time | TEXT | 采集时间 |

## 优势

1. **数据完整性**
   - 采集全量港股指数数据，不限于主要指数
   - 按日期存储，保留历史数据

2. **数据一致性**
   - 基础信息和行情数据分表存储
   - 使用UPSERT机制避免重复数据

3. **查询效率**
   - 按日期分区存储，提高查询效率
   - 支持历史数据查询

4. **扩展性**
   - 支持添加更多港股指数
   - 支持历史数据分析

## 使用方法

### 手动采集

```bash
cd e:\wangxw\股票分析软件\编码\stock_quote_analayze
python test\test_hk_index_collection.py
```

### 定时采集

定时任务已集成到主数据采集程序中：
- 任务ID: `hk_index_realtime`
- 执行时间: 周一至周五，9-12点和13-16点，每小时的第5分钟和第35分钟

### API调用

```javascript
// 获取港股指数数据
const response = await authFetch(`${API_BASE_URL}/api/market/hk-indices`);
const result = await response.json();

// 返回数据格式
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
      "timestamp": "2025-12-03 13:00:00"
    },
    // ... 更多指数
  ]
}
```

## 注意事项

1. **网络依赖**
   - 数据采集依赖于akshare接口的可用性
   - 建议配置网络代理以提高稳定性

2. **数据更新**
   - 同一交易日的数据会被更新（不是追加）
   - 历史数据按日期保留

3. **错误处理**
   - 采集失败会记录到操作日志表
   - 支持自动重试和降级策略

## 相关文件

- `backend_api/models.py` - 数据库模型定义
- `backend_core/data_collectors/akshare/hk_index_realtime.py` - 港股指数采集器
- `backend_api/market_routes.py` - API路由
- `backend_core/data_collectors/main.py` - 定时任务配置
- `test/test_hk_index_collection.py` - 测试脚本

## 后续优化建议

1. 添加数据质量检查
2. 实现数据缓存机制
3. 支持指定日期范围查询
4. 添加数据统计分析功能
