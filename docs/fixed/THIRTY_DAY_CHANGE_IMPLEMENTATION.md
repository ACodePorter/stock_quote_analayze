## 30日涨跌幅扩展说明

### 功能概述
- 在`tushare`历史行情采集中新增30日涨跌幅自动计算流程，独立于现有5日逻辑运行。
- 新增HTTP接口`POST /api/stock/history/calculate_thirty_day_change`，支持手动触发指定区间的30日计算。
- 前端历史行情页面增加“计算30天涨跌”按钮与表格展示列。
- 新增命令行脚本`backend_core/data_collectors/tushare/calculate_thirty_day_change.py`便于批量调度。

### 关键改动
- 新文件`backend_core/data_collectors/tushare/thirty_day_change_calculator.py`封装30日计算核心。
- `backend_core/data_collectors/tushare/historical.py`在扩展涨跌幅后追加30日计算，写入日志类型`thirty_day_change_calculation`。
- 数据结构新增字段`thirty_day_change_percent`（建表、迁移、SQL查询、ORM模型、API响应均已同步）。
- 前端`stock_history.html`、`js/stock_history.js`增加按钮、列以及新的API调用流程。
- 后端服务层新增`backend_api/services/thirty_day_change_calculator.py`，供后续批量或校验场景复用。

### 手动验证建议
1. **数据库列检查**  
   ```sql
   \d historical_quotes
   -- 确认存在 thirty_day_change_percent REAL
   ```
2. **采集完成自动计算**  
   - 运行历史行情采集流程后，查看`historical_collect_operation_logs`是否新增`thirty_day_change_calculation`记录。
3. **API触发**  
   ```bash
   curl -X POST http://<host>/api/stock/history/calculate_thirty_day_change ^
     -H "Content-Type: application/json" ^
     -d "{\"stock_code\":\"600000\",\"start_date\":\"2025-01-01\",\"end_date\":\"2025-03-31\",\"extended_end_date\":\"2025-05-15\"}"
   ```
   - 成功后响应包含`updated_count`，数据库相应日期的`thirty_day_change_percent`应被填充。
4. **命令行脚本**  
   ```bash
   python backend_core/data_collectors/tushare/calculate_thirty_day_change.py --mode date --date 2025-03-31
   ```
   - 日志文件`thirty_day_change_calculation.log`应记录成功/失败详情。
5. **前端校验**  
   - 打开历史行情页面，确认新增按钮显示。
   - 点击按钮并确认提示包含“结束日期已自动延长30个工作日”。
   - 表格新增“30天涨跌%”列并展示后台返回的数据。

### 回归关注点
- 旧有5日、10日、60日流程保持原逻辑，未直接修改其代码。
- 确保数据库和ORM迁移执行一次即可，无重复添加列的问题。
- 若已有数据存在，需要运行迁移脚本或CLI工具对历史数据补齐30日涨跌幅。

