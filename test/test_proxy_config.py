#!/usr/bin/env python3
"""
代理配置测试脚本
快速测试代理配置是否有效
"""

import sys
from pathlib import Path
import requests
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_proxy_connection(proxy_dict, timeout=10):
    """测试代理连接"""
    try:
        print(f"🔍 测试代理: {proxy_dict['http']}")
        
        response = requests.get(
            'https://httpbin.org/ip', 
            proxies=proxy_dict, 
            timeout=timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 代理连接成功")
            print(f"   外部IP: {result.get('origin', 'Unknown')}")
            return True, result
        else:
            print(f"❌ 代理连接失败: HTTP {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ 代理连接失败: {e}")
        return False, str(e)

def test_akshare_with_proxy():
    """测试AKShare是否能正常工作"""
    print("\n🧪 测试AKShare连接...")
    
    try:
        from backend_core.data_collectors.akshare.enhanced_base import EnhancedAKShareCollector
        
        collector = EnhancedAKShareCollector()
        df = collector.get_stock_list()
        
        print(f"✅ AKShare测试成功: 获取到 {len(df)} 条数据")
        return True
        
    except Exception as e:
        print(f"❌ AKShare测试失败: {e}")
        return False

def load_proxy_config():
    """加载代理配置"""
    config_file = Path('proxy_config.json')
    
    if not config_file.exists():
        print("❌ 代理配置文件不存在")
        print("💡 请先运行: python scripts/setup_proxy.py")
        return []
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
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
                    'https': https_proxy,
                    'name': proxy['name']
                })
        
        return proxy_pool
        
    except Exception as e:
        print(f"❌ 加载代理配置失败: {e}")
        return []

def main():
    """主函数"""
    print("🚀 代理配置测试工具")
    print("=" * 50)
    
    # 加载代理配置
    proxy_pool = load_proxy_config()
    
    if not proxy_pool:
        print("❌ 没有可用的代理配置")
        return
    
    print(f"📁 已加载 {len(proxy_pool)} 个代理配置")
    
    # 测试每个代理
    valid_proxies = []
    for proxy in proxy_pool:
        print(f"\n📡 测试代理: {proxy['name']}")
        is_valid, result = test_proxy_connection(proxy)
        if is_valid:
            valid_proxies.append(proxy)
    
    print(f"\n📊 测试结果: {len(valid_proxies)}/{len(proxy_pool)} 个代理可用")
    
    if valid_proxies:
        print("\n🧪 测试AKShare连接...")
        if test_akshare_with_proxy():
            print("\n🎉 代理配置测试完成！AKShare可以正常使用了")
        else:
            print("\n⚠️ 代理配置测试完成，但AKShare测试失败")
            print("💡 建议检查代理服务器是否支持HTTPS连接")
    else:
        print("\n❌ 没有可用的代理服务器")
        print("💡 建议:")
        print("1. 检查代理服务器地址和端口是否正确")
        print("2. 检查代理服务器是否需要认证")
        print("3. 尝试使用其他代理服务器")

if __name__ == "__main__":
    main()
