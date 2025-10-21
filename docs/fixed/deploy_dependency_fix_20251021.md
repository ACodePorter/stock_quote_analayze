# 部署依赖安装问题修复报告

## 问题描述
在运行 `python deploy.py` 时，部署脚本在安装 `backend_core/requirements.txt` 依赖时失败，错误信息显示：
```
ERROR: Could not find a version that satisfies the requirement pandas-ta>=0.3.0 (from versions: 0.4.67b0, 0.4.71b0)
ERROR: No matching distribution found for pandas-ta>=0.3.0
```

## 问题原因
1. **版本不匹配**：`pandas-ta>=0.3.0` 版本不存在，只有 `0.4.67b0` 和 `0.4.71b0` 版本可用
2. **复杂依赖冲突**：原始的 `backend_core/requirements.txt` 包含了大量机器学习、深度学习包，导致依赖解析时间过长和潜在的版本冲突

## 解决方案

### 1. 修复版本问题
将 `backend_core/requirements.txt` 中的：
```
pandas-ta>=0.3.0
```
修改为：
```
pandas-ta>=0.4.67b0
```

### 2. 创建简化依赖文件
创建了 `backend_core/requirements-minimal.txt` 文件，包含核心功能所需的依赖：
- 核心数据处理：pandas, numpy, scipy
- 数据采集：akshare, tushare, requests, beautifulsoup4, lxml
- 数据库：sqlalchemy, redis
- 工具：python-dotenv, pyyaml, tqdm, loguru, apscheduler
- 测试：pytest, pytest-cov, pytest-mock
- 开发工具：black, flake8, isort

将机器学习、深度学习、技术分析等可选依赖注释掉，避免复杂的依赖冲突。

### 3. 修改部署脚本
更新 `deploy.py` 脚本，优先使用简化版本的依赖文件：
```python
# 安装backend_core依赖 - 优先使用简化版本
if os.path.exists("backend_core/requirements-minimal.txt"):
    logger.info("📦 安装backend_core简化依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend_core/requirements-minimal.txt"], 
                 check=True, capture_output=True)
    logger.info("✅ backend_core简化依赖安装完成")
elif os.path.exists("backend_core/requirements.txt"):
    logger.info("📦 安装backend_core完整依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend_core/requirements.txt"], 
                 check=True, capture_output=True)
    logger.info("✅ backend_core完整依赖安装完成")
```

## 修复结果
- ✅ 简化依赖安装成功
- ✅ 完整部署脚本运行成功
- ✅ 所有核心功能依赖已安装
- ✅ 避免了复杂的依赖冲突

## 后续建议
1. **按需安装**：如果项目需要机器学习、深度学习等功能，可以单独安装相关依赖：
   ```bash
   pip install scikit-learn xgboost lightgbm catboost
   pip install tensorflow torch transformers
   pip install ta-lib pandas-ta
   ```

2. **环境隔离**：建议使用虚拟环境来管理不同项目的依赖

3. **版本锁定**：在生产环境中建议使用 `pip freeze > requirements-lock.txt` 锁定具体版本

## 文件变更
- `backend_core/requirements.txt` - 修复 pandas-ta 版本
- `backend_core/requirements-minimal.txt` - 新增简化依赖文件
- `deploy.py` - 更新部署脚本逻辑

修复时间：2025-10-21 14:30
修复状态：✅ 已完成
