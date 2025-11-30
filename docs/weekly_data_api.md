# 周线数据API接口设计文档

## 1. 概述

本文档定义了周线数据的API接口规范，供前端调用展示周线K线图和进行技术分析。

## 2. 接口列表

### 2.1 获取股票周线数据

#### 接口信息
- **接口路径**: `/api/quotes/weekly/{stock_code}`
- **请求方法**: GET
- **接口说明**: 获取指定股票的周线数据

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| stock_code | string | 是 | 股票代码 | 000001 |
| start_date | string | 否 | 开始日期 | 2025-01-01 |
| end_date | string | 否 | 结束日期 | 2025-11-30 |
| limit | integer | 否 | 返回记录数，默认100 | 100 |

#### 请求示例

```bash
GET /api/quotes/weekly/000001?start_date=2025-01-01&end_date=2025-11-30
```

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 状态码，200表示成功 |
| message | string | 响应消息 |
| data | array | 周线数据列表 |
| data[].code | string | 股票代码 |
| data[].name | string | 股票名称 |
| data[].date | string | 周线日期（周五） |
| data[].open | float | 开盘价 |
| data[].high | float | 最高价 |
| data[].low | float | 最低价 |
| data[].close | float | 收盘价 |
| data[].volume | float | 成交量 |
| data[].amount | float | 成交额 |
| data[].change_percent | float | 涨跌幅(%) |
| data[].change | float | 涨跌额 |
| data[].amplitude | float | 振幅(%) |

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "code": "000001",
      "name": "平安银行",
      "date": "2025-11-28",
      "open": 12.50,
      "high": 13.20,
      "low": 12.30,
      "close": 13.00,
      "volume": 150000000,
      "amount": 1950000000,
      "change_percent": 4.00,
      "change": 0.50,
      "amplitude": 7.20
    },
    {
      "code": "000001",
      "name": "平安银行",
      "date": "2025-11-21",
      "open": 12.30,
      "high": 12.80,
      "low": 12.10,
      "close": 12.50,
      "volume": 120000000,
      "amount": 1500000000,
      "change_percent": 1.63,
      "change": 0.20,
      "amplitude": 5.69
    }
  ]
}
```

### 2.2 批量获取周线数据

#### 接口信息
- **接口路径**: `/api/quotes/weekly/batch`
- **请求方法**: POST
- **接口说明**: 批量获取多只股票的周线数据

#### 请求参数

```json
{
  "stock_codes": ["000001", "600000", "000002"],
  "start_date": "2025-01-01",
  "end_date": "2025-11-30",
  "limit": 100
}
```

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "000001": [...],
    "600000": [...],
    "000002": [...]
  }
}
```

### 2.3 获取最新周线数据

#### 接口信息
- **接口路径**: `/api/quotes/weekly/{stock_code}/latest`
- **请求方法**: GET
- **接口说明**: 获取指定股票的最新一周数据

#### 请求示例

```bash
GET /api/quotes/weekly/000001/latest
```

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "code": "000001",
    "name": "平安银行",
    "date": "2025-11-28",
    "open": 12.50,
    "high": 13.20,
    "low": 12.30,
    "close": 13.00,
    "volume": 150000000,
    "amount": 1950000000,
    "change_percent": 4.00,
    "change": 0.50,
    "amplitude": 7.20
  }
}
```

## 3. 后端实现示例

### 3.1 FastAPI 路由定义

```python
# backend_api/routes/weekly_quotes.py

from fastapi import APIRouter, Query
from typing import Optional, List
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/quotes/weekly", tags=["周线数据"])

@router.get("/{stock_code}")
async def get_weekly_quotes(
    stock_code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=1000)
):
    """获取股票周线数据"""
    try:
        # 默认查询最近100周
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(weeks=100)).strftime('%Y-%m-%d')
        
        # 查询数据库
        session = SessionLocal()
        query = text("""
            SELECT code, name, date, open, high, low, close, 
                   volume, amount, change_percent, change, amplitude
            FROM weekly_quotes
            WHERE code = :code 
              AND date >= :start_date 
              AND date <= :end_date
            ORDER BY date DESC
            LIMIT :limit
        """)
        
        result = session.execute(query, {
            'code': stock_code,
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit
        })
        
        data = []
        for row in result.fetchall():
            data.append({
                'code': row[0],
                'name': row[1],
                'date': row[2],
                'open': row[3],
                'high': row[4],
                'low': row[5],
                'close': row[6],
                'volume': row[7],
                'amount': row[8],
                'change_percent': row[9],
                'change': row[10],
                'amplitude': row[11]
            })
        
        session.close()
        
        return {
            'code': 200,
            'message': 'success',
            'data': data
        }
        
    except Exception as e:
        return {
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': []
        }

