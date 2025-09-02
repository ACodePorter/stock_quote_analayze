# 5天升跌计算修复说明

## 问题描述

在历史行情页面中，计算5天升跌功能存在一个问题：每次日期范围内的最后5天数据没有计算出来。

### 具体表现
- 用户选择日期范围（如2024-01-01到2024-01-31）
- 点击"计算5天升跌"按钮
- 系统显示计算完成，但最后5天的数据（如1月27日-1月31日）的5天升跌%字段仍然为空

## 问题原因分析

### 根本原因
后端API在计算5天升跌时，只查询了用户指定的日期范围内的数据，但没有考虑到计算5天升跌需要前5天的数据。

### 具体问题
1. **查询范围限制**：API只查询 `start_date` 到 `end_date` 范围内的数据
2. **数据依赖缺失**：要计算某日的5天升跌，需要该日前5个交易日的收盘价数据
3. **边界处理不当**：最后5天的数据因为缺少前5天的数据而无法计算

### 举例说明
假设用户选择日期范围：2024-01-01 到 2024-01-31
- 要计算1月31日的5天升跌，需要1月26日的收盘价
- 要计算1月30日的5天升跌，需要1月25日的收盘价
- 但API只查询了1月1日-1月31日的数据，没有包含1月26日之前的数据

## 修复方案

### 1. 扩展查询范围
修改后端API，在计算5天升跌时自动扩展查询范围，确保有足够的前5天数据：

```python
# 为了确保最后5条记录也能计算5天升跌%，需要查询更早的数据
# 计算开始日期前5个工作日的数据
extended_start_date = self._get_date_before_business_days(start_date_fmt, 5)

extended_query = """
    SELECT date, close
    FROM historical_quotes 
    WHERE code = :stock_code 
    AND date >= :extended_start_date 
    AND date <= :end_date
    ORDER BY date ASC
"""
```

### 2. 添加工作日计算函数
新增辅助函数来计算前N个工作日的日期：

```python
def _get_date_before_business_days(date_str: str, business_days: int) -> str:
    """
    计算指定日期前N个工作日的日期
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        business_days: 工作日数量
        
    Returns:
        str: 前N个工作日的日期
    """
    from datetime import datetime, timedelta
    
    current_date = datetime.strptime(date_str, '%Y-%m-%d')
    days_back = 0
    business_days_count = 0
    
    while business_days_count < business_days:
        days_back += 1
        check_date = current_date - timedelta(days=days_back)
        
        # 跳过周末（周六=5，周日=6）
        if check_date.weekday() < 5:  # 0-4 表示周一到周五
            business_days_count += 1
    
    return check_date.strftime('%Y-%m-%d')
```

### 3. 限制更新范围
虽然查询范围扩展了，但只更新用户指定日期范围内的记录：

```python
# 只更新用户指定日期范围内的记录
if current_quote.date >= start_date_fmt and current_quote.date <= end_date_fmt:
    if current_quote.close and prev_quote.close and prev_quote.close > 0:
        five_day_change = ((current_quote.close - prev_quote.close) / prev_quote.close) * 100
        five_day_change = round(five_day_change, 2)
        
        # 更新数据库
        update_query = """
            UPDATE historical_quotes 
            SET five_day_change_percent = :five_day_change
            WHERE code = :stock_code AND date = :date
        """
        
        db.execute(text(update_query), {
            "five_day_change": five_day_change,
            "stock_code": request.stock_code,
            "date": current_quote.date
        })
        
        updated_count += 1
```

## 修复效果

### 修复前
- 最后5天的5天升跌%字段为空
- 用户需要手动调整日期范围才能计算完整数据

### 修复后
- 所有指定日期范围内的数据都能正确计算5天升跌%
- 包括最后5天的数据
- 用户体验更加流畅

## 测试验证

### 测试脚本
创建了测试脚本 `test/test_five_day_change_fix.py` 来验证修复效果：

1. **功能测试**：验证最后5天数据是否能正确计算
2. **边界测试**：测试数据不足等异常情况
3. **结果验证**：确认所有记录都成功计算了5天升跌%

### 测试步骤
1. 查询原始历史数据，检查5天升跌%字段状态
2. 执行5天升跌计算
3. 再次查询数据，验证计算结果
4. 统计成功计算的记录数量

## 相关文件

### 修改的文件
- `backend_api/stock/history_api.py` - 主要修复逻辑

### 新增的文件
- `test/test_five_day_change_fix.py` - 测试脚本
- `docs/fixed/FIVE_DAY_CHANGE_CALCULATION_FIX.md` - 本文档

## 注意事项

1. **性能影响**：扩展查询范围会增加少量数据库查询开销，但影响很小
2. **数据一致性**：确保只更新用户指定日期范围内的记录，避免影响其他数据
3. **错误处理**：保持原有的错误处理机制，确保系统稳定性

## 总结

通过扩展查询范围并添加工作日计算逻辑，成功解决了最后5天数据无法计算5天升跌%的问题。修复后的系统能够正确处理所有日期范围内的数据，提供更好的用户体验。
