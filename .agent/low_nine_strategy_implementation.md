# 低九策略实现总结

## 概述
成功实现了"低九策略"选股功能，该策略应用于下跌趋势中，识别连续9根K线每天收盘价都低于其前面第4天收盘价的股票。

## 策略说明
**低九策略条件：**
- 应用场景：下跌趋势
- 核心条件：连续 9 根K线（或交易日），每一天的收盘价都低于它前面第4天的收盘价
- 数据要求：至少需要13个交易日的历史数据（9天形态 + 4天前置数据）
- **股票范围**：
  - 全部A股
  - **自动排除ST股票**（包括ST、*ST、S*ST等所有ST类股票，约294只，占比4.88%）

## 实现的文件修改

### 1. 后端策略实现
**新建文件：** `backend_api/stock/low_nine_strategy.py`
- 实现了 `LowNineStrategy` 类
- 核心方法：
  - `check_low_nine_pattern()`: 检查是否满足低九策略形态
  - `screening_low_nine_strategy()`: 主选股函数，遍历所有A股进行筛选
- 返回数据包括：
  - 形态开始/结束日期
  - 形态开始价格
  - 9天跌幅
  - 9天内最高价/最低价
  - 当前价格和涨跌幅

### 2. 后端路由注册
**修改文件：** `backend_api/stock/stock_screening_routes.py`
- 导入 `LowNineStrategy` 类
- 新增API端点：`GET /api/screening/low-nine-strategy`
- 返回符合条件的股票列表

### 3. 前端HTML界面
**修改文件：** `frontend/screening.html`
- 在策略标签页导航中添加"低九策略"标签
- 新增低九策略内容区域，包括：
  - 策略说明卡片
  - 刷新筛选按钮
  - 加载指示器
  - 结果表格（11列）：
    - 股票代码、名称
    - 形态开始/结束日期
    - 形态开始价格
    - 9天跌幅
    - 9天最高价/最低价
    - 当前价格、涨跌幅
    - 操作（历史、详情链接）

### 4. 前端JavaScript逻辑
**修改文件：** `frontend/js/screening.js`
- 在多个位置添加 `low-nine` 策略支持：
  - `loadScreeningResults()`: 添加suffix映射和API URL
  - 错误处理：设置正确的colspan（11列）
  - `renderResults()`: 添加低九策略的表格渲染逻辑
  - 特殊处理：9天跌幅使用独立的颜色样式（红色表示下跌）

## 技术细节

### 策略算法
```python
# 检查连续9天，每天收盘价 < 前4天收盘价
for i in range(9):
    current_close = historical_data[i]['close']
    fourth_day_before_close = historical_data[i + 4]['close']
    if current_close >= fourth_day_before_close:
        pattern_valid = False
        break
```

### 数据结构
```python
result_item = {
    'code': str,                    # 股票代码
    'name': str,                    # 股票名称
    'current_price': float,         # 当前价格
    'current_change_percent': float,# 当前涨跌幅
    'pattern_start_date': str,      # 形态开始日期（第9天）
    'pattern_end_date': str,        # 形态结束日期（最新一天）
    'pattern_start_price': float,   # 形态开始价格
    'decline_ratio': float,         # 9天跌幅比例
    'max_price_in_9days': float,    # 9天内最高价
    'min_price_in_9days': float     # 9天内最低价
}
```

## API端点

**URL:** `GET /api/screening/low-nine-strategy`

**响应示例:**
```json
{
    "success": true,
    "data": [
        {
            "code": "000001",
            "name": "平安银行",
            "current_price": 12.50,
            "current_change_percent": -1.20,
            "pattern_start_date": "2025-11-25",
            "pattern_end_date": "2025-12-09",
            "pattern_start_price": 13.80,
            "decline_ratio": -0.0942,
            "max_price_in_9days": 13.80,
            "min_price_in_9days": 12.50
        }
    ],
    "total": 1,
    "search_date": "2025-12-09",
    "strategy_name": "低九策略"
}
```

## 使用方法

1. 访问选股页面：`http://your-domain/screening.html`
2. 点击"低九策略"标签
3. 点击"刷新筛选"按钮
4. 等待筛选完成，查看结果
5. 可点击"历史"或"详情"查看具体股票信息

## 注意事项

1. **数据要求：** 需要至少13个交易日的历史数据
2. **性能考虑：** 遍历所有A股可能需要一定时间，建议添加进度提示
3. **策略特点：** 该策略识别持续下跌的股票，适合寻找可能的反转机会
4. **风险提示：** 仅作为技术分析参考，不构成投资建议

## 后续优化建议

1. 添加缓存机制，避免频繁计算
2. 支持自定义参数（如调整K线数量、前置天数）
3. 添加更多统计指标（如成交量变化）
4. 支持导出筛选结果
5. 添加历史回测功能

## 测试建议

1. 测试空数据情况
2. 测试数据不足13天的情况
3. 测试边界条件（恰好9天满足条件）
4. 验证日期排序正确性
5. 检查价格计算准确性
