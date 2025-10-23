# 代理服务器配置指南

## 代理服务器配置方法

### 方法1：在配置文件中配置代理池

#### 1. 修改配置文件

编辑 `backend_core/config/config.py` 文件：

```python
DATA_COLLECTORS = {
    'akshare': {
        'max_retries': 3,
        'retry_delay': 5,
        'timeout': 30,
        'log_dir': str(ROOT_DIR / 'backend_core' / 'logs'),
        'db_file': str(DB_DIR / 'stock_analysis.db'),
        'max_connection_errors': 10,
        # 代理池配置
        'proxy_pool': [
            {'http': 'http://proxy1.example.com:8080', 'https': 'https://proxy1.example.com:8080'},
            {'http': 'http://proxy2.example.com:8080', 'https': 'https://proxy2.example.com:8080'},
            {'http': 'http://proxy3.example.com:8080', 'https': 'https://proxy3.example.com:8080'},
        ],
        'random_delay_range': (1, 3),
        'ssl_verify': False,
        'use_fallback_sources': True,
    }
}
```

#### 2. 代理服务器类型

**HTTP代理示例：**
```python
'proxy_pool': [
    {'http': 'http://username:password@proxy.example.com:8080', 
     'https': 'https://username:password@proxy.example.com:8080'},
]
```

**SOCKS代理示例：**
```python
'proxy_pool': [
    {'http': 'socks5://username:password@proxy.example.com:1080', 
     'https': 'socks5://username:password@proxy.example.com:1080'},
]
```

### 方法2：环境变量配置

#### 1. 设置环境变量

**Windows (PowerShell):**
```powershell
$env:HTTP_PROXY = "http://proxy.example.com:8080"
$env:HTTPS_PROXY = "https://proxy.example.com:8080"
```

**Windows (CMD):**
```cmd
set HTTP_PROXY=http://proxy.example.com:8080
set HTTPS_PROXY=https://proxy.example.com:8080
```

**Linux/Mac:**
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=https://proxy.example.com:8080
```

#### 2. 在代码中使用环境变量

```python
import os

# 从环境变量读取代理配置
proxy_pool = []
if os.getenv('HTTP_PROXY'):
    proxy_pool.append({
        'http': os.getenv('HTTP_PROXY'),
        'https': os.getenv('HTTPS_PROXY', os.getenv('HTTP_PROXY'))
    })
```

### 方法3：动态代理配置

创建一个代理配置文件 `proxy_config.json`：

```json
{
    "proxies": [
        {
            "name": "proxy1",
            "http": "http://proxy1.example.com:8080",
            "https": "https://proxy1.example.com:8080",
            "username": "user1",
            "password": "pass1",
            "enabled": true
        },
        {
            "name": "proxy2",
            "http": "http://proxy2.example.com:8080",
            "https": "https://proxy2.example.com:8080",
            "username": "user2",
            "password": "pass2",
            "enabled": true
        }
    ],
    "rotation_interval": 300,
    "max_failures": 3
}
```

然后在代码中加载配置：

```python
import json
from pathlib import Path

def load_proxy_config():
    config_file = Path('proxy_config.json')
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        proxy_pool = []
        for proxy in config['proxies']:
            if proxy['enabled']:
                if proxy.get('username') and proxy.get('password'):
                    # 带认证的代理
                    http_proxy = f"http://{proxy['username']}:{proxy['password']}@{proxy['http'].replace('http://', '')}"
                    https_proxy = f"https://{proxy['username']}:{proxy['password']}@{proxy['https'].replace('https://', '')}"
                else:
                    # 无认证的代理
                    http_proxy = proxy['http']
                    https_proxy = proxy['https']
                
                proxy_pool.append({
                    'http': http_proxy,
                    'https': https_proxy
                })
        
        return proxy_pool
    return []
```

## 免费代理服务器获取

### 1. 免费代理网站

- **ProxyList**: https://www.proxy-list.download/
- **FreeProxyList**: https://free-proxy-list.net/
- **ProxyScrape**: https://proxyscrape.com/
- **HideMyName**: https://hidemy.name/cn/proxy-list/

### 2. 代理格式示例

从免费代理网站获取的代理通常格式如下：
```
IP:PORT
例如: 123.456.789.012:8080
```

转换为配置格式：
```python
'proxy_pool': [
    {'http': 'http://123.456.789.012:8080', 'https': 'https://123.456.789.012:8080'},
    {'http': 'http://987.654.321.098:3128', 'https': 'https://987.654.321.098:3128'},
]
```

### 3. 代理验证脚本

创建一个代理验证脚本：

```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def test_proxy(proxy_dict, timeout=10):
    """测试代理是否可用"""
    try:
        response = requests.get(
            'https://httpbin.org/ip', 
            proxies=proxy_dict, 
            timeout=timeout
        )
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except Exception as e:
        return False, str(e)

def validate_proxy_pool(proxy_pool):
    """验证代理池中的所有代理"""
    valid_proxies = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(test_proxy, proxy) for proxy in proxy_pool]
        
        for i, future in enumerate(futures):
            is_valid, result = future.result()
            if is_valid:
                valid_proxies.append(proxy_pool[i])
                print(f"✅ 代理 {proxy_pool[i]} 可用")
            else:
                print(f"❌ 代理 {proxy_pool[i]} 不可用: {result}")
    
    return valid_proxies

