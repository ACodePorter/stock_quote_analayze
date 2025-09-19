# 技术分析API

<cite>
**本文档引用的文件**  
- [stock_analysis_routes.py](file://backend_api/stock/stock_analysis_routes.py)
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py)
</cite>

## 目录
1. [接口概览](#接口概览)
2. [主分析接口](#主分析接口)
3. [技术指标接口](#技术指标接口)
4. [价格预测接口](#价格预测接口)
5. [交易建议接口](#交易建议接口)
6. [关键价位接口](#关键价位接口)
7. [分析摘要接口](#分析摘要接口)
8. [输入验证与错误处理](#输入验证与错误处理)
9. [性能与缓存策略](#性能与缓存策略)

## 接口概览

技术分析API提供了一套完整的股票智能分析功能，通过多个端点为前端应用提供多维度的分析数据。API设计遵循RESTful原则，所有接口均位于`/api/analysis`前缀下，返回统一的JSON响应格式。

```mermaid
graph TB
subgraph "技术分析API"
A[/api/analysis/stock/{stock_code}\] --> B[获取完整分析]
C[/api/analysis/technical/{stock_code}\] --> D[获取技术指标]
E[/api/analysis/prediction/{stock_code}\] --> F[获取价格预测]
G[/api/analysis/recommendation/{stock_code}\] --> H[获取交易建议]
I[/api/analysis/levels/{stock_code}\] --> J[获取关键价位]
K[/api/analysis/summary/{stock_code}\] --> L[获取分析摘要]
end
B --> M[技术指标]
B --> N[价格预测]
B --> O[交易建议]
B --> P[关键价位]
style A fill:#4CAF50,stroke:#388E3C,color:white
style C fill:#2196F3,stroke:#1976D2,color:white
style E fill:#FF9800,stroke:#F57C00,color:white
style G fill:#9C27B0,stroke:#7B1FA2,color:white
style I fill:#F44336,stroke:#D32F2F,color:white
style K fill:#607D8B,stroke:#455A64,color:white
```

**Diagram sources**  
- [stock_analysis_routes.py](file://backend_api/stock/stock_analysis_routes.py#L1-L270)

**Section sources**  
- [stock_analysis_routes.py](file://backend_api/stock/stock_analysis_routes.py#L1-L270)

## 主分析接口

`/api/analysis/stock/{stock_code}` 接口是技术分析的核心端点，整合了所有分析模块的结果，提供全面的智能分析报告。

该接口通过`StockAnalysisService`服务类协调各个分析组件，将技术指标、价格预测、交易建议和关键价位等多维度分析结果整合为一个完整的JSON响应。接口首先验证股票代码格式，然后调用分析服务获取结果，最后返回标准化的响应。

```mermaid
sequenceDiagram
participant Client as "客户端"
participant Router as "API路由器"
participant Service as "StockAnalysisService"
participant DB as "数据库"
Client->>Router : GET /api/analysis/stock/000001
Router->>Router : 验证股票代码格式
Router->>Service : 创建分析服务实例
Service->>Service : 获取历史数据
Service->>DB : 查询historical_quotes表
DB-->>Service : 返回60天历史数据
Service->>Service : 获取当前价格
Service->>Service : 计算技术指标
Service->>Service : 生成价格预测
Service->>Service : 生成交易建议
Service->>Service : 计算关键价位
Service-->>Router : 返回完整分析结果
Router-->>Client : 返回JSON响应
```

**Diagram sources**  
- [stock_analysis_routes.py](file://backend_api/stock/stock_analysis_routes.py#L15-L45)
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L300-L350)

**Section sources**  
- [stock_analysis_routes.py](file://backend_api/stock/stock_analysis_routes.py#L15-L45)
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L300-L350)

## 技术指标接口

`/api/analysis/technical/{stock_code}` 接口提供详细的RSI、MACD、KDJ和布林带等技术指标数据。

### RSI指标计算

RSI（相对强弱指数）通过比较一定周期内的平均涨幅和平均跌幅来衡量市场超买超卖状态。

```mermaid
flowchart TD
Start([开始]) --> ValidateData["验证数据长度"]
ValidateData --> DataValid{"数据长度>=15?"}
DataValid --> |否| Return50["返回50.0"]
DataValid --> |是| CalculateDelta["计算价格变化"]
CalculateDelta --> Separate["分离涨跌幅"]
Separate --> CalculateAvg["计算平均涨跌幅"]
CalculateAvg --> CheckLoss{"平均跌幅=0?"}
CheckLoss --> |是| Return100["返回100.0"]
CheckLoss --> |否| CalculateRS["计算RS值"]
CalculateRS --> CalculateRSI["计算RSI"]
CalculateRSI --> Round["四舍五入保留2位小数"]
Round --> End([返回结果])
```

**Diagram sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L20-L35)

### MACD指标计算

MACD（指数平滑异同移动平均线）通过快慢两条指数移动平均线的差值来判断市场趋势。

```mermaid
flowchart TD
Start([开始]) --> ValidateData["验证数据长度"]
ValidateData --> DataValid{"数据长度>=26?"}
DataValid --> |否| ReturnZero["返回0.0"]
DataValid --> |是| CalculateEMA["计算12日和26日EMA"]
CalculateEMA --> CalculateMACD["计算MACD线"]
CalculateMACD --> CalculateSignal["计算9日信号线"]
CalculateSignal --> CalculateHistogram["计算柱状图"]
CalculateHistogram --> Round["四舍五入保留4位小数"]
Round --> End([返回结果])
```

**Diagram sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L37-L55)

### KDJ指标计算

KDJ指标通过计算未成熟随机值（RSV）并进行平滑处理，生成K、D、J三条线来判断市场状态。

```mermaid
flowchart TD
Start([开始]) --> ValidateData["验证数据长度"]
ValidateData --> DataValid{"数据长度>=9?"}
DataValid --> |否| Return50["返回50.0"]
DataValid --> |是| CalculateRSV["计算9日RSV"]
CalculateRSV --> Initialize["初始化K=50,D=50"]
Initialize --> Loop["遍历RSV序列"]
Loop --> UpdateK["更新K值"]
UpdateK --> UpdateD["更新D值"]
UpdateD --> UpdateJ["更新J值"]
Loop --> EndLoop{"遍历完成?"}
EndLoop --> |否| Loop
EndLoop --> |是| Round["四舍五入保留2位小数"]
Round --> End([返回结果])
```

**Diagram sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L57-L75)

### 布林带计算

布林带通过计算移动平均线和标准差，形成上轨、中轨和下轨三条轨道来判断价格波动范围。

```mermaid
flowchart TD
Start([开始]) --> ValidateData["验证数据长度"]
ValidateData --> DataValid{"数据长度>=20?"}
DataValid --> |否| ReturnZero["返回0.0"]
DataValid --> |是| CalculateMA["计算20日移动平均"]
CalculateMA --> CalculateStd["计算标准差"]
CalculateStd --> CalculateUpper["计算上轨: MA+2*Std"]
CalculateUpper --> CalculateLower["计算下轨: MA-2*Std"]
CalculateLower --> Round["四舍五入保留2位小数"]
Round --> End([返回结果])
```

**Diagram sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L77-L90)

**Section sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L20-L90)

## 价格预测接口

`/api/analysis/prediction/{stock_code}` 接口提供基于历史数据的价格预测功能，支持1-365天的预测周期。

### 预测算法原理

价格预测采用线性回归模型结合技术指标置信度评估的方法。首先通过线性回归计算价格趋势，然后结合技术指标的一致性来评估预测的置信度。

```mermaid
classDiagram
class PricePrediction {
+predict_price(historical_data, days) Dict
-calculate_confidence(rsi, macd, slope) float
}
class TechnicalIndicators {
+calculate_rsi(prices) float
+calculate_macd(prices) Dict
}
PricePrediction --> TechnicalIndicators : "使用"
```

**Diagram sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L92-L150)

### 置信度评估机制

预测置信度基于技术指标的一致性进行评估，基础置信度为50%，根据各指标信号进行调整：

- **RSI调整**：30-70区间增加10%，超买超卖减少5%
- **MACD调整**：金叉增加15%，死叉减少10%
- **趋势调整**：上升趋势增加10%，下降趋势减少10%

最终置信度限制在0-100%范围内。

```mermaid
flowchart TD
Start([开始]) --> BaseConfidence["基础置信度=50%"]
BaseConfidence --> RSIAdjust["RSI调整"]
RSIAdjust --> MACDAdjust["MACD调整"]
MACDAdjust --> TrendAdjust["趋势调整"]
TrendAdjust --> LimitRange["限制在0-100%"]
LimitRange --> End([返回置信度])
```

**Diagram sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L135-L150)

**Section sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L92-L150)

## 交易建议接口

`/api/analysis/recommendation/{stock_code}` 接口根据综合技术分析生成交易建议，包括买入、卖出或持有操作。

### 决策流程

交易建议的生成基于多指标信号的综合分析，每个技术指标产生一个信号，系统根据信号的强度和一致性做出决策。

```mermaid
flowchart TD
Start([开始]) --> CollectData["收集历史数据"]
CollectData --> CalculateIndicators["计算技术指标"]
CalculateIndicators --> AnalyzeSignals["分析各指标信号"]
AnalyzeSignals --> CountSignals["统计多空信号数量"]
CountSignals --> GenerateAction["生成交易建议"]
GenerateAction --> DetermineRisk["确定风险等级"]
DetermineRisk --> End([返回建议])
```

**Diagram sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L152-L250)

### 风险等级评估标准

风险等级根据建议的强度来确定：

- **低风险**：强度≥80%
- **中风险**：强度≥60%
- **高风险**：强度<60%

建议强度由信号数量决定，每个有效信号增加25%强度，最多100%。

```mermaid
classDiagram
class TradingRecommendation {
+generate_recommendation(historical_data, current_price) Dict
-analyze_signals(rsi, macd, kdj, bb, current_price, volumes) Dict
-generate_action(signals) Dict
}
class TechnicalIndicators {
+calculate_rsi(prices) float
+calculate_macd(prices) Dict
+calculate_kdj(highs, lows, closes) Dict
+calculate_bollinger_bands(prices) Dict
}
TradingRecommendation --> TechnicalIndicators : "使用"
```

**Diagram sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L152-L250)

**Section sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L152-L250)

