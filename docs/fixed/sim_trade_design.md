# 模拟交易功能设计文档

## 1. 背景与目标

为满足用户在系统内进行虚拟实盘演练的需求，本次迭代引入“模拟交易”能力。目标如下：

- 在后端持久化管理用户虚拟账户资金、持仓、成交记录。
- 提供 REST API 实现买入/卖出操作、账户概览、持仓与订单查询。
- 在行情中心列表加入“买入/卖出”快速入口，调用模拟交易接口完成下单。
- 在“我的”频道展示模拟账户资产、收益、近期交易及持仓，并支持快速下单。

## 2. 系统架构概览

```
┌────────────────────┐        ┌────────────────────┐
│ 前端 Markets 页面  │◀──────▶│  /api/simtrade/...  │
└────────────────────┘        └────────────────────┘
          ▲                               ▲
          │                               │
┌────────────────────┐        ┌────────────────────┐
│ 前端 Profile 页面 │◀──────▶│SimTrade 服务逻辑│
└────────────────────┘        └────────────────────┘
                                         │
                                         ▼
                               模拟交易数据库表
```

- 前端通过 `authFetch` 调用 `/api/simtrade` 系列接口。
- 后端 FastAPI 新增 `trading_routes.py` 处理模拟交易逻辑。
- 数据持久化使用现有数据库，新增三张表：`sim_trade_accounts`、`sim_trade_positions`、`sim_trade_orders`。
- 行情数据仍来源于 `stock_realtime_quote`，用于成交价兜底。

## 3. 数据模型设计

### 3.1 模拟账户 (`SimTradeAccount`)
- `user_id`：唯一关联用户，确保每个用户仅一个模拟账户。
- `initial_capital`：初始资金，默认 ¥1,000,000。
- `cash_balance`：当前可用现金。
- `total_market_value`：当前持仓市值快照。
- `total_profit`/`total_profit_rate`：累计收益与收益率。
- 自动维护 `created_at`、`updated_at`。

### 3.2 模拟持仓 (`SimTradePosition`)
- `user_id` + `stock_code` 唯一约束。
- `quantity`：当前持仓股数。
- `avg_price`：加权成本价。
- `last_price`、`market_value`、`unrealized_profit`：每次下单或刷新时同步更新。

### 3.3 模拟订单 (`SimTradeOrder`)
- 记录每笔买卖操作，字段包括 `side`、`price`、`quantity`、`amount`、`realized_profit`、`status` 等。
- 默认状态 `filled`，当前未实现委托撮合，自成交即成。

## 4. 后端接口设计

路由前缀：`/api/simtrade`

| 方法 | 路径 | 描述 | 鉴权 |
| ---- | ---- | ---- | ---- |
| GET  | `/dashboard` | 返回账户概览（资金、持仓、最近订单） | 需要登录 |
| GET  | `/account` | 仅返回账户汇总数据 | 需要登录 |
| GET  | `/positions` | 返回持仓列表 | 需要登录 |
| GET  | `/orders` | 分页查询历史订单 | 需要登录 |
| POST | `/orders` | 提交买/卖订单，返回更新后的 dashboard | 需要登录 |

### 4.1 下单流程
1. 校验 `side` 合法性与 `quantity`、`price`（可选）。
2. 获取或创建模拟账户（`_ensure_account`）。
3. 若未提供价格，优先从 `stock_realtime_quote` 获取 `current_price`/`close`/`pre_close` 作为成交价。
4. 买入时：检查 `cash_balance`，更新资金与持仓加权成本；卖出时：校验仓位，计算已实现盈亏。持仓清零则删除记录。
5. 刷新所有持仓市值，重算账户市值与收益率。
6. 写入 `SimTradeOrder`，返回最新 dashboard。

### 4.2 账户刷新
- `_refresh_positions` 在每次查询/下单后执行，确保 `last_price`、`market_value` 等与最新行情同步。
- 使用 SQLAlchemy session flush 提交，并在关键异常处回滚。

## 5. 前端实现概要

### 5.1 行情中心 (`frontend/js/markets.js`)
- 涨跌榜操作列新增 `买入`、`卖出` 按钮，调用 `MarketsPage.handleQuickTrade`。
- `handleQuickTrade` 通过 `prompt` 获取股数/价格，调用 `/api/simtrade/orders` 完成下单，反馈 Toast 信息。

### 5.2 “我的”频道 (`frontend/profile.html` & `frontend/js/profile.js`)
- 页面数据源改为实时请求 `/api/simtrade/dashboard`。
- 展示模块：
  - 资产概况：总资产、现金、持仓市值占比。
  - 收益概况：累计收益/收益率、今日收益占位。
  - 最近交易：显示最新 5 条订单。
  - 投资组合：表格渲染所有持仓，支持直接在表格中快速买/卖。
- 新脚本负责格式化货币、百分比、相对时间等展示效果。

### 5.3 认证与请求
- `frontend/js/common.js` 将 `/api/simtrade` 加入 `smartFetch` 的鉴权名单，确保携带 Token。

## 6. 权限与安全

- 所有 `/api/simtrade` 接口均依赖现有 `get_current_user`，仅授权用户可访问。
- 下单逻辑防止越权：查询/更新均绑定当前用户 `user_id`。
- 未提供价格时使用内部行情；若无行情数据且无持仓，则拒绝下单以避免价格不确定。

## 7. 扩展与演进方向

- **委托撮合模拟**：当前为即时成交，可扩展订单状态机与撮合逻辑。
- **手续费/滑点**：未来可增加费率配置或策略引擎模拟真实交易成本。
- **多账户支持**：目前每个用户一个账户，可按需扩展多账户、不同初始金等功能。
- **风控参数**：增加每日交易限额、持仓限制等。

## 8. 测试建议

1. **接口测试**：使用 Postman 或 pytest 调用 `/api/simtrade/orders` 验证买入/卖出、余额校验、持仓清零逻辑。
2. **前端手工测试**：
   - 行情中心点击买入/卖出，确认提示与后台数据同步。
   - “我的”页面刷新后展示与数据库记录一致。
3. **并发场景**：模拟多次快速下单，观察资金与仓位是否正确。
4. **异常场景**：测试无价格、余额不足、仓位不足时的错误提示。

## 9. 风险与注意事项

- 当前未实现事务级串行化，极端高并发下可能需要数据库锁或队列保证一致性。
- 价格兜底依赖 `stock_realtime_quote`；若行情表数据滞后，可能导致成交价与预期差异。
- 前端 `prompt` 交互较简易，可在后续迭代中替换为专业表单与校验。

---
文档位置：`docs/fixed/sim_trade_design.md`

