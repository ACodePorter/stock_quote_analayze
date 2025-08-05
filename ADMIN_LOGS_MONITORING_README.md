# 管理后台日志监控功能

## 功能概述

本功能实现了对所有系统运行产生的日志表进行查询监控，包括：

- **历史数据采集日志** (`historical_collect_operation_logs`)
- **实时数据采集日志** (`realtime_collect_operation_logs`) 
- **系统操作日志** (`operation_logs`)
- **自选股历史采集日志** (`watchlist_history_collection_logs`)

## 功能特性

### 1. 多标签页管理
- 在同一个页面实现多个标签页区分不同日志
- 支持标签页切换，每个标签页独立管理

### 2. 高级筛选功能
- **日期范围筛选**：支持开始日期和结束日期筛选
- **状态筛选**：支持成功、失败、部分成功等状态筛选
- **操作类型筛选**：支持按操作类型模糊搜索
- **股票代码筛选**：针对自选股历史采集日志的特殊筛选

### 3. 统计信息展示
- **总记录数**：显示当前筛选条件下的总记录数
- **成功记录数**：显示成功状态的记录数
- **失败记录数**：显示失败状态的记录数
- **成功率**：自动计算成功率百分比

### 4. 分页功能
- 支持分页浏览大量日志数据
- 每页可配置显示记录数（默认20条）
- 分页信息显示（当前页/总页数/总记录数）

### 5. 数据导出
- 支持将筛选后的日志数据导出（功能开发中）

## 技术实现

### 后端API

#### 1. 日志表配置
```python
LOG_TABLES = {
    "historical_collect": {
        "table_name": "historical_collect_operation_logs",
        "display_name": "历史数据采集日志",
        "columns": ["id", "operation_type", "operation_desc", "affected_rows", "status", "error_message", "created_at"]
    },
    # ... 其他日志表配置
}
```

#### 2. 主要API接口

- `GET /api/admin/logs/tables` - 获取可用的日志表列表
- `GET /api/admin/logs/query/{table_key}` - 查询指定日志表的数据
- `GET /api/admin/logs/stats/{table_key}` - 获取指定日志表的统计信息
- `GET /api/admin/logs/recent/{table_key}` - 获取最近的日志记录

#### 3. 查询参数支持

- `page` - 页码（默认1）
- `page_size` - 每页记录数（默认20，最大100）
- `start_date` - 开始日期（YYYY-MM-DD格式）
- `end_date` - 结束日期（YYYY-MM-DD格式）
- `status` - 状态筛选
- `operation_type` - 操作类型筛选
- `stock_code` - 股票代码筛选（仅适用于watchlist_history表）

### 前端实现

#### 1. 文件结构
```
admin/
├── index.html          # 主页面，包含日志查询界面
├── css/
│   └── admin.css       # 样式文件，包含日志页面样式
└── js/
    ├── admin.js        # 主管理脚本
    └── logs.js         # 日志管理专用脚本
```

#### 2. 核心功能类
```javascript
class LogsManager {
    constructor() {
        this.currentTab = 'historical_collect';
        this.currentPage = 1;
        this.pageSize = 20;
        this.filters = {};
        this.logTables = {};
        this.init();
    }
    
    // 主要方法
    - switchTab(tabKey)      // 切换标签页
    - loadLogs()            // 加载日志数据
    - applyFilters()        // 应用筛选条件
    - renderLogsTable()     // 渲染日志表格
    - updateStatsDisplay()  // 更新统计信息
}
```

## 使用方法

### 1. 启动后端服务
```bash
cd backend_api
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 访问管理后台
```
http://localhost:8000/admin
```

### 3. 登录管理后台
- 用户名：admin
- 密码：123456

### 4. 使用日志监控功能
1. 点击左侧导航栏的"系统日志"
2. 选择要查看的日志类型标签页
3. 使用筛选条件进行数据筛选
4. 查看统计信息和日志详情
5. 使用分页控件浏览更多数据

## 数据库表结构

### 1. historical_collect_operation_logs
```sql
CREATE TABLE historical_collect_operation_logs (
    id SERIAL PRIMARY KEY,
    operation_type TEXT NOT NULL,
    operation_desc TEXT NOT NULL,
    affected_rows INTEGER,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. realtime_collect_operation_logs
```sql
CREATE TABLE realtime_collect_operation_logs (
    id SERIAL PRIMARY KEY,
    operation_type TEXT NOT NULL,
    operation_desc TEXT NOT NULL,
    affected_rows INTEGER,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. operation_logs
```sql
CREATE TABLE operation_logs (
    id SERIAL PRIMARY KEY,
    operation_type TEXT NOT NULL,
    operation_desc TEXT NOT NULL,
    affected_rows INTEGER,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. watchlist_history_collection_logs
```sql
CREATE TABLE watchlist_history_collection_logs (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    affected_rows INTEGER,
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 测试

### 运行API测试
```bash
cd backend_api/test
python test_logs_api.py
```

### 测试内容
1. 获取日志表列表
2. 查询各类型日志数据
3. 获取统计信息
4. 获取最近日志记录

## 注意事项

1. **权限控制**：所有日志API都需要管理员权限认证
2. **数据库连接**：确保PostgreSQL数据库连接正常
3. **日志表存在**：确保相关的日志表已经在数据库中创建
4. **CORS配置**：确保前端可以正常访问后端API

## 扩展功能

### 计划中的功能
- [ ] 日志数据导出功能
- [ ] 日志数据清理功能
- [ ] 日志告警功能
- [ ] 日志图表展示
- [ ] 实时日志监控

### 自定义扩展
如需添加新的日志表，只需：
1. 在`LOG_TABLES`配置中添加新表信息
2. 确保数据库中存在对应的表
3. 前端会自动识别并显示新的标签页

## 故障排除

### 常见问题

1. **API返回401错误**
   - 检查管理员登录状态
   - 确认JWT token是否有效

2. **数据库连接失败**
   - 检查数据库配置
   - 确认PostgreSQL服务是否运行

3. **日志表不存在**
   - 检查数据库表是否已创建
   - 运行数据库迁移脚本

4. **前端页面无法加载**
   - 检查静态文件路径
   - 确认JavaScript文件是否正确引入

## 联系支持

如有问题或建议，请联系开发团队。 