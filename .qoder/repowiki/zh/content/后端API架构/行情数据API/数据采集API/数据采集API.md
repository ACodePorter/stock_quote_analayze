# 数据采集API

<cite>
**本文档中引用的文件**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py)
- [models.py](file://backend_api/models.py)
- [database.py](file://backend_api/database.py)
</cite>

## 目录
1. [简介](#简介)
2. [核心组件](#核心组件)
3. [架构概述](#架构概述)
4. [详细组件分析](#详细组件分析)
5. [依赖分析](#依赖分析)
6. [性能考虑](#性能考虑)
7. [故障排除指南](#故障排除指南)
8. [结论](#结论)

## 简介
本文档全面解析了基于FastAPI实现的数据采集API系统，重点阐述了历史数据采集任务的管理机制。该系统通过`/start_historical_collection`接口启动后台任务，利用线程锁实现并发控制，并通过`AkshareDataCollector`类完成股票数据的批量采集。文档详细说明了任务状态查询、任务列表管理和任务取消等核心功能，以及任务状态存储、线程安全和数据库会话管理的最佳实践。

## 核心组件

本系统的核心组件包括数据采集请求/响应模型、任务状态管理机制、Akshare数据采集器以及后台任务执行流程。这些组件协同工作，实现了安全、可靠的历史数据采集功能。

**Section sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L1-L645)
- [models.py](file://backend_api/models.py#L401-L434)

## 架构概述

该数据采集API采用分层架构设计，包含API路由层、业务逻辑层和数据访问层。系统通过全局变量管理任务状态，使用线程锁确保线程安全，并通过后台任务机制实现异步数据采集。

```mermaid
graph TB
subgraph "API层"
A[/start_historical_collection\nPOST /historical/]
B[/get_collection_status\nGET /status/{task_id}/]
C[/list_collection_tasks\nGET /tasks/]
D[/cancel_collection_task\nDELETE /tasks/{task_id}/]
end
subgraph "业务逻辑层"
E[AkshareDataCollector]
F[run_historical_collection_task]
end
subgraph "数据层"
G[stock_basic_info表]
H[historical_quotes表]
I[historical_collect_operation_logs表]
end
A --> E
B --> collection_tasks
C --> collection_tasks
D --> collection_tasks
E --> G
E --> H
E --> I
F --> E
collection_tasks[(collection_tasks\n字典)]
task_lock[(task_lock\n线程锁)]
current_task_id[(current_task_id\n当前任务ID)]
style collection_tasks fill:#f9f,stroke:#333
style task_lock fill:#f9f,stroke:#333
style current_task_id fill:#f9f,stroke:#333
```

**Diagram sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L1-L645)

## 详细组件分析

### 历史数据采集接口分析

`/start_historical_collection`接口是启动历史数据采集任务的入口点，它实现了任务ID生成、并发控制和后台任务调度等关键功能。

```mermaid
sequenceDiagram
participant Client as "客户端"
participant API as "start_historical_collection"
participant Lock as "task_execution_lock"
participant TaskManager as "collection_tasks"
participant Background as "BackgroundTasks"
participant Runner as "run_historical_collection_task"
Client->>API : POST /historical/
API->>API : 验证日期格式
API->>Lock : 获取锁
Lock-->>API : 锁定
API->>API : 检查current_task_id
alt 有任务正在运行
API-->>Client : HTTP 400错误
else 无任务运行
API->>API : 生成task_id
API->>TaskManager : 初始化任务状态
API->>Lock : 设置current_task_id
API->>Background : 添加后台任务
Background->>Runner : 执行采集任务
API-->>Client : 返回启动响应
end
Lock->>API : 释放锁
```

**Diagram sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L300-L350)

**Section sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L300-L350)

### AkshareDataCollector类分析

`AkshareDataCollector`类是数据采集的核心业务逻辑组件，负责股票列表获取、已存在数据检查、单只股票数据采集和全量采集标志更新等功能。

```mermaid
classDiagram
class AkshareDataCollector {
+session : Session
+collected_count : int
+skipped_count : int
+failed_count : int
+failed_stocks : List[str]
+__init__(db_session : Session)
+get_stock_list(only_uncompleted : bool) : List[Dict]
+check_existing_data(stock_code : str, start_date : str, end_date : str) : List[str]
+collect_single_stock_data(stock_code : str, stock_name : str, start_date : str, end_date : str) : bool
+collect_historical_data(start_date : str, end_date : str, stock_codes : List[str], full_collection_mode : bool) : Dict
+_update_full_collection_flag(stock_code : str, start_date : str, end_date : str)
+_log_collection_result(start_date : str, end_date : str, total_stocks : int, success_stocks : int)
}
class DataCollectionRequest {
+start_date : str
+end_date : str
+stock_codes : Optional[List[str]]
+test_mode : bool
+full_collection_mode : bool
}
class DataCollectionResponse {
+task_id : str
+status : str
+message : str
+start_date : str
+end_date : str
+stock_codes : Optional[List[str]]
+test_mode : bool
+full_collection_mode : bool
}
class DataCollectionStatus {
+task_id : str
+status : str
+progress : int
+total_stocks : int
+processed_stocks : int
+success_count : int
+failed_count : int
+collected_count : int
+skipped_count : int
+start_time : datetime
+end_time : Optional[datetime]
+error_message : Optional[str]
+failed_details : List[str]
}
AkshareDataCollector --> DataCollectionRequest : "使用"
AkshareDataCollector --> DataCollectionResponse : "返回"
AkshareDataCollector --> DataCollectionStatus : "更新"
```

**Diagram sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L100-L290)
- [models.py](file://backend_api/models.py#L401-L434)

**Section sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L100-L290)

### 后台任务执行流程分析

`run_historical_collection_task`函数定义了后台任务的执行流程，包括重试机制和随机延迟以避免API限流。

```mermaid
flowchart TD
Start([开始执行任务]) --> CreateDB["创建数据库会话"]
CreateDB --> CreateCollector["创建AkshareDataCollector"]
CreateCollector --> CheckMode{"测试模式?"}
CheckMode --> |是| LimitStocks["只采集前5只股票"]
CheckMode --> |否| GetAllStocks["获取所有股票列表"]
LimitStocks --> UpdateStatus["更新任务状态"]
GetAllStocks --> UpdateStatus
UpdateStatus --> ExecuteCollect["执行collect_historical_data"]
ExecuteCollect --> CheckResult{"采集成功?"}
CheckResult --> |是| UpdateSuccess["更新成功状态"]
CheckResult --> |否| UpdateFail["更新失败状态"]
UpdateSuccess --> CloseDB["关闭数据库会话"]
UpdateFail --> CloseDB
CloseDB --> ClearTask["清除current_task_id"]
ClearTask --> End([任务结束])
style Start fill:#9f9,stroke:#333
style End fill:#9f9,stroke:#333
```

**Diagram sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L352-L400)

**Section sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L352-L400)

### 任务状态管理接口分析

系统提供了多个接口用于任务状态的实时查询和管理，包括获取任务状态、列出所有任务和取消任务。

```mermaid
sequenceDiagram
participant Client as "客户端"
participant StatusAPI as "get_collection_status"
participant TasksAPI as "list_collection_tasks"
participant CancelAPI as "cancel_collection_task"
participant TaskManager as "collection_tasks"
participant Lock as "task_lock"
Client->>StatusAPI : GET /status/{task_id}
StatusAPI->>Lock : 获取锁
Lock-->>StatusAPI : 锁定
StatusAPI->>TaskManager : 查找任务
alt 任务存在
StatusAPI->>StatusAPI : 计算进度
StatusAPI-->>Client : 返回状态信息
else 任务不存在
StatusAPI-->>Client : HTTP 404错误
end
Lock->>StatusAPI : 释放锁
Client->>TasksAPI : GET /tasks
TasksAPI->>Lock : 获取锁
Lock-->>TasksAPI : 锁定
TasksAPI->>TaskManager : 获取所有任务
TasksAPI->>TasksAPI : 计算各任务进度
TasksAPI->>TasksAPI : 按开始时间倒序排列
TasksAPI-->>Client : 返回任务列表
Lock->>TasksAPI : 释放锁
Client->>CancelAPI : DELETE /tasks/{task_id}
CancelAPI->>Lock : 获取锁
Lock-->>CancelAPI : 锁定
CancelAPI->>TaskManager : 查找任务
alt 任务存在
CancelAPI->>CancelAPI : 检查任务状态
alt 任务进行中
CancelAPI->>TaskManager : 更新为取消状态
CancelAPI->>task_execution_lock : 清除current_task_id
CancelAPI-->>Client : 返回取消成功
else 任务已完成
CancelAPI-->>Client : HTTP 400错误
end
else 任务不存在
CancelAPI-->>Client : HTTP 404错误
end
Lock->>CancelAPI : 释放锁
```

**Diagram sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L402-L550)

**Section sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L402-L550)

## 依赖分析

该数据采集API系统依赖于多个核心组件和外部库，形成了一个完整的数据采集生态系统。

```mermaid
graph TD
A[data_collection_api.py] --> B[FastAPI]
A --> C[SQLAlchemy]
A --> D[akshare]
A --> E[pandas]
A --> F[backend_api.database]
A --> G[backend_api.models]
B --> H[Starlette]
C --> I[SQLAlchemy Core]
D --> J[requests]
D --> K[pandas]
F --> L[DATABASE_CONFIG]
G --> M[Pydantic]
A --> N[threading]
A --> O[logging]
style A fill:#f96,stroke:#333
style B fill:#69f,stroke:#333
style C fill:#69f,stroke:#333
style D fill:#69f,stroke:#333
style F fill:#69f,stroke:#333
style G fill:#69f,stroke:#333
```

**Diagram sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L1-L20)
- [models.py](file://backend_api/models.py#L1-L10)
- [database.py](file://backend_api/database.py#L1-L10)

**Section sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L1-L20)

## 性能考虑

在数据采集过程中，系统实施了多项性能优化措施，以确保高效、稳定地完成大规模数据采集任务。

1. **数据库会话管理**：每个后台任务创建独立的数据库会话，并在任务完成后正确关闭，避免连接泄漏。
2. **请求频率控制**：在采集单只股票数据后添加随机延迟（0.5-1.5秒），避免对akshare API造成过大压力。
3. **批量处理优化**：在数据库操作中采用批量提交策略，减少事务开销。
4. **内存使用控制**：通过分批处理股票列表，避免一次性加载过多数据到内存中。
5. **错误重试机制**：实现三次重试机制，每次重试间隔逐渐增加，提高采集成功率。

**Section sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L200-L250)

## 故障排除指南

当数据采集任务出现问题时，可以参考以下常见问题及解决方案：

```mermaid
flowchart TD
A[任务无法启动] --> B{"检查current_task_id"}
B --> |不为空| C[等待当前任务完成]
B --> |为空| D[检查请求参数]
E[采集速度过慢] --> F[检查网络连接]
F --> G[优化数据库性能]
G --> H[调整采集间隔]
I[部分股票采集失败] --> J[检查akshare API状态]
J --> K[查看失败详情日志]
K --> L[手动重试失败股票]
M[数据库连接错误] --> N[检查DATABASE_CONFIG]
N --> O[验证数据库服务状态]
O --> P[检查连接池配置]
Q[任务状态不更新] --> R[检查task_lock同步]
R --> S[验证后台任务是否正常执行]
S --> T[查看系统日志]
style A fill:#f99,stroke:#333
style E fill:#f99,stroke:#333
style I fill:#f99,stroke:#333
style M fill:#f99,stroke:#333
style Q fill:#f99,stroke:#333
```

**Section sources**
- [data_collection_api.py](file://backend_api/stock/data_collection_api.py#L300-L550)

## 结论

本文档全面解析了数据采集API的设计与实现，重点阐述了后台任务管理机制、并发控制策略和数据采集流程。系统通过精心设计的架构和实现，确保了历史数据采集任务的安全性、可靠性和效率。`AkshareDataCollector`类封装了核心采集逻辑，而全局任务状态管理机制则提供了完善的任务监控能力。通过合理的线程安全措施和数据库会话管理，系统能够在高并发环境下稳定运行。未来可进一步优化的方向包括引入更智能的重试策略、实现分布式任务调度以及增强任务状态的持久化能力。