# 低九策略 - 后端服务重启指南

## 问题现象
- 前端点击"刷新筛选"后一直显示"正在筛选股票，请稍候..."
- 浏览器控制台显示请求已发送但无响应
- 后端服务超时或无响应

## 原因分析
1. **后端服务可能正在处理之前的请求**（遍历所有A股需要较长时间）
2. **连接池耗尽**（有很多CLOSE_WAIT连接）
3. **数据库查询慢**

## 解决方案

### 方案1: 重启后端服务（推荐）

#### 步骤1: 停止当前服务
```powershell
# 找到Python进程ID
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Select-Object ProcessName, Id, CPU

# 停止FastAPI服务（进程ID 7640）
Stop-Process -Id 7640 -Force
```

#### 步骤2: 重新启动服务
```powershell
# 进入backend_api目录
cd e:\wangxw\股票分析软件\编码\stock_quote_analayze\backend_api

# 启动服务
python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### 方案2: 使用测试模式（快速验证）

修改路由文件，添加limit参数用于测试：

```python
# backend_api/stock/stock_screening_routes.py

@router.get("/low-nine-strategy")
async def get_low_nine_strategy(
    limit: int = Query(None, description="限制处理股票数量（测试用）"),
    db: Session = Depends(get_db)
):
    """低九策略选股"""
    try:
        logger.info("开始执行低九策略选股")
        
        # 执行选股策略（可以限制数量用于测试）
        results = LowNineStrategy.screening_low_nine_strategy(db, limit=limit)
        
        logger.info(f"低九策略选股执行完成，找到 {len(results)} 只符合条件的股票")
        
        return JSONResponse({
            "success": True,
            "data": results,
            "total": len(results),
            "search_date": datetime.now().strftime("%Y-%m-%d"),
            "strategy_name": "低九策略"
        })
        
    except Exception as e:
        logger.error(f"执行低九策略选股失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"低九策略选股执行失败: {str(e)}"
        )
```

然后可以这样测试：
```
http://localhost:5000/api/screening/low-nine-strategy?limit=100
```

### 方案3: 优化数据库查询

如果数据库查询太慢，可以考虑：

1. **添加索引**
```sql
CREATE INDEX idx_historical_quotes_code_date 
ON historical_quotes(code, date DESC);
```

2. **使用缓存**
- 缓存股票列表
- 缓存历史数据

3. **分批处理**
- 将所有股票分成多个批次
- 每批处理100-200只股票

## 性能优化建议

### 1. 添加超时设置
```python
# 在FastAPI中设置超时
from fastapi import FastAPI
import uvicorn

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        timeout_keep_alive=300  # 5分钟
    )
```

### 2. 使用异步处理
```python
from fastapi import BackgroundTasks

@router.get("/low-nine-strategy")
async def get_low_nine_strategy(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # 立即返回任务ID
    task_id = str(uuid.uuid4())
    
    # 在后台执行策略
    background_tasks.add_task(
        run_strategy_in_background,
        task_id,
        db
    )
    
    return {"task_id": task_id, "status": "processing"}
```

### 3. 添加进度查询接口
```python
@router.get("/low-nine-strategy/progress/{task_id}")
async def get_strategy_progress(task_id: str):
    # 返回任务进度
    return {
        "task_id": task_id,
        "progress": 45.5,
        "processed": 2000,
        "total": 4400,
        "found": 15
    }
```

## 验证步骤

重启服务后：

1. 访问根路径验证服务是否正常：
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/" -Method GET
```

2. 测试低九策略（限制100只股票）：
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/screening/low-nine-strategy?limit=100" -Method GET
```

3. 查看后端日志：
```powershell
Get-Content "e:\wangxw\股票分析软件\编码\stock_quote_analayze\backend_api\app.log" -Tail 50 -Wait
```

## 预期结果

重启后，应该能看到：
- 后端日志显示策略执行进度
- 每处理100只股票输出一次进度
- 找到符合条件的股票会立即记录
- 最终返回结果给前端

## 注意事项

1. **执行时间**：遍历所有A股（约4400只）可能需要2-5分钟
2. **数据库性能**：确保数据库连接正常且性能良好
3. **内存使用**：注意监控内存使用情况
4. **日志监控**：实时查看日志了解执行进度

## 后续优化

1. 实现任务队列（Celery）
2. 添加Redis缓存
3. 使用数据库连接池
4. 实现增量更新而非全量扫描
