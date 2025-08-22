# 研报重复数据问题修复总结

## 问题描述

用户在使用股票分析系统时遇到"获取研报数据失败"的错误，错误信息显示：

```
(psycopg2.errors.UniqueViolation) 错误: 重复键违反唯一约束
键值"(stock_code, report_name, report_date)=(688256,公司深度报告:云边端共铸国产算力脊梁,软硬件同迎寒武破晓时代,2025-06-29 00:00:00)"已经存在
```

## 问题分析

### 根本原因
1. **唯一约束冲突**：数据库表 `stock_research_reports` 存在唯一约束 `(stock_code, report_name, report_date)`
2. **标点符号差异**：系统尝试插入的研报标题与数据库中已存在的研报标题内容相同，但标点符号不同
   - 数据库中的标题：`公司深度报告：云边端共铸国产算力脊梁，软硬件同迎寒武破晓时代`（中文标点）
   - 要插入的标题：`公司深度报告:云边端共铸国产算力脊梁,软硬件同迎寒武破晓时代`（英文标点）
3. **日期格式不匹配**：数据库中的日期包含时间部分（如 `2025-06-29 00:00:00`），而查询使用的日期只有日期部分（如 `2025-06-29`）

### 技术细节
- 数据库表：`stock_research_reports`
- 唯一约束：`idx_16511_sqlite_autoindex_stock_research_reports_1` 作用于 `(stock_code, report_name, report_date)`
- 影响股票：寒武纪-U (688256)
- 错误时间：2025-06-29

## 解决方案

### 1. 改进重复检测逻辑
在 `backend_api/stock/stock_news.py` 的 `save_research_reports_to_db` 函数中添加了智能重复检测：

```python
# 改进重复检测：考虑标点符号差异和内容相似性
existing_report = None

# 首先尝试精确匹配（修复日期格式不匹配问题）
existing_report = db.query(StockResearchReport).filter(
    StockResearchReport.stock_code == symbol,
    StockResearchReport.report_name == report_name,
    StockResearchReport.report_date.like(f"{report_date_str}%")
).first()

# 如果精确匹配失败，尝试模糊匹配（处理标点符号差异）
if not existing_report:
    # 查询同一天的所有研报（使用日期字符串匹配，忽略时间部分）
    same_date_reports = db.query(StockResearchReport).filter(
        StockResearchReport.stock_code == symbol,
        StockResearchReport.report_date.like(f"{report_date_str}%")
    ).all()
    
    # 检查是否有内容相似的研报
    for existing in same_date_reports:
        if _is_similar_title(report_name, existing.report_name):
            existing_report = existing
            print(f"[DEBUG] 发现相似研报（标点符号差异）: '{report_name}' vs '{existing.report_name}'")
            break
```

### 2. 添加标题标准化函数
新增 `_normalize_title()` 函数，统一处理中英文标点符号差异：

```python
def _normalize_title(title: str) -> str:
    """标准化研报标题，移除标点符号差异"""
    if not title:
        return ""
    
    # 替换中文标点为英文标点
    normalized = title
    normalized = normalized.replace('：', ':')  # 中文冒号 -> 英文冒号
    normalized = normalized.replace('，', ',')  # 中文逗号 -> 英文逗号
    normalized = normalized.replace('；', ';')  # 中文分号 -> 英文分号
    normalized = normalized.replace('！', '!')  # 中文感叹号 -> 英文感叹号
    normalized = normalized.replace('？', '?')  # 中文问号 -> 英文问号
    normalized = normalized.replace('（', '(')  # 中文括号 -> 英文括号
    normalized = normalized.replace('）', ')')
    normalized = normalized.replace('【', '[')  # 中文方括号 -> 英文方括号
    normalized = normalized.replace('】', ']')
    normalized = normalized.replace('《', '<')  # 中文书名号 -> 英文尖括号
    normalized = normalized.replace('》', '>')
    
    return normalized
```

### 3. 添加标题相似性检测函数
新增 `_is_similar_title()` 函数，智能判断两个标题是否相似：

