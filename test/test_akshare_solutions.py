#!/usr/bin/env python3
"""
AKShare连接问题解决方案测试
提供多种解决方案的测试和演示
"""

import sys
import os
from pathlib import Path
import time
import random

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_solution_1_proxy():
    """解决方案1：使用代理"""
    print("=" * 60)
    print("解决方案1：使用代理服务器")
    print("=" * 60)
    
    try:
        import requests
        
        # 示例代理配置（需要替换为实际可用的代理）
        proxies = {
            'http': 'http://proxy.example.com:8080',
            'https': 'https://proxy.example.com:8080'
        }
        
        print("1. 测试代理连接...")
        print("   注意：需要配置实际可用的代理服务器")
        print("   配置示例：")
        print("   - HTTP代理: http://proxy.example.com:8080")
        print("   - SOCKS代理: socks5://proxy.example.com:1080")
        
        # 测试代理连接
        try:
            response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
            print(f"   代理测试成功: {response.json()}")
            return True
        except Exception as e:
            print(f"   代理测试失败: {e}")
            return False
            
    except Exception as e:
        print(f"代理解决方案测试失败: {e}")
        return False

def test_solution_2_requests_config():
    """解决方案2：优化requests配置"""
    print("\n" + "=" * 60)
    print("解决方案2：优化requests配置")
    print("=" * 60)
    
    try:
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # 创建优化的session
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置User-Agent
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        print("1. 测试优化的requests配置...")
        try:
            # 测试连接
            response = session.get('https://httpbin.org/user-agent', timeout=10)
            print(f"   配置测试成功: {response.json()}")
            return True
        except Exception as e:
            print(f"   配置测试失败: {e}")
            return False
            
    except Exception as e:
        print(f"requests配置解决方案测试失败: {e}")
        return False

def test_solution_3_alternative_sources():
    """解决方案3：备用数据源"""
    print("\n" + "=" * 60)
    print("解决方案3：备用数据源")
    print("=" * 60)
    
    print("1. 推荐的备用数据源：")
    print("   - Tushare (需要Token)")
    print("   - 新浪财经API")
    print("   - 腾讯财经API")
    print("   - 网易财经API")
    print("   - 和讯财经API")
    
    print("\n2. Tushare示例代码：")
    print("""
import tushare as ts

# 设置Token
ts.set_token('your_token')
pro = ts.pro_api()

# 获取实时行情
df = pro.daily_basic(ts_code='', trade_date='20231201')
""")
    
    print("\n3. 新浪财经API示例：")
    print("""
import requests

# 获取股票列表
url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData'
params = {
    'page': 1,
    'num': 100,
    'sort': 'symbol',
    'asc': 1,
    'node': 'hs_a',
    'symbol': ''
}
response = requests.get(url, params=params)
""")
    
    return True

def test_solution_4_enhanced_collector():
    """解决方案4：增强的采集器"""
    print("\n" + "=" * 60)
    print("解决方案4：增强的采集器")
    print("=" * 60)
    
    try:
        from backend_core.data_collectors.akshare.enhanced_base import EnhancedAKShareCollector
        
        print("1. 创建增强采集器...")
        collector = EnhancedAKShareCollector()
        
        print("2. 测试基础功能...")
        try:
            # 测试获取股票列表
            df = collector.get_stock_list()
            print(f"   成功获取 {len(df)} 只股票信息")
            return True
        except Exception as e:
            print(f"   增强采集器测试失败: {e}")
            return False
            
    except Exception as e:
        print(f"增强采集器解决方案测试失败: {e}")
        return False

def test_solution_5_network_diagnostics():
    """解决方案5：网络诊断"""
    print("\n" + "=" * 60)
    print("解决方案5：网络诊断")
    print("=" * 60)
    
    print("1. 网络连接诊断...")
    
    # 测试DNS解析
    try:
        import socket
        ip = socket.gethostbyname('82.push2.eastmoney.com')
        print(f"   DNS解析成功: 82.push2.eastmoney.com -> {ip}")
    except Exception as e:
        print(f"   DNS解析失败: {e}")
    
    # 测试端口连接
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('82.push2.eastmoney.com', 443))
        sock.close()
        if result == 0:
            print("   端口443连接成功")
        else:
            print("   端口443连接失败")
    except Exception as e:
        print(f"   端口连接测试失败: {e}")
    
    # 测试HTTP连接
    try:
        import requests
        response = requests.get('https://82.push2.eastmoney.com', timeout=10)
        print(f"   HTTP连接成功: 状态码 {response.status_code}")
    except Exception as e:
        print(f"   HTTP连接失败: {e}")
    
    return True

def main():
    """主测试函数"""
    print("AKShare连接问题解决方案测试")
    print("这个测试将演示多种解决方案")
    
    test_results = []
    
    # 测试各种解决方案
    test_results.append(("代理服务器", test_solution_1_proxy()))
    test_results.append(("优化requests配置", test_solution_2_requests_config()))
    test_results.append(("备用数据源", test_solution_3_alternative_sources()))
    test_results.append(("增强采集器", test_solution_4_enhanced_collector()))
    test_results.append(("网络诊断", test_solution_5_network_diagnostics()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("解决方案测试结果汇总")
    print("=" * 60)
    
    for solution_name, result in test_results:
        status = "✅ 可用" if result else "❌ 不可用"
        print(f"{solution_name}: {status}")
    
    # 输出建议
    print("\n" + "=" * 60)
    print("解决建议")
    print("=" * 60)
    print("1. 如果网络环境允许，建议使用代理服务器")
    print("2. 如果无法使用代理，建议切换到Tushare或其他数据源")
    print("3. 可以考虑使用VPN或更换网络环境")
    print("4. 定期监控数据源可用性，实现自动故障转移")
    print("5. 配置多个备用数据源，确保数据采集的稳定性")

if __name__ == "__main__":
    main()
