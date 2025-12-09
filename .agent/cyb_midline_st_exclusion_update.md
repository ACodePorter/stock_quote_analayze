# 创业板中线选股策略 - 排除ST股票更新

## 更新时间
2025-12-09 16:06

## 更新内容

### ✅ 已完成的修改

#### 1. 后端策略代码
**文件**: `backend_api/stock/stock_screening.py`

**修改内容**:
- 更新SQL查询，添加条件 `AND name NOT LIKE '%ST%'`
- 更新注释说明排除ST股票

**修改位置**: 第280-286行

**修改前**:
```python
# 1. 获取创业板股票列表（代码以3开头）
cyb_stocks_query = db.execute(text("""
    SELECT DISTINCT code, name 
    FROM stock_basic_info 
    WHERE code LIKE '3%' AND LENGTH(code) = 6
    ORDER BY code
"""))
```

**修改后**:
```python
# 1. 获取创业板股票列表（代码以3开头，排除ST股票）
cyb_stocks_query = db.execute(text("""
    SELECT DISTINCT code, name 
    FROM stock_basic_info 
    WHERE code LIKE '3%' AND LENGTH(code) = 6
    AND name NOT LIKE '%ST%'
    ORDER BY code
"""))
```

#### 2. 后端API路由
**文件**: `backend_api/stock/stock_screening_routes.py`

**修改内容**:
- 更新API文档字符串，添加股票范围说明
- 明确标注排除ST股票

**修改位置**: 第29-45行

#### 3. 前端HTML
**文件**: `frontend/screening.html`

**修改内容**:
- 更新策略说明卡片
- 股票范围改为"创业板股票（代码以3开头，排除ST股票）"
- 添加第6条选股条件："自动排除所有ST股票（包括ST、*ST、S*ST等）"

**修改位置**: 第34-46行

### 📊 预期效果

根据之前的测试数据：
- 全部A股中ST股票约294只（4.88%）
- 创业板股票总数约1200只左右
- 预计创业板中约有50-60只ST股票会被排除

### 🎯 策略说明

**创业板中线选股策略**现在包含以下条件：

1. ✅ **股票范围**：
   - 创业板股票（代码以3开头）
   - **自动排除ST股票**（包括ST、*ST、S*ST等）

2. ✅ **选股条件**：
   - 第一个涨停（涨幅≥9.8%）
   - 第一次回调不跌穿涨停底部
   - 第二次上涨突破第一个涨停高点
   - 中间包含向上跳空和揉搓线指标
   - 当前均线多头排列（MA5 > MA10 > MA20）
   - **自动排除所有ST股票**

### 🔍 与低九策略的一致性

现在两个策略都排除ST股票：
- ✅ **低九策略**：全部A股（排除ST股票）
- ✅ **创业板中线策略**：创业板股票（排除ST股票）

保持了策略的一致性和风险控制标准。

### ✅ 验证清单

- [x] 后端SQL查询已修改
- [x] API文档已更新
- [x] 前端界面已更新
- [x] 注释说明已完善
- [x] 与低九策略保持一致

### 📝 相关文件

1. `backend_api/stock/stock_screening.py` - 策略实现
2. `backend_api/stock/stock_screening_routes.py` - API路由
3. `frontend/screening.html` - 前端界面

### 💡 使用说明

修改已生效，无需额外操作。下次运行创业板中线选股策略时：
- ✅ 将自动排除创业板中的ST股票
- ✅ 只在非ST创业板股票中筛选
- ✅ 前端界面会显示排除说明

### 🔄 后续建议

如果需要为其他策略也添加ST排除功能，可以参考相同的模式：
1. 在SQL查询中添加 `AND name NOT LIKE '%ST%'`
2. 更新API文档字符串
3. 更新前端策略说明
4. 添加相应的注释

## 总结

✅ **创业板中线选股策略已成功排除ST股票**  
✅ **所有相关文件已更新**  
✅ **与低九策略保持一致的风险控制标准**  

创业板中线选股策略现在将只在非ST创业板股票中进行筛选，提高了策略的安全性和可靠性。