## 关键价位接口

`/api/analysis/levels/{stock_code}` 接口识别股票的关键支撑位和阻力位，为交易决策提供重要参考。

### 支撑位识别

支撑位的识别采用多维度综合方法，包括：

1. **重要低点**：基于成交量加权的局部最低点
2. **斐波那契回调位**：基于近期高低点的黄金分割位
3. **移动平均线**：5、10、20、30、60日均线
4. **心理价位**：整数价位和半整数价位
5. **布林带下轨**：价格波动的理论下限

```mermaid
flowchart TD
Start([开始]) --> FindSignificantLows["寻找重要低点"]
FindSignificantLows --> CalculateFibonacci["计算斐波那契位"]
CalculateFibonacci --> CalculateMA["计算移动平均线"]
CalculateMA --> CalculatePsychological["计算心理价位"]
CalculatePsychological --> CalculateBollinger["计算布林带下轨"]
CalculateBollinger --> FilterLevels["过滤和排序"]
FilterLevels --> RemoveDuplicates["去除重复"]
RemoveDuplicates --> SortDescending["按降序排列"]
SortDescending --> LimitResults["限制返回3个"]
LimitResults --> End([返回支撑位])
```

**Diagram sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L252-L450)

### 阻力位识别

阻力位的识别方法与支撑位类似，但方向相反：

