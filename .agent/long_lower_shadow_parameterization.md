# 长下影线策略参数化实现总结

## 更新时间
2025-12-09 16:32

## 实现目标
将长下影线策略的固定规则改为可配置参数，允许用户自定义选择或输入参数值。

## 已完成的后端修改

### 1. API路由参数化 ✅
**文件**: `backend_api/stock/stock_screening_routes.py`

**添加的参数**:
- `lower_shadow_ratio`: 下影线长度 >= 实体长度的倍数（0.5-3.0，默认1.0）
- `upper_shadow_ratio`: 上影线 <= 实体长度的比例（0.1-0.5，默认0.3）
- `min_amplitude`: 最小振幅要求（0.01-0.1，默认0.02）
- `recent_days`: 检查最近N个交易日（1-10，默认2）

**API调用示例**:
```
GET /api/screening/long-lower-shadow-strategy?lower_shadow_ratio=1.5&upper_shadow_ratio=0.2&min_amplitude=0.03&recent_days=3
```

### 2. 策略实现参数化 ✅
**文件**: `backend_api/stock/long_lower_shadow_strategy.py`

**修改的方法**:
1. `check_long_lower_shadow()` - 添加 lower_shadow_ratio, upper_shadow_ratio 参数
2. `check_long_lower_shadow_conditions()` - 添加所有4个参数
3. `screening_long_lower_shadow_strategy()` - 添加所有4个参数并传递

**参数传递链**:
```
API路由 
  → screening_long_lower_shadow_strategy(参数)
    → check_long_lower_shadow_conditions(参数)
      → check_long_lower_shadow(参数)
```

### 3. 返回数据增强 ✅
API响应中添加了 `parameters` 字段，返回当前使用的参数值：
```json
{
  "success": true,
  "data": [...],
  "total": 10,
  "search_date": "2025-12-09",
  "strategy_name": "长下影阳线",
  "parameters": {
    "lower_shadow_ratio": 1.0,
    "upper_shadow_ratio": 0.3,
    "min_amplitude": 0.02,
    "recent_days": 2
  }
}
```

## 待实现的前端修改

### 1. 添加参数输入界面
**文件**: `frontend/screening.html`

需要在长下影线策略的内容区域添加参数配置表单：

```html
<div class="strategy-params">
    <h3>策略参数配置</h3>
    <div class="param-group">
        <label>下影线倍数 (0.5-3.0):</label>
        <input type="number" id="lowerShadowRatio" 
               min="0.5" max="3.0" step="0.1" value="1.0">
        <span class="param-desc">下影线长度 >= 实体长度的倍数</span>
    </div>
    <div class="param-group">
        <label>上影线比例 (0.1-0.5):</label>
        <input type="number" id="upperShadowRatio" 
               min="0.1" max="0.5" step="0.05" value="0.3">
        <span class="param-desc">上影线 <= 实体长度的比例</span>
    </div>
    <div class="param-group">
        <label>最小振幅 (1%-10%):</label>
        <input type="number" id="minAmplitude" 
               min="0.01" max="0.1" step="0.01" value="0.02">
        <span class="param-desc">当日振幅要求</span>
    </div>
    <div class="param-group">
        <label>检查天数 (1-10):</label>
        <input type="number" id="recentDays" 
               min="1" max="10" step="1" value="2">
        <span class="param-desc">检查最近N个交易日</span>
    </div>
</div>
```

### 2. 修改JavaScript逻辑
**文件**: `frontend/js/screening.js`

需要修改 `loadScreeningResults` 方法，读取参数并构造URL：

```javascript
// 在 long-lower-shadow 策略的URL构造中
if (strategy === 'long-lower-shadow') {
    // 读取参数
    const lowerShadowRatio = document.getElementById('lowerShadowRatio')?.value || 1.0;
    const upperShadowRatio = document.getElementById('upperShadowRatio')?.value || 0.3;
    const minAmplitude = document.getElementById('minAmplitude')?.value || 0.02;
    const recentDays = document.getElementById('recentDays')?.value || 2;
    
    // 构造URL
    url = `${apiBaseUrl}/api/screening/long-lower-shadow-strategy?` +
          `lower_shadow_ratio=${lowerShadowRatio}&` +
          `upper_shadow_ratio=${upperShadowRatio}&` +
          `min_amplitude=${minAmplitude}&` +
          `recent_days=${recentDays}`;
}
```

