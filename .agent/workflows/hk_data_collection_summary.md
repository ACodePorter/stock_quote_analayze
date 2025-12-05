---
description: Summary of HK Historical Data Collection Enhancements
---

# 港股历史数据采集功能增强总结

## 实施日期
2025-12-05

## 主要功能

### 1. 全量采集支持
- **功能**: 支持采集数据库中所有港股的历史数据
- **实现位置**: 
  - Backend: `backend_api/stock/data_collection_api.py`
  - Frontend: `admin/src/views/DataCollectView.vue`

### 2. 采集间隔控制
- **功能**: 港股采集间隔设置为5秒，A股保持20秒
- **目的**: 遵守Akshare的限流要求，同时提高港股采集效率
- **实现**: 在 `collect_historical_data` 方法中根据市场类型动态调整休眠时间

### 3. 市场参数支持
- **新增参数**: `market` (可选值: 'CN' 或 'HK')
- **默认值**: 'CN' (A股)
- **影响范围**:
  - `DataCollectionRequest` 模型
  - `DataCollectionResponse` 模型
  - `collect_historical_data` 方法
  - `run_historical_collection_task` 函数

## 代码变更详情

### Backend 变更

#### 1. models.py
```python
class DataCollectionRequest(BaseModel):
    start_date: str
    end_date: str
    stock_codes: Optional[List[str]] = None
    test_mode: bool = False
    full_collection_mode: bool = False
    market: str = 'CN'  # 新增: CN: A股, HK: 港股

class DataCollectionResponse(BaseModel):
    task_id: str
    status: str
    message: str
    start_date: str
    end_date: str
    stock_codes: Optional[List[str]] = None
    test_mode: bool = False
    full_collection_mode: bool = False
    market: str = 'CN'  # 新增
```

#### 2. data_collection_api.py

**新增方法 - 获取港股列表**:
```python
def get_hk_stock_list(self) -> List[Dict[str, str]]:
    """从stock_basic_info_hk表获取港股列表"""
    # 检查数据库中港股数量
    # 如果数量过少(<100)，尝试从Akshare重新获取
    # 返回港股代码和名称列表
```

**更新方法 - 历史数据采集**:
```python
def collect_historical_data(
    self, 
    start_date: str, 
    end_date: str, 
    stock_codes: Optional[List[str]] = None, 
    full_collection_mode: bool = False, 
    market: str = 'CN'  # 新增参数
) -> Dict[str, any]:
    # 根据market参数选择股票列表来源
    # 全量采集模式下:
    #   - market='HK': 获取所有港股
    #   - market='CN': 获取未完成全量采集的A股
    # 采集后根据market调整休眠时间
```

**更新函数 - 后台任务**:
```python
def run_historical_collection_task(
    task_id: str,
    start_date: str,
    end_date: str,
    stock_codes: Optional[List[str]] = None,
    test_mode: bool = False,
    full_collection_mode: bool = False,
    market: str = 'CN'  # 新增参数
):
    # 测试模式下根据market选择股票列表
    # 计算任务总数时考虑market参数
    # 传递market参数给collect_historical_data
```

### Frontend 变更

#### DataCollectView.vue

**新增接口定义**:
```typescript
interface HKFormData {
  start_date: string
  end_date: string
  stock_codes_text: string
  collection_type: 'specified' | 'all'  // 新增: 采集类型
}

interface RequestData {
  start_date: string
  end_date: string
  test_mode: boolean
  stock_codes?: string[]
  full_collection_mode?: boolean
  market?: string  // 新增: 市场参数
}
```

**UI 增强**:
- 添加采集类型选择器（指定股票/全量采集）
- 全量采集模式下隐藏股票代码输入框
- 显示全量采集说明信息

**逻辑更新**:
```typescript
const startHKCollection = async () => {
  // 验证表单
  // 指定股票模式: 需要输入股票代码
  // 全量采集模式: 不需要输入股票代码
  
  const requestData: RequestData = {
    start_date: hkForm.value.start_date,
    end_date: hkForm.value.end_date,
    test_mode: false,
    market: 'HK'  // 设置市场为港股
  }

  if (hkForm.value.collection_type === 'specified') {
    // 解析股票代码
    requestData.stock_codes = stockCodes
  } else {
    // 全量采集模式
    requestData.full_collection_mode = true
  }
}
```

## 数据库结构

### stock_basic_info_hk 表
```sql
CREATE TABLE stock_basic_info_hk (
    code VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    create_date TIMESTAMP
);
```

### historical_quotes_hk 表
包含以下字段:
- code, ts_code, name, english_name
- date, open, high, low, close, pre_close
- volume, amount, change_amount, change_percent
- turnover_rate, amplitude
- five_day_change_percent, ten_day_change_percent
- thirty_day_change_percent, sixty_day_change_percent
- collected_source, collected_date

## 使用说明

### 1. 指定股票采集
1. 选择"港股历史数据采集"标签
2. 选择日期范围
3. 选择"指定股票"
4. 输入港股代码（5位数字，每行一个）
5. 点击"开始采集"

### 2. 全量采集
1. 选择"港股历史数据采集"标签
2. 选择日期范围
3. 选择"全量采集"
4. 点击"开始采集"
5. 系统将自动采集数据库中所有港股的历史数据

## 性能优化

1. **采集间隔**: 港股5秒/次，避免API限流
2. **数据源切换**: EastMoney失败时自动切换到Sina
3. **重试机制**: EastMoney接口支持3次重试
4. **增量采集**: 自动跳过已存在的数据

## 注意事项

1. **单任务执行**: 系统同时只能运行一个采集任务
2. **数据完整性**: 全量采集前确保stock_basic_info_hk表有足够数据
3. **网络稳定性**: 采集过程需要稳定的网络连接
4. **时间估算**: 2730只港股 × 5秒 ≈ 3.8小时（单日数据）

## 后续优化建议

1. **断点续传**: 实现任务中断后的续传功能
2. **并发控制**: 考虑适当的并发采集（需评估API限制）
3. **进度持久化**: 将采集进度保存到数据库
4. **错误重试**: 对失败的股票实现自动重试机制
5. **数据验证**: 增加采集数据的完整性验证

## 测试建议

1. 测试指定股票采集（1-5只股票）
2. 测试全量采集（建议先用测试模式）
3. 验证采集间隔是否符合预期
4. 检查数据库中数据的完整性和准确性
5. 测试任务取消功能
