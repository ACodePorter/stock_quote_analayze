# 低九策略更新 - 排除ST股票

## 更新时间
2025-12-09 15:58

## 更新内容

### ✅ 已完成的修改

#### 1. 后端策略代码
**文件**: `backend_api/stock/low_nine_strategy.py`

**修改内容**:
- 更新SQL查询，添加条件 `AND name NOT LIKE '%ST%'`
- 更新文件顶部文档字符串，说明排除ST股票
- 更新函数注释

**修改前**:
```python
stocks_query = db.execute(text("""
    SELECT DISTINCT code, name 
    FROM stock_basic_info 
    WHERE LENGTH(code) = 6
    ORDER BY code
"""))
```

**修改后**:
```python
stocks_query = db.execute(text("""
    SELECT DISTINCT code, name 
    FROM stock_basic_info 
    WHERE LENGTH(code) = 6
    AND name NOT LIKE '%ST%'
    ORDER BY code
"""))
```

#### 2. 后端API路由
**文件**: `backend_api/stock/stock_screening_routes.py`

**修改内容**:
- 更新API文档字符串，说明排除ST股票

#### 3. 前端HTML
**文件**: `frontend/screening.html`

**修改内容**:
- 更新策略说明卡片
- 添加"自动排除所有ST股票"的说明

**修改前**:
```html
<li><strong>股票范围:</strong>全部A股</li>
```

**修改后**:
```html
<li><strong>股票范围:</strong>全部A股（排除ST股票）</li>
<li class="condition-item">自动排除所有ST股票（包括ST、*ST、S*ST等）</li>
```

#### 4. 文档更新
**文件**: `.agent/low_nine_strategy_implementation.md`

**修改内容**:
- 添加ST股票排除说明
- 添加统计数据（约294只ST股票，占比4.88%）

### 📊 测试验证

创建了测试脚本 `backend_api/test_st_exclusion.py`，验证结果：

```
📊 统计结果:
  全部A股数量: 6,024 只
  非ST股票数量: 5,730 只
  ST股票数量: 294 只
  排除比例: 4.88%

📋 ST股票示例（前10只）:
  000004 - *ST国华
  000005 - ST星源
  000013 - *ST石化A
  000023 - *ST深天
  000040 - *ST旭蓝
  000046 - *ST泛海
  000047 - ST中侨
  000150 - *ST宜康
  000405 - ST鑫光
  000412 - ST五环

✅ 验证结果:
  ✓ 数量验证通过: 6024 = 5730 + 294
  ✓ 成功识别 294 只ST股票
```

### 🎯 排除原因

ST股票（Special Treatment，特别处理）通常具有以下特征：
1. **财务风险高**：连续亏损、资不抵债等
2. **退市风险**：可能被强制退市
3. **交易限制**：涨跌幅限制为±5%（而非±10%）
4. **投资风险大**：不适合普通投资者

排除ST股票可以：
- ✅ 降低投资风险
- ✅ 避免退市风险
- ✅ 提高策略质量
- ✅ 符合稳健投资原则

### 📝 SQL模式说明

使用 `name NOT LIKE '%ST%'` 可以排除所有包含"ST"的股票名称，包括：
- `ST开头`：ST五环
- `*ST开头`：*ST国华
- `S*ST开头`：S*ST某某
- `中间包含ST`：某某ST某某

这种模式确保了全面覆盖所有ST类股票。

### ⚠️ 注意事项

1. **数据库依赖**：依赖 `stock_basic_info` 表中的 `name` 字段
2. **名称更新**：如果股票名称发生变化（如摘帽），需要更新数据库
3. **性能影响**：`LIKE` 查询可能略微影响性能，但影响很小
4. **覆盖范围**：目前排除约294只ST股票（4.88%）

### 🔄 后续优化建议

1. **添加ST标识字段**：
   - 在 `stock_basic_info` 表中添加 `is_st` 字段
   - 使用 `WHERE is_st = FALSE` 替代 `LIKE` 查询
   - 提高查询性能

2. **定期更新**：
   - 定期更新股票ST状态
   - 处理摘帽情况

3. **灵活配置**：
   - 添加配置选项，允许用户选择是否排除ST股票
   - 支持其他排除条件（如创业板、科创板等）

### ✅ 验证清单

- [x] 后端代码已修改
- [x] API路由已更新
- [x] 前端HTML已更新
- [x] 文档已更新
- [x] 测试脚本已创建
- [x] 测试验证通过
- [x] ST股票成功排除（294只）

### 📚 相关文件

1. `backend_api/stock/low_nine_strategy.py` - 策略实现
2. `backend_api/stock/stock_screening_routes.py` - API路由
3. `frontend/screening.html` - 前端界面
4. `backend_api/test_st_exclusion.py` - 测试脚本
5. `.agent/low_nine_strategy_implementation.md` - 实现文档

## 使用说明

修改完成后，无需额外操作。下次运行低九策略时，将自动排除所有ST股票。

### 测试方法

1. **测试ST排除功能**:
```bash
cd backend_api
python test_st_exclusion.py
```

2. **测试策略（限制100只）**:
```
http://localhost:5000/api/screening/low-nine-strategy?limit=100
```

3. **前端测试**:
   - 访问选股页面
   - 点击"低九策略"标签
   - 点击"刷新筛选"
   - 查看结果中是否包含ST股票

## 总结

✅ **成功排除294只ST股票**（占比4.88%）  
✅ **所有相关文件已更新**  
✅ **测试验证通过**  
✅ **文档已完善**  

低九策略现在将只在5,730只非ST股票中进行筛选，提高了策略的安全性和可靠性。