### 3. 显示当前参数
在结果显示区域添加当前使用的参数信息：

```html
<div class="current-params">
    <strong>当前参数：</strong>
    下影线倍数: <span id="current-lower-ratio">1.0</span> |
    上影线比例: <span id="current-upper-ratio">0.3</span> |
    最小振幅: <span id="current-amplitude">2%</span> |
    检查天数: <span id="current-days">2</span>
</div>
```

## 参数说明

### 1. 下影线倍数 (lower_shadow_ratio)
- **范围**: 0.5 - 3.0
- **默认值**: 1.0
- **说明**: 下影线长度必须 >= 实体长度的X倍
- **示例**:
  - 1.0 = 下影线至少等于实体长度
  - 1.5 = 下影线至少是实体长度的1.5倍
  - 2.0 = 下影线至少是实体长度的2倍（更严格）

### 2. 上影线比例 (upper_shadow_ratio)
- **范围**: 0.1 - 0.5
- **默认值**: 0.3 (30%)
- **说明**: 上影线必须 <= 实体长度的Y%
- **示例**:
  - 0.3 = 上影线最多是实体长度的30%
  - 0.2 = 上影线最多是实体长度的20%（更严格）
  - 0.5 = 上影线最多是实体长度的50%（更宽松）

### 3. 最小振幅 (min_amplitude)
- **范围**: 0.01 - 0.1 (1% - 10%)
- **默认值**: 0.02 (2%)
- **说明**: 当日振幅必须超过Z%
- **计算**: (最高价 - 最低价) / 昨日收盘价
- **示例**:
  - 0.02 = 振幅至少2%
  - 0.03 = 振幅至少3%（更严格）
  - 0.05 = 振幅至少5%（更严格）

### 4. 检查天数 (recent_days)
- **范围**: 1 - 10
- **默认值**: 2
- **说明**: 检查最近N个交易日内是否出现长下影线
- **示例**:
  - 2 = 检查最近2个交易日
  - 5 = 检查最近5个交易日（更宽松）
  - 1 = 只检查最新一个交易日（更严格）

## 使用场景

### 场景1: 寻找强烈反转信号
```
下影线倍数: 2.0（更长的下影线）
上影线比例: 0.2（更短的上影线）
最小振幅: 0.05（5%，更大的波动）
检查天数: 1（最新一天）
```

### 场景2: 宽松筛选，增加候选
```
下影线倍数: 0.8（稍短的下影线）
上影线比例: 0.4（允许较长的上影线）
最小振幅: 0.01（1%，较小的波动）
检查天数: 5（最近5天）
```

### 场景3: 默认平衡配置
```
下影线倍数: 1.0
上影线比例: 0.3
最小振幅: 0.02（2%）
检查天数: 2
```

## 优势

1. ✅ **灵活性**: 用户可以根据市场情况调整参数
2. ✅ **可测试性**: 可以快速测试不同参数组合的效果
3. ✅ **适应性**: 适应不同的市场环境和投资风格
4. ✅ **可扩展性**: 未来可以添加更多参数
5. ✅ **向后兼容**: 所有参数都有默认值，不影响现有使用

## 后续优化建议

1. **参数预设**: 提供几组预设参数（保守、平衡、激进）
2. **参数保存**: 保存用户的参数配置到localStorage
3. **参数验证**: 前端添加参数范围验证和提示
4. **参数说明**: 添加参数说明的帮助提示
5. **回测功能**: 提供参数回测功能，评估不同参数的历史表现

## 文件清单

### 已修改
- ✅ `backend_api/stock/stock_screening_routes.py`
- ✅ `backend_api/stock/long_lower_shadow_strategy.py`

### 待修改
- ⏳ `frontend/screening.html` - 添加参数输入界面
- ⏳ `frontend/js/screening.js` - 修改API调用逻辑
- ⏳ `frontend/css/screening.css` - 添加参数表单样式（如需要）

## 测试建议

1. **默认参数测试**: 不传参数，验证使用默认值
2. **边界值测试**: 测试参数的最小值和最大值
3. **组合测试**: 测试不同参数组合的效果
4. **性能测试**: 测试宽松参数下的性能（可能返回很多结果）

## 总结

✅ **后端参数化已完成**  
⏳ **前端界面待实现**  

后端已经完全支持参数化配置，API可以接收4个参数并正确处理。前端需要添加参数输入界面和相应的JavaScript逻辑来调用参数化的API。
