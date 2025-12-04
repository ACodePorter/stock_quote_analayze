# 港股指数实时行情数据采集功能

## 功能概述

本次更新增加了港股指数实时行情数据采集功能，实现了从akshare接口获取港股指数数据并存储到数据库，前端页面从数据库读取数据而不是直连akshare接口。

## 主要变更

### 1. 数据库模型 (backend_api/models.py)

新增两个数据库表模型：

- **HKIndexRealtimeQuotes**: 港股指数实时行情表
  - code: 指数代码 (主键)
  - name: 指数名称
  - price: 最新价
  - change: 涨跌额
  - pct_chg: 涨跌幅
  - open, high, low, pre_close: 开盘价、最高价、最低价、昨收价
  - volume, amount: 成交量、成交额
  - update_time, collect_time: 更新时间、采集时间

- **HKIndexHistoricalQuotes**: 港股指数历史行情表
  - code, date: 指数代码、日期 (联合主键)
  - name: 指数名称
  - open, high, low, close: 开盘价、最高价、最低价、收盘价
  - volume, amount: 成交量、成交额
  - change, pct_chg: 涨跌额、涨跌幅
  - collected_source, collected_date: 采集来源、采集日期

### 2. 数据采集器 (backend_core/data_collectors/akshare/hk_index_realtime.py)

新增 **HKIndexRealtimeCollector** 类：

- 从akshare获取港股指数数据（支持多个数据源）
- 支持的指数：
  - HSI: 恒生指数
  - HSTECH: 恒生科技指数
  - HSCI: 恒生综合指数
  - HSCEI: 恒生中国企业指数
- 优先使用 `stock_hk_index_spot_em` 接口
- 失败时自动切换到 `stock_hk_index_daily_sina` 接口
- 数据存储到 `hk_index_realtime_quotes` 表

### 3. 后端API (backend_api/market_routes.py)

修改 **get_hk_market_indices** 接口：

- 从数据库 `hk_index_realtime_quotes` 表读取数据
- 不再直连akshare接口
- 返回格式与前端期望一致

### 4. 定时任务 (backend_core/data_collectors/main.py)

新增定时采集任务：

- 任务ID: `hk_index_realtime`
- 执行时间: 周一至周五，9-12点和13-16点，每小时的第5分钟和第35分钟
- 执行函数: `collect_hk_index_realtime()`

## 使用方法

### 1. 手动测试采集功能

```bash
cd e:\wangxw\股票分析软件\编码\stock_quote_analayze
python test\test_hk_index_collection.py
```

### 2. 启动定时采集服务

定时采集服务已集成到主数据采集程序中，会自动运行。

### 3. 前端调用

前端通过以下API获取港股指数数据：

```javascript
const response = await authFetch(`${API_BASE_URL}/api/market/hk-indices`);
const result = await response.json();
```

返回数据格式：

```json
{
  "success": true,
  "data": [
    {
      "code": "HSI",
      "name": "恒生指数",
      "current": 18000.00,
      "change": 100.00,
      "change_percent": 0.56,
      "volume": 0,
      "timestamp": "2025-12-03 10:30:00"
    },
    ...
  ]
}
```

## 数据流程

1. **数据采集**: 定时任务调用 `HKIndexRealtimeCollector.collect_realtime_quotes()`
2. **数据存储**: 采集到的数据写入 `hk_index_realtime_quotes` 表
3. **API查询**: 后端API从数据库读取数据
4. **前端展示**: 前端调用API获取数据并显示在首页

## 注意事项

1. 首次使用需要确保数据库表已创建
2. 定时任务会在交易时间段自动运行
3. 如果数据库中没有数据，API会返回提示信息
4. 采集器支持多数据源，确保数据获取的可靠性

## 测试验证

运行测试脚本验证功能：

```bash
python test\test_hk_index_collection.py
```

预期输出：

```
============================================================
测试港股指数实时行情采集功能
============================================================

开始采集港股指数数据...

✓ 采集成功！共采集 4 条港股指数数据

------------------------------------------------------------
指数代码     指数名称               最新价      涨跌幅(%)   
------------------------------------------------------------
HSI        恒生指数               18000.00   0.56      
HSTECH     恒生科技指数            4000.00    1.27      
HSCI       恒生综合指数            5000.00    -0.40     
HSCEI      恒生中国企业指数         6000.00    0.50      
------------------------------------------------------------

测试通过！港股指数采集功能正常。
```

## 相关文件

- `backend_api/models.py` - 数据库模型定义
- `backend_core/data_collectors/akshare/hk_index_realtime.py` - 港股指数采集器
- `backend_api/market_routes.py` - API路由
- `backend_core/data_collectors/main.py` - 定时任务配置
- `test/test_hk_index_collection.py` - 测试脚本
- `frontend/js/home.js` - 前端页面（已有，无需修改）
