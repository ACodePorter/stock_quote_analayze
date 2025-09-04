# 全量历史数据采集功能实现文档

## 功能概述

在全量历史数据采集时，系统会在每采集完一只股票的历史数据后，自动更新`stock_basic_info`表中对应股票代码的全量采集标志为已采集。

## 数据库变更

### 新增字段

为`stock_basic_info`表添加了以下字段：

```sql
-- 全量采集完成标志
full_collection_completed BOOLEAN DEFAULT FALSE

-- 全量采集完成时间
full_collection_date TIMESTAMP

-- 全量采集开始日期
full_collection_start_date DATE

-- 全量采集结束日期
full_collection_end_date DATE
```

### 索引优化

```sql
-- 为全量采集标志创建索引
CREATE INDEX idx_stock_basic_info_full_collection_completed 
ON stock_basic_info(full_collection_completed);

-- 为全量采集时间创建索引
CREATE INDEX idx_stock_basic_info_full_collection_date 
ON stock_basic_info(full_collection_date);
```

## API功能增强

### 1. 数据采集请求模型更新

`DataCollectionRequest`模型新增字段：
```python
full_collection_mode: bool = False  # 全量采集模式
```

### 2. 数据采集响应模型更新

`DataCollectionResponse`模型新增字段：
```python
full_collection_mode: bool = False  # 全量采集模式
```

### 3. API端点增强

#### 获取股票列表 (`GET /data-collection/stock-list`)

新增查询参数：
- `only_uncompleted`: 是否只返回未完成全量采集的股票

响应数据增强：
```json
{
  "total": 5744,
  "stocks": [
    {
      "code": "000001",
      "name": "平安银行",
      "full_collection_completed": false,
      "full_collection_date": null
    }
  ],
  "only_uncompleted": false
}
```

#### 启动历史数据采集 (`POST /data-collection/historical`)

请求参数增强：
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-03",
  "stock_codes": null,
  "test_mode": false,
  "full_collection_mode": true
}
```

## 核心功能实现

### 1. 全量采集标志更新

在`AkshareDataCollector.collect_single_stock_data()`方法中，每完成一只股票的数据采集后，会调用`_update_full_collection_flag()`方法更新该股票的全量采集标志：

```python
def _update_full_collection_flag(self, stock_code: str, start_date: str, end_date: str):
    """更新股票的全量采集标志"""
    try:
        self.session.execute(text("""
            UPDATE stock_basic_info 
            SET full_collection_completed = TRUE,
                full_collection_date = CURRENT_TIMESTAMP,
                full_collection_start_date = :start_date,
                full_collection_end_date = :end_date
            WHERE code = :stock_code
        """), {
            'stock_code': stock_code,
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.session.commit()
        logger.info(f"已更新股票 {stock_code} 的全量采集标志")
        
    except Exception as e:
        logger.error(f"更新股票 {stock_code} 全量采集标志失败: {e}")
        # 不抛出异常，避免影响主流程
```

### 2. 全量采集模式支持

在`collect_historical_data()`方法中，新增`full_collection_mode`参数：

```python
def collect_historical_data(self, start_date: str, end_date: str, stock_codes: Optional[List[str]] = None, full_collection_mode: bool = False):
    """批量采集历史行情数据"""
    # ...
    if full_collection_mode:
        # 全量采集模式：只获取未完成全量采集的股票
        stocks = self.get_stock_list(only_uncompleted=True)
        logger.info(f"全量采集模式：获取到 {len(stocks)} 只未完成全量采集的股票")
    else:
        # 普通模式：获取所有股票
        stocks = self.get_stock_list()
    # ...
```

### 3. 股票列表过滤

`get_stock_list()`方法支持过滤未完成的股票：

```python
def get_stock_list(self, only_uncompleted: bool = False) -> List[Dict[str, str]]:
    """从stock_basic_info表获取股票列表"""
    if only_uncompleted:
        # 只返回未完成全量采集的股票
        result = self.session.execute(text("""
            SELECT code, name, full_collection_completed, full_collection_date
            FROM stock_basic_info 
            WHERE full_collection_completed = FALSE OR full_collection_completed IS NULL
            ORDER BY code
        """))
    else:
        # 返回所有股票，包含全量采集状态
        result = self.session.execute(text("""
            SELECT code, name, full_collection_completed, full_collection_date
            FROM stock_basic_info 
            ORDER BY code
        """))
```

## 使用方式

### 1. 全量采集模式

启动全量采集任务，只处理未完成全量采集的股票：

```bash
curl -X POST "http://localhost:5000/data-collection/historical" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2024-01-01",
    "end_date": "2024-01-03",
    "stock_codes": null,
    "test_mode": false,
    "full_collection_mode": true
  }'
```

### 2. 查看未完成全量采集的股票

```bash
curl "http://localhost:5000/data-collection/stock-list?only_uncompleted=true"
```

### 3. 查看所有股票的全量采集状态

```bash
curl "http://localhost:5000/data-collection/stock-list"
```

## 测试验证

运行测试脚本验证功能：

```bash
python test_full_collection.py
```

测试内容包括：
1. 获取股票列表（包含全量采集状态）
2. 获取未完成全量采集的股票列表
3. 启动全量采集任务（测试模式）
4. 检查全量采集标志更新情况
5. 测试单只股票采集功能

## 优势特点

1. **避免重复采集**: 全量采集模式下只处理未完成的股票，避免重复采集
2. **状态跟踪**: 实时跟踪每只股票的全量采集状态
3. **灵活配置**: 支持全量采集模式和普通采集模式
4. **错误容错**: 全量采集标志更新失败不影响主流程
5. **性能优化**: 为相关字段创建索引，提高查询性能

## 注意事项

1. 全量采集标志的更新是在每只股票数据采集完成后进行的
2. 如果某只股票的数据采集失败，其全量采集标志不会被更新
3. 全量采集模式只影响股票的选择，不影响数据采集的逻辑
4. 可以通过`full_collection_date`字段查看每只股票完成全量采集的时间