1. **重要高点**：基于成交量加权的局部最高点
2. **斐波那契扩展位**：基于近期高低点的黄金分割位
3. **移动平均线**：5、10、20、30、60日均线
4. **心理价位**：整数价位和半整数价位
5. **布林带上轨**：价格波动的理论上限

```mermaid
flowchart TD
Start([开始]) --> FindSignificantHighs["寻找重要高点"]
FindSignificantHighs --> CalculateFibonacci["计算斐波那契位"]
CalculateFibonacci --> CalculateMA["计算移动平均线"]
CalculateMA --> CalculatePsychological["计算心理价位"]
CalculatePsychological --> CalculateBollinger["计算布林带上轨"]
CalculateBollinger --> FilterLevels["过滤和排序"]
FilterLevels --> RemoveDuplicates["去除重复"]
RemoveDuplicates --> SortAscending["按升序排列"]
SortAscending --> LimitResults["限制返回3个"]
LimitResults --> End([返回阻力位])
```

**Diagram sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L252-L450)

**Section sources**  
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L252-L450)

## 分析摘要接口

`/api/analysis/summary/{stock_code}` 接口提供简化版的分析摘要，聚合核心指标便于快速查看。

### 摘要内容

分析摘要包含以下关键信息：

- **股票基本信息**：股票代码、当前价格
- **价格预测**：目标价格、预期涨跌幅、置信度
- **交易建议**：操作建议、风险等级、建议强度
- **技术摘要**：RSI、MACD、KDJ信号
- **分析时间**：结果生成时间

