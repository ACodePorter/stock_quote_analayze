# API参考文档

<cite>
**本文档中引用的文件**  
- [main.py](file://backend_api/main.py)
- [auth_routes.py](file://backend_api/auth_routes.py)
- [users.py](file://backend_api/admin/users.py)
- [quotes_routes.py](file://backend_api/quotes_routes.py)
- [history_api.py](file://backend_api/stock/history_api.py)
- [logs.py](file://backend_api/admin/logs.py)
- [api.ts](file://admin/src/services/api.ts)
</cite>

## 目录
1. [简介](#简介)
2. [认证API](#认证api)
3. [用户管理API](#用户管理api)
4. [股票行情API](#股票行情api)
5. [历史数据API](#历史数据api)
6. [系统日志API](#系统日志api)
7. [错误码体系](#错误码体系)
8. [前端调用示例](#前端调用示例)

## 简介
本API参考文档详细描述了股票分析系统的后端RESTful API接口。文档覆盖了用户认证、用户管理、股票实时行情、历史数据查询、技术分析计算以及系统日志监控等核心功能模块。所有API均基于FastAPI框架构建，采用Bearer Token认证机制，返回JSON格式数据。

## 认证API

### 用户登录
- **HTTP方法**: `POST`
- **URL路径**: `/api/auth/login`
- **请求头**: 
  - `Content-Type: application/json`
- **请求参数（Body）**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **响应格式（200 OK）**:
  ```json
  {
    "access_token": "string",
    "token_type": "bearer",
    "user": {
      "id": 0,
      "username": "string",
      "email": "string",
      "role": "string",
      "status": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  }
  ```
- **curl命令示例**:
  ```bash
  curl -X POST "http://localhost:5000/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"password"}'
  ```
- **响应示例**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "status": "active",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  }
  ```

### 获取认证状态
- **HTTP方法**: `GET`
- **URL路径**: `/api/auth/status`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **响应格式（200 OK）**:
  ```json
  {
    "success": true,
    "logged_in": true,
    "user": {
      "id": 0,
      "username": "string",
      "email": "string",
      "role": "string",
      "status": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  }
  ```
- **curl命令示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/auth/status" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx"
  ```

### 用户登出
- **HTTP方法**: `POST`
- **URL路径**: `/api/auth/logout`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **响应格式（200 OK）**:
  ```json
  {
    "success": true,
    "message": "已成功登出"
  }
  ```

**本节来源**
- [auth_routes.py](file://backend_api/auth_routes.py#L150-L331)

## 用户管理API

### 获取用户列表
- **HTTP方法**: `GET`
- **URL路径**: `/api/admin/users`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **请求参数（查询参数）**:
  - `skip`: 整数，跳过记录数，默认0
  - `limit`: 整数，每页数量，默认20
  - `search`: 字符串，搜索关键词
- **响应格式（200 OK）**:
  ```json
  {
    "data": [
      {
        "id": 0,
        "username": "string",
        "email": "string",
        "role": "string",
        "status": "string",
        "created_at": "string",
        "updated_at": "string"
      }
    ],
    "total": 0,
    "page": 0,
    "pageSize": 0
  }
  ```
- **curl命令示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/admin/users?skip=0&limit=10&search=admin" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx"
  ```

### 创建用户
- **HTTP方法**: `POST`
- **URL路径**: `/api/admin/users`
- **请求头**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **请求参数（Body）**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "role": "string"
  }
  ```
- **响应格式（201 Created）**:
  ```json
  {
    "id": 0,
    "username": "string",
    "email": "string",
    "role": "string",
    "status": "string",
    "created_at": "string",
    "updated_at": "string"
  }
  ```

### 更新用户信息
- **HTTP方法**: `PUT`
- **URL路径**: `/api/admin/users/{user_id}`
- **请求头**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **请求参数（路径参数）**:
  - `user_id`: 整数，用户ID
- **请求参数（Body）**:
  ```json
  {
    "username": "string",
    "email": "string",
    "role": "string",
    "status": "string"
  }
  ```
- **响应格式（200 OK）**:
  ```json
  {
    "id": 0,
    "username": "string",
    "email": "string",
    "role": "string",
    "status": "string",
    "created_at": "string",
    "updated_at": "string"
  }
  ```

### 更新用户状态
- **HTTP方法**: `PUT`
- **URL路径**: `/api/admin/users/{user_id}/status`
- **请求头**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **请求参数（路径参数）**:
  - `user_id`: 整数，用户ID
- **请求参数（查询参数）**:
  - `status`: 字符串，状态值（active, disabled, suspended）
- **响应格式（200 OK）**:
  ```json
  {
    "message": "用户状态已更新为active"
  }
  ```

### 删除用户
- **HTTP方法**: `DELETE`
- **URL路径**: `/api/admin/users/{user_id}`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **请求参数（路径参数）**:
  - `user_id`: 整数，用户ID
- **响应格式（200 OK）**:
  ```json
  {
    "message": "用户删除成功"
  }
  ```

### 获取用户统计信息
- **HTTP方法**: `GET`
- **URL路径**: `/api/admin/users/stats`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **响应格式（200 OK）**:
  ```json
  {
    "total": 0,
    "active": 0,
    "disabled": 0,
    "suspended": 0
  }
  ```

**本节来源**
- [users.py](file://backend_api/admin/users.py#L20-L197)

## 股票行情API

### 获取股票实时行情
- **HTTP方法**: `GET`
- **URL路径**: `/api/quotes/stocks`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **请求参数（查询参数）**:
  - `page`: 整数，页码，默认1
  - `page_size`: 整数，每页大小，默认20
  - `keyword`: 字符串，搜索关键词
  - `market`: 字符串，市场类型（sh, sz, cy, bj）
  - `sort_by`: 字符串，排序字段
- **响应格式（200 OK）**:
  ```json
  {
    "success": true,
    "data": [
      {
        "code": "string",
        "name": "string",
        "current_price": 0,
        "change_percent": 0,
        "volume": 0,
        "amount": 0,
        "high": 0,
        "low": 0,
        "open": 0,
        "pre_close": 0,
        "turnover_rate": 0,
        "pe_dynamic": 0,
        "total_market_value": 0,
        "pb_ratio": 0,
        "circulating_market_value": 0,
        "update_time": "string"
      }
    ],
    "total": 0,
    "page": 0,
    "page_size": 0
  }
  ```
- **curl命令示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/quotes/stocks?page=1&page_size=10&keyword=600&sort_by=change_percent" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx"
  ```

### 获取指数实时行情
- **HTTP方法**: `GET`
- **URL路径**: `/api/quotes/indices`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **请求参数（查询参数）**:
  - `page`: 整数，页码，默认1
  - `page_size`: 整数，每页大小，默认20
  - `keyword`: 字符串，搜索关键词
  - `sort_by`: 字符串，排序字段
- **响应格式（200 OK）**:
  ```json
  {
    "success": true,
    "data": [
      {
        "code": "string",
        "name": "string",
        "price": 0,
        "change": 0,
        "pct_chg": 0,
        "high": 0,
        "low": 0,
        "open": 0,
        "pre_close": 0,
        "volume": 0,
        "amount": 0,
        "amplitude": 0,
        "turnover": 0,
        "pe": 0,
        "volume_ratio": 0,
        "update_time": "string"
      }
    ],
    "total": 0,
    "page": 0,
    "page_size": 0
  }
  ```

### 获取行业板块实时行情
- **HTTP方法**: `GET`
- **URL路径**: `/api/quotes/industries`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **请求参数（查询参数）**:
  - `page`: 整数，页码，默认1
  - `page_size`: 整数，每页大小，默认20
  - `keyword`: 字符串，搜索关键词
  - `sort_by`: 字符串，排序字段
- **响应格式（200 OK）**:
  ```json
  {
    "success": true,
    "data": [
      {
        "name": "string",
        "price": 0,
        "change_percent": 0,
        "change_amount": 0,
        "total_market_value": 0,
        "volume": 0,
        "amount": 0,
        "turnover_rate": 0,
        "leading_stock": "string",
        "leading_stock_change": 0,
        "leading_stock_code": "string",
        "update_time": "string"
      }
    ],
    "total": 0,
    "page": 0,
    "page_size": 0
  }
  ```

### 获取行情数据统计
- **HTTP方法**: `GET`
- **URL路径**: `/api/quotes/stats`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **响应格式（200 OK）**:
  ```json
  {
    "success": true,
    "data": {
      "totalStocks": 0,
      "totalIndices": 0,
      "totalIndustries": 0,
      "lastUpdateTime": "string"
    }
  }
  ```

### 刷新行情数据
- **HTTP方法**: `POST`
- **URL路径**: `/api/quotes/refresh`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **响应格式（200 OK）**:
  ```json
  {
    "success": true,
    "message": "行情数据刷新任务已启动"
  }
  ```

**本节来源**
- [quotes_routes.py](file://backend_api/quotes_routes.py#L100-L581)

## 历史数据API

### 获取股票历史数据
- **HTTP方法**: `GET`
- **URL路径**: `/api/stock/history`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **请求参数（查询参数）**:
  - `code`: 字符串，股票代码（必填）
  - `start_date`: 字符串，开始日期（YYYY-MM-DD）
  - `end_date`: 字符串，结束日期（YYYY-MM-DD）
  - `page`: 整数，页码，默认1
  - `size`: 整数，每页大小，默认20
  - `include_notes`: 布尔值，是否包含交易备注，默认true
- **响应格式（200 OK）**:
  ```json
  {
    "items": [
      {
        "code": "string",
        "name": "string",
        "date": "string",
        "open": 0,
        "close": 0,
        "high": 0,
        "low": 0,
        "volume": 0,
        "amount": 0,
        "change_percent": 0,
        "change": 0,
        "turnover_rate": 0,
        "cumulative_change_percent": 0,
        "five_day_change_percent": 0,
        "ten_day_change_percent": 0,
        "sixty_day_change_percent": 0,
        "remarks": "string",
        "user_notes": "string",
        "strategy_type": "string",
        "risk_level": "string",
        "notes_creator": "string",
        "notes_created_at": "string",
        "notes_updated_at": "string"
      }
    ],
    "total": 0
  }
  ```
- **curl命令示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/stock/history?code=600519&start_date=2024-01-01&end_date=2024-01-31&page=1&size=10" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx"
  ```

### 导出股票历史数据
- **HTTP方法**: `GET`
- **URL路径**: `/api/stock/history/export`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **请求参数（查询参数）**:
  - `code`: 字符串，股票代码（必填）
  - `start_date`: 字符串，开始日期（YYYY-MM-DD）
  - `end_date`: 字符串，结束日期（YYYY-MM-DD）
  - `include_notes`: 布尔值，是否包含交易备注，默认true
- **响应格式（200 OK）**: CSV文件流
- **curl命令示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/stock/history/export?code=600519&start_date=2024-01-01&end_date=2024-01-31&include_notes=true" \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx" \
    -o 600519_historical_quotes.csv
  ```

### 计算5天升跌%
- **HTTP方法**: `POST`
- **URL路径**: `/api/stock/history/calculate_five_day_change`
- **请求头**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **请求参数（Body）**:
  ```json
  {
    "stock_code": "string",
    "start_date": "string",
    "end_date": "string"
  }
  ```
- **响应格式（200 OK）**:
  ```json
  {
    "message": "股票 600519 在 2024-01-01 到 2024-01-31 期间的5天升跌%计算完成",
    "stock_code": "string",
    "start_date": "string",
    "end_date": "string",
    "updated_count": 0,
    "total_records": 0
  }
  ```

### 计算10天涨跌%
- **HTTP方法**: `POST`
- **URL路径**: `/api/stock/history/calculate_ten_day_change`
- **请求头**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **请求参数（Body）**:
  ```json
  {
    "stock_code": "string",
    "start_date": "string",
    "end_date": "string"
  }
  ```
- **响应格式（200 OK）**:
  ```json
  {
    "message": "股票 600519 在 2024-01-01 到 2024-01-31 期间的10天涨跌%计算完成",
    "stock_code": "string",
    "start_date": "string",
    "end_date": "string",
    "updated_count": 0,
    "total_records": 0
  }
  ```

### 计算60天涨跌%
- **HTTP方法**: `POST`
- **URL路径**: `/api/stock/history/calculate_sixty_day_change`
- **请求头**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **请求参数（Body）**:
  ```json
  {
    "stock_code": "string",
    "start_date": "string",
    "end_date": "string"
  }
  ```
- **响应格式（200 OK）**:
  ```json
  {
    "message": "股票 600519 在 2024-01-01 到 2024-01-31 期间的60天涨跌%计算完成",
    "stock_code": "string",
    "start_date": "string",
    "end_date": "string",
    "updated_count": 0,
    "total_records": 0
  }
  ```

**本节来源**
- [history_api.py](file://backend_api/stock/history_api.py#L50-L602)

## 系统日志API

### 获取日志表列表
- **HTTP方法**: `GET`
- **URL路径**: `/api/admin/logs/tables`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **响应格式（200 OK）**:
  ```json
  {
    "tables": [
      {
        "key": "string",
        "display_name": "string",
        "table_name": "string"
      }
    ]
  }
  ```

### 获取全局统计信息
- **HTTP方法**: `GET`
- **URL路径**: `/api/admin/logs/stats`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **响应格式（200 OK）**:
  ```json
  {
    "historical_collect": {
      "table_name": "string",
      "total_count": 0,
      "today_count": 0,
      "error_count": 0
    },
    "realtime_collect": {
      "table_name": "string",
      "total_count": 0,
      "today_count": 0,
      "error_count": 0
    },
    "operation": {
      "table_name": "string",
      "total_count": 0,
      "today_count": 0,
      "error_count": 0
    },
    "watchlist_history": {
      "table_name": "string",
      "total_count": 0,
      "today_count": 0,
      "error_count": 0
    }
  }
  ```

### 查询日志数据
- **HTTP方法**: `GET`
- **URL路径**: `/api/admin/logs/query/{table_key}`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **请求参数（路径参数）**:
  - `table_key`: 字符串，日志表键名
- **请求参数（查询参数）**:
  - `page`: 整数，页码，默认1
  - `page_size`: 整数，每页大小，默认20
  - `start_date`: 字符串，开始日期（YYYY-MM-DD）
  - `end_date`: 字符串，结束日期（YYYY-MM-DD）
  - `status`: 字符串，状态筛选
  - `operation_type`: 字符串，操作类型筛选
  - `stock_code`: 字符串，股票代码筛选（仅适用于自选股历史采集日志）
- **响应格式（200 OK）**:
  ```json
  {
    "table_key": "string",
    "table_name": "string",
    "data": [
      {
        "id": 0,
        "operation_type": "string",
        "operation_desc": "string",
        "affected_rows": 0,
        "status": "string",
        "error_message": "string",
        "created_at": "string"
      }
    ],
    "total": 0,
    "page": 0,
    "pageSize": 0
  }
  ```

### 获取日志统计信息
- **HTTP方法**: `GET`
- **URL路径**: `/api/admin/logs/stats/{table_key}`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **请求参数（路径参数）**:
  - `table_key`: 字符串，日志表键名
- **请求参数（查询参数）**:
  - `days`: 整数，统计天数
- **响应格式（200 OK）**:
  ```json
  {
    "table_key": "string",
    "table_name": "string",
    "period_days": 0,
    "is_all_data": false,
    "status_stats": [
      {
        "status": "string",
        "count": 0
      }
    ],
    "daily_stats": [
      {
        "date": "string",
        "total_count": 0,
        "success_count": 0,
        "error_count": 0
      }
    ],
    "operation_stats": [
      {
        "operation_type": "string",
        "count": 0
      }
    ]
  }
  ```

### 获取最近日志记录
- **HTTP方法**: `GET`
- **URL路径**: `/api/admin/logs/recent/{table_key}`
- **请求头**: 
  - `Authorization: Bearer <token>`
- **请求参数（路径参数）**:
  - `table_key`: 字符串，日志表键名
- **请求参数（查询参数）**:
  - `limit`: 整数，记录数量，默认10
- **响应格式（200 OK）**:
  ```json
  {
    "table_key": "string",
    "table_name": "string",
    "data": [
      {
        "id": 0,
        "operation_type": "string",
        "operation_desc": "string",
        "affected_rows": 0,
        "status": "string",
        "error_message": "string",
        "created_at": "string"
      }
    ]
  }
  ```

**本节来源**
- [logs.py](file://backend_api/admin/logs.py#L50-L385)

## 错误码体系
本系统采用标准HTTP状态码和自定义错误信息相结合的方式进行错误处理：

- **400 Bad Request**: 请求参数无效或缺失
  - 示例：`{"detail":"日期格式无效"}`
- **401 Unauthorized**: 未授权访问，认证失败
  - 示例：`{"detail":"用户名或密码错误"}`
- **403 Forbidden**: 禁止访问，权限不足
  - 示例：`{"detail":"账号已被禁用"}`
- **404 Not Found**: 资源未找到
  - 示例：`{"detail":"用户不存在"}`
- **500 Internal Server Error**: 服务器内部错误
  - 示例：`{"detail":"获取股票行情数据失败: database error"}`

所有错误响应均包含`detail`字段，提供具体的错误信息。

## 前端调用示例
以下示例展示了前端`api.ts`服务类如何调用后端API：

```typescript
// api.ts中的服务类
class ApiService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 请求拦截器 - 自动添加认证token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('admin_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // 响应拦截器 - 处理401未授权
    this.api.interceptors.response.use(
      (response) => response.data,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('admin_token')
          localStorage.removeItem('admin_user')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.api.get(url, config)
  }

  post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.api.post(url, data, config)
  }
}

export const apiService = new ApiService()
```

**本节来源**
- [api.ts](file://admin/src/services/api.ts#L1-L75)