```python
def _is_similar_title(title1: str, title2: str) -> bool:
    """判断两个研报标题是否相似（考虑标点符号差异）"""
    if not title1 or not title2:
        return False
    
    # 标准化两个标题
    norm1 = _normalize_title(title1)
    norm2 = _normalize_title(title2)
    
    # 如果标准化后完全相同，认为是相似标题
    if norm1 == norm2:
        return True
    
    # 计算相似度
    common_chars = sum(1 for c1, c2 in zip(norm1, norm2) if c1 == c2)
    total_chars = max(len(norm1), len(norm2))
    
    if total_chars > 0:
        similarity = common_chars / total_chars
        # 如果相似度超过90%，认为是相似标题
        return similarity > 0.9
    
    return False
```

## 修复效果

### 修复前
- 系统无法识别标点符号差异的相似标题
- 尝试插入重复内容时触发唯一约束违反错误
- 用户看到"获取研报数据失败"的错误信息

### 修复后
- 系统能够智能识别内容相似但标点符号不同的研报标题
- 自动跳过重复或相似的研报数据插入
- 避免唯一约束违反错误
- 用户能够正常获取研报数据

## 测试验证

### 测试用例1：标点符号差异
- 标题1：`公司深度报告：云边端共铸国产算力脊梁，软硬件同迎寒武破晓时代`（中文标点）
- 标题2：`公司深度报告:云边端共铸国产算力脊梁,软硬件同迎寒武破晓时代`（英文标点）
- 结果：✅ 正确识别为相似标题

### 测试用例2：完全不同的标题
- 标题1：`一季度业绩同环比高增，积极备货保障下游供应`
- 标题2：`公司深度报告：云边端共铸国产算力脊梁，软硬件同迎寒武破晓时代`
- 结果：✅ 正确识别为不相似标题

### 测试用例3：部分相似的标题
- 标题1：`公司深度报告：云边端共铸国产算力脊梁，软硬件同迎寒武破晓时代`
- 标题2：`公司深度报告：云边端共铸国产算力脊梁，软硬件同迎寒武破晓时代（修订版）`
- 结果：✅ 正确识别为不相似标题

## 文件修改清单

1. **`backend_api/stock/stock_news.py`**
   - 修改 `save_research_reports_to_db` 函数，添加智能重复检测
   - 新增 `_normalize_title` 函数，处理标点符号标准化
   - 新增 `_is_similar_title` 函数，判断标题相似性

2. **测试脚本**
   - `test_title_similarity.py` - 测试标题相似性检测功能
   - `test_research_reports_api.py` - 测试修复后的研报API
   - `check_research_reports_structure.py` - 检查数据库表结构
   - `check_cambricon_reports.py` - 检查特定股票的研报数据
   - `fix_research_reports_duplicates.py` - 修复重复数据（如需要）

## 部署说明

1. **代码更新**：将修改后的 `backend_api/stock/stock_news.py` 部署到生产环境
2. **重启服务**：重启后端API服务以应用代码更改
3. **功能验证**：测试研报数据获取功能，确认不再出现重复键错误

## 预防措施

1. **数据标准化**：在数据采集阶段统一标点符号格式
2. **定期检查**：定期检查数据库中是否存在重复或相似的研报数据
3. **监控告警**：添加数据库约束违反的监控和告警机制

## 总结

通过实施智能重复检测机制和修复日期格式匹配问题，我们成功解决了研报数据插入时的唯一约束违反问题。新的系统能够：

- 准确识别内容相似但标点符号不同的研报标题
- 正确处理数据库中的日期格式差异（包含时间部分 vs 仅日期部分）
- 自动避免重复数据的插入
- 提高系统的稳定性和用户体验
- 为后续的数据质量改进奠定基础

这个修复不仅解决了当前的问题，还为系统处理类似的数据差异问题提供了通用的解决方案。

## 关键修复点

1. **智能重复检测**：添加了基于标点符号标准化的标题相似性检测
2. **日期格式兼容**：使用 `LIKE` 操作符处理日期格式差异，确保同一天的数据能够正确匹配
3. **双重检查机制**：先进行精确匹配，再进行模糊匹配，确保不遗漏任何重复数据