```mermaid
classDiagram
class AnalysisSummary {
+stock_code : str
+current_price : float
+prediction : Dict
+recommendation : Dict
+technical_summary : Dict
+analysis_time : str
}
class Prediction {
+target_price : float
+change_percent : float
+confidence : float
}
class Recommendation {
+action : str
+risk_level : str
+strength : int
}
class TechnicalSummary {
+rsi : str
+macd : str
+kdj : str
}
AnalysisSummary --> Prediction
AnalysisSummary --> Recommendation
AnalysisSummary --> TechnicalSummary
```

**Diagram sources**  
- [stock_analysis_routes.py](file://backend_api/stock/stock_analysis_routes.py#L220-L270)

**Section sources**  
- [stock_analysis_routes.py](file://backend_api/stock/stock_analysis_routes.py#L220-L270)

## 输入验证与错误处理

API实现了全面的输入验证和错误处理机制，确保系统的稳定性和可靠性。

### 输入验证

所有接口都对股票代码进行格式验证，要求必须是6位数字：

```mermaid
flowchart TD
Start([开始]) --> ValidateStockCode["验证股票代码"]
ValidateStockCode --> CodeValid{"代码存在且长度=6?"}
CodeValid --> |否| ReturnError["返回400错误"]
CodeValid --> |是| Continue["继续处理"]
```

**Section sources**  
- [stock_analysis_routes.py](file://backend_api/stock/stock_analysis_routes.py#L20-L25)

### 错误处理

系统采用统一的错误处理策略，所有异常都会被捕获并记录日志，然后返回标准化的错误响应：

```mermaid
sequenceDiagram
participant Client as "客户端"
participant Endpoint as "API端点"
participant Logger as "日志系统"
Client->>Endpoint : 发送请求
Endpoint->>Endpoint : 执行业务逻辑
alt 发生异常
Endpoint->>Logger : 记录错误日志
Logger-->>Endpoint : 确认记录
Endpoint-->>Client : 返回500错误
else 正常执行
Endpoint-->>Client : 返回200成功
end
```

**Diagram sources**  
- [stock_analysis_routes.py](file://backend_api/stock/stock_analysis_routes.py#L25-L45)

**Section sources**  
- [stock_analysis_routes.py](file://backend_api/stock/stock_analysis_routes.py#L25-L45)

## 性能与缓存策略

### 性能监控

虽然当前代码中没有显式的性能监控代码，但系统通过日志记录了关键操作的执行情况，为性能分析提供了基础数据。

### 缓存策略

当前实现中未包含显式的缓存机制。所有请求都会实时计算分析结果，这确保了数据的实时性，但可能影响高并发场景下的性能表现。

**Section sources**  
- [stock_analysis_routes.py](file://backend_api/stock/stock_analysis_routes.py#L1-L270)
- [stock_analysis.py](file://backend_api/stock/stock_analysis.py#L1-L805)