# 使用示例
proxy_pool = [
    {'http': 'http://proxy1.example.com:8080', 'https': 'https://proxy1.example.com:8080'},
    {'http': 'http://proxy2.example.com:8080', 'https': 'https://proxy2.example.com:8080'},
]

valid_proxies = validate_proxy_pool(proxy_pool)
print(f"可用代理数量: {len(valid_proxies)}")
```

## 代理轮换机制

### 1. 简单轮换

```python
class ProxyRotator:
    def __init__(self, proxy_pool):
        self.proxy_pool = proxy_pool
        self.current_index = 0
    
    def get_next_proxy(self):
        if not self.proxy_pool:
            return None
        
        proxy = self.proxy_pool[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxy_pool)
        return proxy
```

### 2. 智能轮换（基于成功率）

```python
class SmartProxyRotator:
    def __init__(self, proxy_pool):
        self.proxy_pool = proxy_pool
        self.proxy_stats = {i: {'success': 0, 'failures': 0} for i in range(len(proxy_pool))}
        self.current_index = 0
    
    def get_next_proxy(self):
        if not self.proxy_pool:
            return None
        
        # 选择成功率最高的代理
        best_index = max(self.proxy_stats.keys(), 
                        key=lambda i: self.proxy_stats[i]['success'] - self.proxy_stats[i]['failures'])
        
        return self.proxy_pool[best_index]
    
    def record_success(self, proxy_index):
        if proxy_index in self.proxy_stats:
            self.proxy_stats[proxy_index]['success'] += 1
    
    def record_failure(self, proxy_index):
        if proxy_index in self.proxy_stats:
            self.proxy_stats[proxy_index]['failures'] += 1
```

## 完整的使用示例

### 1. 创建代理配置脚本

```python
# proxy_setup.py
import json
from pathlib import Path

def setup_proxy_config():
    """设置代理配置"""
    
    # 代理服务器列表（请替换为实际的代理服务器）
    proxies = [
        {
            "name": "proxy1",
            "http": "http://proxy1.example.com:8080",
            "https": "https://proxy1.example.com:8080",
            "enabled": True
        },
        {
            "name": "proxy2", 
            "http": "http://proxy2.example.com:3128",
            "https": "https://proxy2.example.com:3128",
            "enabled": True
        }
    ]
    
    # 保存到配置文件
    config = {
        "proxies": proxies,
        "rotation_interval": 300,  # 5分钟轮换一次
        "max_failures": 3,  # 最大失败次数
        "timeout": 30  # 超时时间
    }
    
    with open('proxy_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("代理配置已保存到 proxy_config.json")

if __name__ == "__main__":
    setup_proxy_config()
```

### 2. 更新AKShare配置

```python
# 在 backend_core/config/config.py 中添加
import json
from pathlib import Path

def load_proxy_pool():
    """加载代理池配置"""
    config_file = Path('proxy_config.json')
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        proxy_pool = []
        for proxy in config['proxies']:
            if proxy['enabled']:
                proxy_pool.append({
                    'http': proxy['http'],
                    'https': proxy['https']
                })
        
        return proxy_pool
    return []

# 更新DATA_COLLECTORS配置
DATA_COLLECTORS = {
    'akshare': {
        'max_retries': 3,
        'retry_delay': 5,
        'timeout': 30,
        'log_dir': str(ROOT_DIR / 'backend_core' / 'logs'),
        'db_file': str(DB_DIR / 'stock_analysis.db'),
        'max_connection_errors': 10,
        # 动态加载代理池
        'proxy_pool': load_proxy_pool(),
        'random_delay_range': (1, 3),
        'ssl_verify': False,
        'use_fallback_sources': True,
    }
}
```

### 3. 测试代理配置

```python
# test_proxy.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend_core.data_collectors.akshare.enhanced_base import EnhancedAKShareCollector

def test_with_proxy():
    """测试代理配置"""
    print("测试代理配置...")
    
    try:
        collector = EnhancedAKShareCollector()
        
        # 测试获取股票列表
        df = collector.get_stock_list()
        print(f"✅ 代理配置成功: 获取到 {len(df)} 条数据")
        return True
        
    except Exception as e:
        print(f"❌ 代理配置失败: {e}")
        return False

if __name__ == "__main__":
    test_with_proxy()
```

## 注意事项

1. **代理服务器稳定性**：免费代理通常不稳定，建议使用付费代理服务
2. **代理认证**：某些代理需要用户名和密码认证
3. **代理类型**：HTTP代理和SOCKS代理的使用方式不同
4. **代理轮换**：建议实现代理轮换机制，避免单个代理被限制
5. **代理验证**：定期验证代理的可用性，及时移除失效的代理
6. **法律合规**：使用代理时请遵守相关法律法规

## 推荐的代理服务商

### 付费代理服务（推荐）

1. **Bright Data (Luminati)**
   - 网址: https://brightdata.com/
   - 特点: 高质量住宅代理，稳定性好

2. **Oxylabs**
   - 网址: https://oxylabs.io/
   - 特点: 专业代理服务，支持多种协议

3. **Smartproxy**
   - 网址: https://smartproxy.com/
   - 特点: 价格合理，支持多种代理类型

### 免费代理服务

1. **ProxyMesh**
   - 网址: https://proxymesh.com/
   - 特点: 提供免费试用

2. **ProxyList**
   - 网址: https://www.proxy-list.download/
   - 特点: 免费代理列表

通过以上配置，您就可以使用代理服务器来解决AKShare的连接问题了。
