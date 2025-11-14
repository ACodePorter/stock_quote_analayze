## 30日涨跌幅功能设计说明

### 1. 设计背景
- 历史行情页面需要在现有 5/10/60 日涨跌幅基础上新增 30 日维度，满足更长周期的走势分析。
- 既有 5 日逻辑稳定运行，用户要求避免影响原实现，新增能力需独立实现并可复用。
- 系统包含自动采集、手动脚本、HTTP 服务及前端页面，设计需覆盖全链路。

### 2. 目标与约束
- **目标**  
  1. 采集流程完成后自动计算指定日期的 30 日涨跌幅。  
  2. 后端提供 HTTP 接口及 CLI 脚本，支持人工触发。  
  3. 前端展示新增数据列，并允许按钮触发后台计算。  
- **约束**  
  - 保留 `FiveDayChangeCalculator` 及相关流程不修改。  
  - 使用现有数据库结构及 ORM 机制，新增字段需兼容历史数据。  
  - 仅依靠交易日（工作日）顺序计算，不额外引入交易日历表。  
  - 代码需维持与十日/六十日逻辑的风格一致，便于后续扩展。  

### 3. 架构设计
```
+-------------------+            +-----------------------------+
| 历史行情采集流程  | --成功-->  | ThirtyDayChangeCalculator  |
| (historical.py)   |            | (SQLAlchemy Session)       |
+-------------------+            +-----------------------------+
        |                                      |
        | 自动日志记录                         | 更新字段 thirty_day_change_percent
        v                                      v
 +------------------+                +-------------------------+
 | operation_logs   |                | historical_quotes 表    |
 +------------------+                +-------------------------+
        ^
        | HTTP/CLI 手动触发
        |
 +-----------------------------------------------+
 | 后端接口 history_api / CLI calculate_30d      |
 +-----------------------------------------------+
        ^
        | fetch API 调用
        |
+--------------------------+
| 前端 stock_history 页面  |
+--------------------------+
```

### 4. 数据模型
- 新增字段：`historical_quotes.thirty_day_change_percent REAL`
- ORM：`HistoricalQuotes.thirty_day_change_percent = Column(Float)`
- 迁移脚本：在`migrate_extended_change_fields.py`中检测/新增该列，避免重复执行。

### 5. 后端实现
1. **计算器**  
   - 新建 `ThirtyDayChangeCalculator`（session 驱动，SQL 查询 + UPDATE）。  
   - 提供单日、批量、多日状态查询，逻辑与 5 日计算类似但窗口为 30。  
2. **自动流程**  
   - `historical.py` 在扩展涨跌幅计算完成后串联执行 30 日计算，并记录 `thirty_day_change_calculation` 日志。  
3. **接口层**  
   - `GET /api/stock/history`、导出接口增加 30 日字段的查询与数据整形。  
   - 新增 `POST /api/stock/history/calculate_thirty_day_change`，支持扩展结束日期，内部向前追溯 30 个工作日。  
4. **服务层脚本**  
   - CLI 脚本 `calculate_thirty_day_change.py` 与服务 `services/thirty_day_change_calculator.py` 支撑批量/验证需求。  

### 6. 前端实现
- `stock_history.html` 新增按钮与表格列。  
- `stock_history.js` 增加按钮事件、列渲染及调用逻辑：  
  - 触发时自动延长结束日期 30 个工作日并传递 `extended_end_date`。  
  - 成功后刷新列表并提示。  

### 7. 日志与监控
- 自动流程写入 `historical_collect_operation_logs`，记录成功/失败统计。  
- CLI 脚本输出文件 `thirty_day_change_calculation.log`。  
- 接口保留标准的 print/logging 语句，方便追踪调用情况。  

### 8. 测试与验证
- 快速验证步骤：  
  1. 运行采集流程 -> 检查日志表存在 `thirty_day_change_calculation` 记录。  
  2. 调用新接口/脚本核对 `historical_quotes.thirty_day_change_percent` 数据。  
  3. 前端触发按钮确认提示、刷新效果及表格列数据。  
  4. 扩展导出 (CSV/Excel/Text) 检查新增字段。  
- 自动化测试：后续可在 `backend_api/test/test_stock_history_api.py` 中补充接口级用例。  

### 9. 风险与缓解
- **数据缺失**：历史数据不足 31 条时无法计算；日志返回详细失败列表。  
- **性能**：批量计算按日期序列依次执行，长区间需关注执行时间，可在后期引入批处理优化。  
- **并发**：与现有逻辑一致，依赖数据库事务控制；如需进一步优化可在未来引入锁或队列。  
- **路径/编码问题**：Windows 中文目录可能影响 CLI/pytest，部署时需确保环境变量（如 `PYTHONPATH`）正确设置。  

### 10. 后续规划
- 抽象多周期计算器模板，减少重复代码。  
- 完善接口自动测试及 CLI 集成测试。  
- 若需更复杂交易日处理，可引入交易日历表或第三方日历服务。  