@router.post("/batch")
async def get_batch_weekly_quotes(request: dict):
    """批量获取周线数据"""
    stock_codes = request.get('stock_codes', [])
    start_date = request.get('start_date')
    end_date = request.get('end_date')
    limit = request.get('limit', 100)
    
    result_data = {}
    for code in stock_codes:
        # 调用单个查询接口
        response = await get_weekly_quotes(code, start_date, end_date, limit)
        result_data[code] = response['data']
    
    return {
        'code': 200,
        'message': 'success',
        'data': result_data
    }

@router.get("/{stock_code}/latest")
async def get_latest_weekly_quote(stock_code: str):
    """获取最新周线数据"""
    response = await get_weekly_quotes(stock_code, limit=1)
    
    if response['code'] == 200 and response['data']:
        return {
            'code': 200,
            'message': 'success',
            'data': response['data'][0]
        }
    else:
        return {
            'code': 404,
            'message': '未找到数据',
            'data': None
        }
```

### 3.2 注册路由

```python
# backend_api/main.py

from fastapi import FastAPI
from backend_api.routes import weekly_quotes

app = FastAPI()

# 注册周线数据路由
app.include_router(weekly_quotes.router)
```

## 4. 前端调用示例

### 4.1 JavaScript/Axios

```javascript
// 获取周线数据
async function getWeeklyQuotes(stockCode, startDate, endDate) {
  try {
    const response = await axios.get(`/api/quotes/weekly/${stockCode}`, {
      params: {
        start_date: startDate,
        end_date: endDate,
        limit: 100
      }
    });
    
    if (response.data.code === 200) {
      return response.data.data;
    } else {
      console.error('获取周线数据失败:', response.data.message);
      return [];
    }
  } catch (error) {
    console.error('请求失败:', error);
    return [];
  }
}

// 使用示例
const weeklyData = await getWeeklyQuotes('000001', '2025-01-01', '2025-11-30');
console.log(weeklyData);
```

### 4.2 ECharts K线图展示

```javascript
// 将周线数据转换为 ECharts 格式
function convertToEChartsFormat(weeklyData) {
  const dates = [];
  const klineData = [];
  const volumes = [];
  
  // 数据需要按时间正序排列
  const sortedData = weeklyData.sort((a, b) => 
    new Date(a.date) - new Date(b.date)
  );
  
  sortedData.forEach(item => {
    dates.push(item.date);
    // K线数据格式: [开盘, 收盘, 最低, 最高]
    klineData.push([item.open, item.close, item.low, item.high]);
    volumes.push(item.volume);
  });
  
  return { dates, klineData, volumes };
}

// 绘制周线K线图
function drawWeeklyKLine(stockCode) {
  const chart = echarts.init(document.getElementById('weekly-chart'));
  
  // 获取数据
  getWeeklyQuotes(stockCode, '2025-01-01', '2025-11-30').then(data => {
    const { dates, klineData, volumes } = convertToEChartsFormat(data);
    
    const option = {
      title: {
        text: `${stockCode} 周线图`
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        }
      },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: false
      },
      yAxis: [
        {
          type: 'value',
          scale: true,
          name: '价格'
        },
        {
          type: 'value',
          scale: true,
          name: '成交量',
          position: 'right'
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          show: true,
          type: 'slider',
          bottom: 10,
          start: 0,
          end: 100
        }
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: klineData,
          itemStyle: {
            color: '#ef232a',  // 阳线颜色
            color0: '#14b143', // 阴线颜色
            borderColor: '#ef232a',
            borderColor0: '#14b143'
          }
        },
        {
          name: '成交量',
          type: 'bar',
          yAxisIndex: 1,
          data: volumes,
          itemStyle: {
            color: function(params) {
              const index = params.dataIndex;
              if (index === 0) return '#999';
              return klineData[index][1] >= klineData[index][0] 
                ? '#ef232a' 
                : '#14b143';
            }
          }
        }
      ]
    };
    
    chart.setOption(option);
  });
}

// 调用
drawWeeklyKLine('000001');
```

### 4.3 Vue 组件示例

```vue
<template>
  <div class="weekly-chart-container">
    <div class="chart-header">
      <h3>{{ stockCode }} 周线图</h3>
      <div class="date-range">
        <input type="date" v-model="startDate" @change="loadData" />
        <span>至</span>
        <input type="date" v-model="endDate" @change="loadData" />
      </div>
    </div>
    <div id="weekly-chart" style="width: 100%; height: 500px;"></div>
  </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';

