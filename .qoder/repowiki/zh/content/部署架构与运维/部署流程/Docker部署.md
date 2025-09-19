# Docker部署

<cite>
**本文档引用的文件**   
- [deploy.py](file://deploy.py)
- [DEPLOYMENT_SUMMARY.md](file://DEPLOYMENT_SUMMARY.md)
</cite>

## 目录
1. [Docker部署概述](#docker部署概述)
2. [Docker文件生成](#docker文件生成)
3. [Docker镜像构建](#docker镜像构建)
4. [容器运行与编排](#容器运行与编排)
5. [服务依赖与健康检查](#服务依赖与健康检查)
6. [端口映射与环境变量](#端口映射与环境变量)
7. [常见问题排查](#常见问题排查)

## Docker部署概述

本文档详细说明如何使用Docker部署股票分析系统。基于`deploy.py`脚本中的`create_docker_files`方法和`DEPLOYMENT_SUMMARY.md`中的Docker部署方案，全面介绍Docker部署所需的文件生成、镜像构建、容器运行和服务配置。

**Section sources**
- [deploy.py](file://deploy.py#L300-L380)
- [DEPLOYMENT_SUMMARY.md](file://DEPLOYMENT_SUMMARY.md#L20-L50)

## Docker文件生成

### Dockerfile生成

`deploy.py`脚本中的`create_docker_files`方法会自动生成Dockerfile，该文件定义了应用的构建环境和运行时配置。

```mermaid
flowchart TD
Start([开始]) --> BaseImage["选择基础镜像 python:3.9-slim"]
BaseImage --> WorkDir["设置工作目录 /app"]
WorkDir --> EnvVars["设置环境变量 PYTHONPATH 和 PYTHONUNBUFFERED"]
EnvVars --> SystemDeps["安装系统依赖 gcc, g++, curl"]
SystemDeps --> CopyRequirements["复制 requirements.txt 文件"]
CopyRequirements --> InstallPythonDeps["安装Python依赖"]
InstallPythonDeps --> CopyProject["复制项目文件到镜像"]
CopyProject --> CreateLogsDir["创建日志目录 logs"]
CreateLogsDir --> ExposePorts["暴露端口 5000, 8000, 8001"]
ExposePorts --> CopyWaitScript["复制 wait-for-it.sh 脚本"]
CopyWaitScript --> SetPermissions["设置脚本执行权限"]
SetPermissions --> CMD["设置启动命令"]
CMD --> End([结束])
```

**Diagram sources**
- [deploy.py](file://deploy.py#L310-L330)

### docker-compose.yml生成

`create_docker_files`方法还会生成docker-compose.yml文件，用于定义多容器应用的配置。

```mermaid
graph TD
ComposeFile[docker-compose.yml] --> Version["指定Compose版本 3.8"]
Version --> Services["定义服务"]
Services --> PostgresService["PostgreSQL服务"]
Services --> StockAnalyzerService["股票分析服务"]
PostgresService --> Image["使用 postgres:13 镜像"]
PostgresService --> Environment["设置数据库环境变量"]
PostgresService --> Ports["端口映射 5446:5432"]
PostgresService --> Volumes["挂载数据卷 postgres_data"]
PostgresService --> Restart["重启策略 unless-stopped"]
PostgresService --> Healthcheck["健康检查配置"]
StockAnalyzerService --> Build["从当前目录构建"]
StockAnalyzerService --> Ports["端口映射 5000:5000, 8000:8000, 8001:8001"]
StockAnalyzerService --> Volumes["挂载日志目录 ./logs:/app/logs"]
StockAnalyzerService --> Environment["设置应用环境变量"]
StockAnalyzerService --> DependsOn["依赖postgres服务"]
StockAnalyzerService --> Restart["重启策略 unless-stopped"]
StockAnalyzerService --> Healthcheck["健康检查配置"]
ComposeFile --> Volumes["定义数据卷 postgres_data"]
```

**Diagram sources**
- [deploy.py](file://deploy.py#L332-L360)

### .dockerignore生成

`.dockerignore`文件用于指定在构建镜像时需要忽略的文件和目录。

```mermaid
flowchart TD
Dockerignore[".dockerignore"] --> PythonCache["__pycache__/"]
Dockerignore --> PythonBytecode["*.pyc, *.pyo, *.pyd"]
Dockerignore --> PythonEnv["env, venv/, .venv, ENV/"]
Dockerignore --> Git["Git相关 .git"]
Dockerignore --> Logs["日志文件 *.log"]
Dockerignore --> Config["配置文件 .env"]
Dockerignore --> Test["测试目录 .pytest_cache, .hypothesis"]
Dockerignore --> Temp["临时文件 pip-log.txt, pip-delete-this-directory.txt"]
Dockerignore --> Coverage["覆盖率文件 .coverage*"]
Dockerignore --> Cache["缓存目录 .mypy_cache, .cache"]
Dockerignore --> Mac["Mac系统文件 .DS_Store"]
Dockerignore --> Package["包文件 *.egg-info, *.egg, MANIFEST"]
```

**Diagram sources**
- [deploy.py](file://deploy.py#L362-L380)

**Section sources**
- [deploy.py](file://deploy.py#L300-L380)

## Docker镜像构建

### 构建过程详解

Docker镜像构建过程遵循最佳实践，确保镜像的轻量化和安全性。

```mermaid
sequenceDiagram
participant User as "用户"
participant DockerCLI as "Docker CLI"
participant DockerDaemon as "Docker守护进程"
User->>DockerCLI : docker build -t stock-analyzer .
DockerCLI->>DockerDaemon : 发送构建上下文
DockerDaemon->>DockerDaemon : 读取Dockerfile
DockerDaemon->>DockerDaemon : 拉取基础镜像 python : 3.9-slim
DockerDaemon->>DockerDaemon : 执行RUN命令安装系统依赖
DockerDaemon->>DockerDaemon : 复制requirements.txt并安装Python依赖
DockerDaemon->>DockerDaemon : 复制项目文件
DockerDaemon->>DockerDaemon : 创建日志目录
DockerDaemon->>DockerDaemon : 暴露指定端口
DockerDaemon->>DockerDaemon : 复制并设置wait-for-it.sh权限
DockerDaemon->>DockerCLI : 构建完成
DockerCLI->>User : 返回镜像ID
```

**Diagram sources**
- [deploy.py](file://deploy.py#L310-L330)

### 构建命令

使用以下命令构建Docker镜像：

```bash
docker build -t stock-analyzer .
```

构建过程中会执行以下步骤：
1. 从`python:3.9-slim`基础镜像开始
2. 安装必要的系统依赖（gcc, g++, curl）
3. 安装Python依赖包
4. 复制项目文件到镜像
5. 配置启动环境

**Section sources**
- [DEPLOYMENT_SUMMARY.md](file://DEPLOYMENT_SUMMARY.md#L25-L30)

## 容器运行与编排

### 单容器运行

可以使用`docker run`命令直接运行单个容器：

```bash
docker run -d -p 5000:5000 -p 8000:8000 -p 8001:8001 stock-analyzer
```

```mermaid
flowchart TD
RunCommand["docker run命令"] --> Options["选项解析"]
Options --> Detached["-d: 后台运行"]
Options --> PortMapping["-p: 端口映射"]
Options --> ImageName["镜像名称 stock-analyzer"]
RunCommand --> ContainerCreation["创建容器实例"]
ContainerCreation --> NetworkSetup["网络配置"]
NetworkSetup --> PortBinding["端口绑定"]
PortBinding --> VolumeMount["挂载卷(如果有)"]
VolumeMount --> StartContainer["启动容器"]
StartContainer --> ExecuteCMD["执行Dockerfile中的CMD命令"]
ExecuteCMD --> WaitForDB["运行wait-for-it.sh等待数据库"]
WaitForDB --> StartApp["启动应用 python start_system.py"]
```

**Diagram sources**
- [deploy.py](file://deploy.py#L318-L320)

### Docker Compose编排

使用Docker Compose可以更方便地管理多容器应用：

```bash
docker-compose up -d
```

```mermaid
sequenceDiagram
participant User as "用户"
participant DockerCompose as "Docker Compose"
participant Postgres as "PostgreSQL容器"
participant App as "应用容器"
User->>DockerCompose : docker-compose up -d
DockerCompose->>DockerCompose : 读取docker-compose.yml
DockerCompose->>DockerCompose : 构建stock-analyzer镜像(如果需要)
DockerCompose->>Postgres : 创建并启动PostgreSQL容器
Postgres->>Postgres : 初始化数据库
Postgres->>Postgres : 执行健康检查
Postgres-->>DockerCompose : 健康检查通过
DockerCompose->>App : 创建并启动应用容器
App->>App : 等待PostgreSQL服务
App->>Postgres : 连接数据库
App->>App : 启动应用服务
App-->>DockerCompose : 启动完成
DockerCompose-->>User : 所有服务启动完成
```

**Diagram sources**
- [deploy.py](file://deploy.py#L340-L360)

**Section sources**
- [DEPLOYMENT_SUMMARY.md](file://DEPLOYMENT_SUMMARY.md#L32-L35)

## 服务依赖与健康检查

### 服务依赖关系

Docker Compose配置中明确定义了服务间的依赖关系，确保服务按正确顺序启动。

```mermaid
graph TD
AppService[stock-analyzer服务] --> |depends_on| PostgresService[PostgreSQL服务]
PostgresService --> |healthcheck| DBHealth[数据库健康检查]
DBHealth --> |test: pg_isready| PostgresReady["pg_isready -U postgres"]
AppService --> |healthcheck| AppHealth[应用健康检查]
AppHealth --> |test: curl| AppReady["curl -f http://localhost:5000/health"]
AppService --> |等待| PostgresReady
PostgresReady --> |成功| AppService
```

**Diagram sources**
- [deploy.py](file://deploy.py#L340-L360)

### 健康检查配置

健康检查确保服务在完全就绪后才被视为可用。

#### PostgreSQL健康检查

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

#### 应用服务健康检查

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

```mermaid
flowchart TD
HealthCheckStart["健康检查开始"] --> ExecuteTest["执行测试命令"]
ExecuteTest --> PostgresTest{"PostgreSQL检查?"}
PostgresTest --> |是| RunPgIsReady["运行 pg_isready -U postgres"]
PostgresTest --> |否| RunCurl["运行 curl -f http://localhost:5000/health"]
RunPgIsReady --> CheckResult["检查返回码"]
RunCurl --> CheckResult
CheckResult --> Success{"成功?"}
Success --> |是| MarkHealthy["标记服务为健康"]
Success --> |否| RetryCount["重试次数 < 最大重试次数?"]
RetryCount --> |是| WaitInterval["等待间隔时间"]
WaitInterval --> ExecuteTest
RetryCount --> |否| MarkUnhealthy["标记服务为不健康"]
MarkHealthy --> End["健康检查通过"]
MarkUnhealthy --> End
```

**Diagram sources**
- [deploy.py](file://deploy.py#L348-L350)
- [deploy.py](file://deploy.py#L372-L374)

**Section sources**
- [deploy.py](file://deploy.py#L340-L380)

## 端口映射与环境变量

### 端口映射配置

Docker部署中的端口映射配置确保外部可以访问容器内的服务。

```mermaid
graph LR
Host[宿主机] --> |端口映射| Container[容器]
Host --> Port5446["端口 5446"]
Host --> Port5000["端口 5000"]
Host --> Port8000["端口 8000"]
Host --> Port8001["端口 8001"]
Port5446 --> |映射到| ContainerPort5432["容器端口 5432"]
Port5000 --> |映射到| ContainerPort5000["容器端口 5000"]
Port8000 --> |映射到| ContainerPort8000["容器端口 8000"]
Port8001 --> |映射到| ContainerPort8001["容器端口 8001"]
ContainerPort5432 --> Postgres["PostgreSQL服务"]
ContainerPort5000 --> Backend["后端API服务"]
ContainerPort8000 --> Frontend["前端服务"]
ContainerPort8001 --> Admin["管理后台服务"]
```

**Diagram sources**
- [deploy.py](file://deploy.py#L344-L346)
- [deploy.py](file://deploy.py#L364-L366)

### 环境变量设置

环境变量用于配置应用运行时的行为。

```mermaid
flowchart TD
EnvVars[环境变量] --> App["应用容器"]
EnvVars --> Postgres["PostgreSQL容器"]
Postgres --> DBName["POSTGRES_DB=stock_analysis"]
Postgres --> DBUser["POSTGRES_USER=postgres"]
Postgres --> DBPassword["POSTGRES_PASSWORD=qidianspacetime"]
App --> PythonPath["PYTHONPATH=/app"]
App --> Environment["ENVIRONMENT=production"]
App --> DBHost["DB_HOST=postgres"]
App --> DBPort["DB_PORT=5432"]
App --> DBName["DB_NAME=stock_analysis"]
App --> DBUser["DB_USER=postgres"]
App --> DBPassword["DB_PASSWORD=qidianspacetime"]
App --> |用于连接| Postgres
```

**Diagram sources**
- [deploy.py](file://deploy.py#L342-L343)
- [deploy.py](file://deploy.py#L368-L370)

**Section sources**
- [deploy.py](file://deploy.py#L332-L380)

## 常见问题排查

### 镜像构建失败

当Docker镜像构建失败时，可能的原因和解决方案如下：

```mermaid
flowchart TD
BuildFailed["镜像构建失败"] --> CheckDockerfile["检查Dockerfile语法"]
CheckDockerfile --> SyntaxError{"语法错误?"}
SyntaxError --> |是| FixSyntax["修正Dockerfile语法"]
SyntaxError --> |否| CheckNetwork["检查网络连接"]
CheckNetwork --> NetworkIssue{"网络问题?"}
NetworkIssue --> |是| UseMirror["使用国内镜像源"]
NetworkIssue --> |否| CheckDependencies["检查依赖文件"]
CheckDependencies --> MissingFiles{"缺少requirements.txt?"}
MissingFiles --> |是| CreateRequirements["创建缺失的依赖文件"]
MissingFiles --> |否| CheckPermissions["检查文件权限"]
CheckPermissions --> PermissionIssue{"权限问题?"}
PermissionIssue --> |是| FixPermissions["修复文件权限"]
PermissionIssue --> |否| CheckDiskSpace["检查磁盘空间"]
CheckDiskSpace --> LowSpace{"磁盘空间不足?"}
LowSpace --> |是| FreeSpace["清理磁盘空间"]
LowSpace --> |否| CheckContext["检查构建上下文大小"]
CheckContext --> LargeContext{"上下文过大?"}
LargeContext --> |是| UpdateDockerignore["完善.dockerignore文件"]
LargeContext --> |否| CheckBaseImage["检查基础镜像"]
CheckBaseImage --> ImageUnavailable{"基础镜像不可用?"}
ImageUnavailable --> |是| UseAlternativeImage["使用替代基础镜像"]
ImageUnavailable --> |否| CheckBuildCache["检查构建缓存"]
CheckBuildCache --> ClearCache["清理构建缓存后重试"]
```

**Diagram sources**
- [deploy.py](file://deploy.py#L300-L380)

### 容器启动异常

容器启动异常的排查流程：

```mermaid
flowchart TD
ContainerStartFailed["容器启动异常"] --> CheckLogs["查看容器日志"]
CheckLogs --> docker_logs["docker logs <container_id>"]
docker_logs --> AnalyzeError["分析错误信息"]
AnalyzeError --> DBConnection{"数据库连接问题?"}
DBConnection --> |是| CheckDBConfig["检查数据库配置"]
CheckDBConfig --> VerifyHost["验证DB_HOST配置"]
VerifyHost --> VerifyPort["验证DB_PORT配置"]
VerifyPort --> VerifyCredentials["验证用户名密码"]
DBConnection --> |否| PortConflict{"端口冲突?"}
PortConflict --> |是| ChangePort["修改端口映射"]
PortConflict --> |否| MissingDependencies["检查缺失依赖"]
MissingDependencies --> CheckRequirements["验证requirements.txt"]
CheckRequirements --> InstallMissing["安装缺失依赖"]
MissingDependencies --> |否| FilePermissions["检查文件权限"]
FilePermissions --> FixPermissions["修复文件权限问题"]
FilePermissions --> |否| ResourceLimit["检查资源限制"]
ResourceLimit --> IncreaseResources["增加内存/CPU限制"]
ResourceLimit --> |否| CheckHealthCheck["检查健康检查配置"]
CheckHealthCheck --> AdjustHealthCheck["调整健康检查参数"]
```

**Diagram sources**
- [deploy.py](file://deploy.py#L340-L380)

### 网络连接问题

网络连接问题的排查方法：

```mermaid
flowchart TD
NetworkIssue["网络连接问题"] --> CheckContainerNetwork["检查容器网络"]
CheckContainerNetwork --> docker_network["docker network ls"]
docker_network --> docker_inspect["docker inspect <container>"]
docker_inspect --> AnalyzeNetworkConfig["分析网络配置"]
AnalyzeNetworkConfig --> SameNetwork{"服务在同一网络?"}
SameNetwork --> |否| RecreateCompose["重新创建docker-compose"]
SameNetwork --> |是| CheckServiceName["检查服务名称"]
CheckServiceName --> ServiceNameCorrect{"服务名称正确?"}
ServiceNameCorrect --> |否| FixServiceName["修正服务名称"]
ServiceNameCorrect --> |是| CheckPort["检查端口配置"]
CheckPort --> PortCorrect{"端口配置正确?"}
PortCorrect --> |否| FixPortConfig["修正端口配置"]
PortCorrect --> |是| TestConnection["测试连接"]
TestConnection --> docker_exec["docker exec -it <container> bash"]
docker_exec --> TestConnectivity["在容器内测试连接"]
TestConnectivity --> CanConnect{"能否连接?"}
CanConnect --> |是| CheckFirewall["检查防火墙设置"]
CanConnect --> |否| CheckRouting["检查路由配置"]
CheckFirewall --> AdjustFirewall["调整防火墙规则"]
CheckRouting --> FixRouting["修正路由配置"]
```

**Diagram sources**
- [deploy.py](file://deploy.py#L340-L380)

**Section sources**
- [DEPLOYMENT_SUMMARY.md](file://DEPLOYMENT_SUMMARY.md#L150-L180)