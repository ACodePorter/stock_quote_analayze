#!/usr/bin/env python3
"""
代理服务器配置脚本
帮助用户快速配置代理服务器来解决AKShare连接问题
"""

import json
import os
from pathlib import Path
import requests
import time
from concurrent.futures import ThreadPoolExecutor

class ProxySetup:
    def __init__(self):
        self.config_file = Path('proxy_config.json')
        self.proxy_pool = []
        
    def create_default_config(self):
        """创建默认代理配置"""
        config = {
            "proxies": [
                {
                    "name": "proxy1",
                    "http": "http://proxy1.example.com:8080",
                    "https": "https://proxy1.example.com:8080",
                    "username": "",
                    "password": "",
                    "enabled": False
                },
                {
                    "name": "proxy2",
                    "http": "http://proxy2.example.com:3128", 
                    "https": "https://proxy2.example.com:3128",
                    "username": "",
                    "password": "",
                    "enabled": False
                }
            ],
            "rotation_interval": 300,
            "max_failures": 3,
            "timeout": 30
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 默认代理配置已创建: {self.config_file}")
        print("请编辑配置文件，添加您的代理服务器信息")
        
    def load_config(self):
        """加载代理配置"""
        if not self.config_file.exists():
            print("❌ 代理配置文件不存在，正在创建...")
            self.create_default_config()
            return False
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.proxy_pool = []
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
                    
                    self.proxy_pool.append({
                        'http': http_proxy,
                        'https': https_proxy,
                        'name': proxy['name']
                    })
            
            print(f"✅ 已加载 {len(self.proxy_pool)} 个启用的代理")
            return True
            
        except Exception as e:
            print(f"❌ 加载代理配置失败: {e}")
            return False
    
    def test_proxy(self, proxy_dict, timeout=10):
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
    
    def validate_proxy_pool(self):
        """验证代理池中的所有代理"""
        if not self.proxy_pool:
            print("❌ 没有可用的代理服务器")
            return []
            
        print(f"🔍 正在验证 {len(self.proxy_pool)} 个代理服务器...")
        valid_proxies = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.test_proxy, proxy) for proxy in self.proxy_pool]
            
            for i, future in enumerate(futures):
                is_valid, result = future.result()
                proxy_name = self.proxy_pool[i]['name']
                
                if is_valid:
                    valid_proxies.append(self.proxy_pool[i])
                    print(f"✅ 代理 {proxy_name} 可用 - IP: {result.get('origin', 'Unknown')}")
                else:
                    print(f"❌ 代理 {proxy_name} 不可用: {result}")
        
        print(f"📊 验证结果: {len(valid_proxies)}/{len(self.proxy_pool)} 个代理可用")
        return valid_proxies
    
    def update_akshare_config(self, valid_proxies):
        """更新AKShare配置文件"""
        if not valid_proxies:
            print("❌ 没有可用的代理，无法更新配置")
            return False
            
        try:
            # 读取当前配置
            config_file = Path('backend_core/config/config.py')
            if not config_file.exists():
                print("❌ AKShare配置文件不存在")
                return False
                
            with open(config_file, 'r', encoding='utf-8') as f:
                content = config_file.read_text(encoding='utf-8')
            
            # 更新代理池配置
            proxy_pool_str = str(valid_proxies).replace("'", '"')
            
            # 查找并替换代理池配置
            import re
            pattern = r"'proxy_pool':\s*\[.*?\]"
            replacement = f"'proxy_pool': {proxy_pool_str}"
            
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            else:
                # 如果没有找到代理池配置，添加到akshare配置中
                pattern = r"'akshare':\s*\{([^}]*)\}"
                replacement = f"'akshare': {{\\1        'proxy_pool': {proxy_pool_str},\n    }}"
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            # 写回配置文件
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 已更新AKShare配置文件，添加了 {len(valid_proxies)} 个代理")
            return True
            
        except Exception as e:
            print(f"❌ 更新AKShare配置失败: {e}")
            return False
    
    def test_akshare_with_proxy(self):
        """测试AKShare是否能正常工作"""
        print("🧪 测试AKShare连接...")
        
        try:
            # 导入增强采集器
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            from backend_core.data_collectors.akshare.enhanced_base import EnhancedAKShareCollector
            
            collector = EnhancedAKShareCollector()
            df = collector.get_stock_list()
            
            print(f"✅ AKShare测试成功: 获取到 {len(df)} 条数据")
            return True
            
        except Exception as e:
            print(f"❌ AKShare测试失败: {e}")
            return False
    
    def interactive_setup(self):
        """交互式设置代理"""
        print("🔧 交互式代理设置")
        print("=" * 50)
        
        # 询问代理类型
        print("请选择代理类型:")
        print("1. HTTP代理")
        print("2. SOCKS5代理")
        print("3. 跳过设置")
        
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == '3':
            print("跳过代理设置")
            return False
            
        if choice not in ['1', '2']:
            print("❌ 无效选择")
            return False
        
        # 收集代理信息
        proxy_type = "HTTP" if choice == '1' else "SOCKS5"
        protocol = "http" if choice == '1' else "socks5"
        
        print(f"\n设置 {proxy_type} 代理:")
        
        host = input("代理服务器地址: ").strip()
        if not host:
            print("❌ 代理服务器地址不能为空")
            return False
            
        port = input("代理服务器端口: ").strip()
        if not port:
            print("❌ 代理服务器端口不能为空")
            return False
        
        username = input("用户名 (可选，直接回车跳过): ").strip()
        password = input("密码 (可选，直接回车跳过): ").strip()
        
        # 构建代理URL
        if username and password:
            proxy_url = f"{protocol}://{username}:{password}@{host}:{port}"
        else:
            proxy_url = f"{protocol}://{host}:{port}"
        
        # 测试代理
        print(f"\n🧪 测试代理: {proxy_url}")
        
        proxy_dict = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        is_valid, result = self.test_proxy(proxy_dict)
        
        if is_valid:
            print(f"✅ 代理测试成功: {result}")
            
            # 保存到配置
            self.proxy_pool = [proxy_dict]
            return True
        else:
            print(f"❌ 代理测试失败: {result}")
            return False

