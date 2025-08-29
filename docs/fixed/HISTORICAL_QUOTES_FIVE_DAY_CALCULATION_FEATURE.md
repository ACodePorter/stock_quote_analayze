# 历史行情5天升跌计算功能说明

## 📖 功能概述

在历史行情页面新增了"计算5天升跌"按钮，用户可以选择日期范围，系统自动计算指定期间内股票的5天升跌百分比，并更新到数据库中。

## 🎯 功能特性

- **智能计算**：只计算5天升跌%字段为空的记录，避免重复计算
- **日期范围**：支持用户自定义开始和结束日期
- **实时反馈**：计算过程中显示进度状态，完成后显示结果
- **数据更新**：计算完成后自动刷新页面，显示最新结果
- **错误处理**：完善的异常处理和用户提示

## 🏗️ 技术实现

### 前端实现

#### 1. HTML页面修改
在历史行情页面的工具栏中添加了"计算5天升跌"按钮：

```html
<button id="calculateFiveDayBtn" class="calculate-btn">计算5天升跌</button>
```

#### 2. CSS样式
为按钮添加了现代化的渐变样式和交互效果：

```css
.calculate-btn {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.3s ease;
    margin-left: 10px;
}
```

#### 3. JavaScript功能
实现了完整的计算逻辑和用户交互：

```javascript
async calculateFiveDayChange() {
    // 获取日期范围
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    // 验证输入
    if (!this.currentStockCode) {
        alert('请先选择股票');
        return;
    }
    
    // 调用后端API
    const response = await fetch(`${API_BASE_URL}/api/stock/history/calculate_five_day_change`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            stock_code: this.currentStockCode,
            start_date: startDate,
            end_date: endDate
        })
    });
    
    // 处理响应和错误
}
```

### 后端实现

#### 1. API端点
新增了计算5天升跌%的API端点：

```python
@router.post("/calculate_five_day_change")
def calculate_five_day_change(
    request: CalculateFiveDayChangeRequest,
    db: Session = Depends(get_db)
):
    """计算指定日期范围内股票的5天升跌%"""
```

#### 2. 请求模型
定义了标准的请求数据结构：

```python
class CalculateFiveDayChangeRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str
```

#### 3. 计算逻辑
实现了智能的5天升跌%计算：

```python
# 只查询5天升跌%为空的记录
query = """
    SELECT date, close
    FROM historical_quotes 
    WHERE code = :stock_code 
    AND date >= :start_date 
    AND date <= :end_date
    AND (five_day_change_percent IS NULL OR five_day_change_percent = 0)
    ORDER BY date ASC
"""

# 计算5天升跌%
for i in range(5, len(quotes)):
    current_quote = quotes[i]
    prev_quote = quotes[i-5]  # 5天前的数据
    
    if current_quote.close and prev_quote.close and prev_quote.close > 0:
        five_day_change = ((current_quote.close - prev_quote.close) / prev_quote.close) * 100
        five_day_change = round(five_day_change, 2)
        
        # 更新数据库
        update_query = """
            UPDATE historical_quotes 
            SET five_day_change_percent = :five_day_change
            WHERE code = :stock_code AND date = :date
        """
```

## 📊 使用方法

### 1. 基本操作流程

1. **选择股票**：在历史行情页面选择要计算的股票
2. **设置日期范围**：选择开始日期和结束日期
3. **点击计算**：点击"计算5天升跌"按钮
4. **等待完成**：系统显示"计算中..."状态
5. **查看结果**：计算完成后显示结果信息
6. **数据刷新**：页面自动刷新，显示最新计算结果

### 2. 计算规则

- **时间定义**：5个交易日（非自然日）
- **起始条件**：从第6个交易日开始计算
- **数据要求**：需要至少6天的历史数据
- **精度控制**：结果保留2位小数
- **智能过滤**：只计算5天升跌%字段为空的记录

### 3. 计算公式

```
5天升跌% = (当前收盘价 - 5天前收盘价) / 5天前收盘价 × 100
```

## 🔧 API接口说明

### 请求信息

- **URL**: `POST /api/stock/history/calculate_five_day_change`
- **Content-Type**: `application/json`

### 请求参数

```json
{
    "stock_code": "000001",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
}
```

### 响应格式

```json
{
    "message": "股票 000001 在 2024-01-01 到 2024-01-31 期间的5天升跌%计算完成",
    "stock_code": "000001",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "updated_count": 15,
    "total_records": 20
}
```

### 错误处理

- **400**: 日期格式无效或数据不足6天
- **500**: 服务器内部错误

## 🧪 测试验证

### 1. 运行测试脚本

```bash
python test_five_day_change_api.py
```

### 2. 测试内容

- API连接测试
- 计算功能测试
- 数据验证测试
- 错误处理测试

### 3. 验证方法

1. **手动验证**：对比手动计算结果
2. **数据一致性**：检查计算结果的准确性
3. **边界条件**：测试数据不足、异常数据等情况

## 📈 性能优化

### 1. 数据库优化

- 只查询需要计算的记录（5天升跌%为空的记录）
- 使用批量更新减少数据库交互
- 合理的索引设计提高查询性能

### 2. 计算优化

- 避免重复计算已有数据的记录
- 内存友好的数据处理方式
- 异常情况的优雅处理

### 3. 用户体验优化

- 计算过程中禁用按钮，防止重复操作
- 实时显示计算状态
- 计算完成后自动刷新数据

## 🚨 注意事项

### 1. 使用限制

- 需要至少6天的历史数据才能计算
- 只计算5天升跌%字段为空的记录
- 计算过程中请勿关闭页面

### 2. 数据要求

- 股票代码必须存在于历史行情表中
- 日期范围必须在有效数据范围内
- 收盘价数据必须完整有效

### 3. 错误处理

- 网络异常时会显示相应错误信息
- 数据不足时会提示具体原因
- 计算失败时会回滚数据库事务

## 🔮 未来扩展

### 1. 功能增强

- 支持更多时间周期（3天、7天、10天等）
- 批量计算多只股票
- 计算结果的图表展示

### 2. 性能提升

- 异步计算支持
- 计算进度实时显示
- 计算结果缓存机制

### 3. 用户体验

- 计算历史记录
- 计算任务管理
- 结果导出功能

## 📞 技术支持

如果在使用过程中遇到问题，请：

1. 检查浏览器控制台的错误信息
2. 查看后端服务的日志输出
3. 运行测试脚本验证功能
4. 联系技术支持团队

---

**功能版本**: v1.0.0  
**最后更新**: 2025年1月  
**维护状态**: 持续维护