export default {
  name: 'WeeklyChart',
  props: {
    stockCode: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      startDate: '2025-01-01',
      endDate: '2025-11-30',
      chart: null
    };
  },
  mounted() {
    this.initChart();
    this.loadData();
  },
  methods: {
    initChart() {
      this.chart = echarts.init(document.getElementById('weekly-chart'));
    },
    
    async loadData() {
      try {
        const response = await axios.get(`/api/quotes/weekly/${this.stockCode}`, {
          params: {
            start_date: this.startDate,
            end_date: this.endDate,
            limit: 200
          }
        });
        
        if (response.data.code === 200) {
          this.renderChart(response.data.data);
        }
      } catch (error) {
        console.error('加载周线数据失败:', error);
      }
    },
    
    renderChart(data) {
      // 转换数据格式并绘制图表
      // ... (同上面的 ECharts 示例)
    }
  }
};
</script>
```

## 5. 数据格式说明

### 5.1 K线数据格式

ECharts K线图要求的数据格式：
```javascript
[开盘价, 收盘价, 最低价, 最高价]
```

注意顺序：开、收、低、高

### 5.2 时间排序

- API返回的数据默认按时间倒序（最新的在前）
- 绘制K线图时需要按时间正序排列

### 5.3 颜色约定

- 阳线（收盘 > 开盘）: 红色 `#ef232a`
- 阴线（收盘 < 开盘）: 绿色 `#14b143`

## 6. 性能优化建议

### 6.1 数据缓存

```javascript
// 使用 localStorage 缓存周线数据
function getCachedWeeklyData(stockCode, startDate, endDate) {
  const cacheKey = `weekly_${stockCode}_${startDate}_${endDate}`;
  const cached = localStorage.getItem(cacheKey);
  
  if (cached) {
    const data = JSON.parse(cached);
    // 检查缓存是否过期（周线数据可以缓存较长时间）
    if (Date.now() - data.timestamp < 24 * 60 * 60 * 1000) {
      return data.quotes;
    }
  }
  
  return null;
}

function cacheWeeklyData(stockCode, startDate, endDate, quotes) {
  const cacheKey = `weekly_${stockCode}_${startDate}_${endDate}`;
  localStorage.setItem(cacheKey, JSON.stringify({
    quotes,
    timestamp: Date.now()
  }));
}
```

### 6.2 分页加载

```javascript
// 分页加载周线数据
async function loadWeeklyDataByPage(stockCode, page = 1, pageSize = 50) {
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(endDate.getDate() - (page * pageSize * 7));
  
  return await getWeeklyQuotes(
    stockCode,
    startDate.toISOString().split('T')[0],
    endDate.toISOString().split('T')[0]
  );
}
```

### 6.3 数据压缩

对于大量数据，可以使用压缩传输：

```python
# 后端启用 gzip 压缩
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

## 7. 错误处理

### 7.1 常见错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|---------|
| 200 | 成功 | - |
| 404 | 未找到数据 | 检查股票代码是否正确 |
| 400 | 参数错误 | 检查日期格式等参数 |
| 500 | 服务器错误 | 稍后重试或联系管理员 |

### 7.2 前端错误处理

```javascript
async function getWeeklyQuotesWithErrorHandling(stockCode) {
  try {
    const response = await axios.get(`/api/quotes/weekly/${stockCode}`);
    
    if (response.data.code === 200) {
      return response.data.data;
    } else if (response.data.code === 404) {
      showMessage('该股票暂无周线数据', 'warning');
      return [];
    } else {
      showMessage(`获取数据失败: ${response.data.message}`, 'error');
      return [];
    }
  } catch (error) {
    if (error.response) {
      showMessage(`服务器错误: ${error.response.status}`, 'error');
    } else if (error.request) {
      showMessage('网络连接失败，请检查网络', 'error');
    } else {
      showMessage(`请求失败: ${error.message}`, 'error');
    }
    return [];
  }
}
```

## 8. 安全性考虑

### 8.1 参数验证

```python
from pydantic import BaseModel, validator

class WeeklyQuotesRequest(BaseModel):
    stock_code: str
    start_date: Optional[str]
    end_date: Optional[str]
    limit: int = 100
    
    @validator('stock_code')
    def validate_stock_code(cls, v):
        if not v or len(v) != 6 or not v.isdigit():
            raise ValueError('股票代码格式错误')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('limit 必须在 1-1000 之间')
        return v
```

### 8.2 SQL注入防护

使用参数化查询，避免SQL注入：

```python
# ✅ 正确：使用参数化查询
query = text("SELECT * FROM weekly_quotes WHERE code = :code")
result = session.execute(query, {'code': stock_code})

# ❌ 错误：字符串拼接
query = f"SELECT * FROM weekly_quotes WHERE code = '{stock_code}'"
```

### 8.3 访问频率限制

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@router.get("/{stock_code}", dependencies=[Depends(RateLimiter(times=100, seconds=60))])
async def get_weekly_quotes(...):
    # 限制每分钟最多100次请求
    pass
```

## 9. 总结

本API设计文档提供了完整的周线数据接口规范和前后端实现示例，主要特点：

- ✅ RESTful 风格的API设计
- ✅ 完整的请求/响应示例
- ✅ 前端调用和图表展示代码
- ✅ 性能优化和错误处理建议
- ✅ 安全性考虑

开发者可以根据本文档快速实现周线数据的展示和分析功能。