def main():
    """主函数"""
    print("🚀 AKShare代理配置工具")
    print("=" * 50)
    
    setup = ProxySetup()
    
    # 检查是否已有配置文件
    if setup.config_file.exists():
        print("📁 发现现有代理配置文件")
        choice = input("是否要重新配置? (y/n): ").strip().lower()
        
        if choice == 'y':
            setup.config_file.unlink()  # 删除现有配置
            print("🗑️ 已删除现有配置")
        else:
            print("📖 使用现有配置")
    
    # 加载配置
    if not setup.load_config():
        print("\n🔧 开始交互式设置...")
        if not setup.interactive_setup():
            print("❌ 代理设置失败")
            return
    
    # 验证代理
    print("\n🔍 验证代理服务器...")
    valid_proxies = setup.validate_proxy_pool()
    
    if not valid_proxies:
        print("❌ 没有可用的代理服务器")
        print("💡 建议:")
        print("1. 检查代理服务器地址和端口是否正确")
        print("2. 检查代理服务器是否需要认证")
        print("3. 尝试使用其他代理服务器")
        return
    
    # 更新AKShare配置
    print("\n⚙️ 更新AKShare配置...")
    if setup.update_akshare_config(valid_proxies):
        print("✅ 配置更新成功")
        
        # 测试AKShare
        print("\n🧪 测试AKShare连接...")
        if setup.test_akshare_with_proxy():
            print("\n🎉 代理配置完成！AKShare现在可以正常使用了")
        else:
            print("\n⚠️ 代理配置完成，但AKShare测试失败")
            print("💡 建议检查代理服务器是否支持HTTPS连接")
    else:
        print("❌ 配置更新失败")

if __name__ == "__main__":
    main()
