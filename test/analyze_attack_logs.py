#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8000端口攻击日志分析脚本
分析恶意访问模式和安全威胁
"""

import re
from collections import Counter
from datetime import datetime

def analyze_attack_logs():
    """分析攻击日志"""
    
    # 模拟日志数据（从用户提供的日志中提取）
    log_entries = [
        "65.49.1.74 - - [11/Sep/2025 12:20:13] \"GET /favicon.ico HTTP/1.1\" 200 -",
        "65.49.1.73 - - [11/Sep/2025 12:20:16] \"GET http://api.ipify.org/?format=json HTTP/1.1\" 301 -",
        "65.49.1.69 - - [11/Sep/2025 12:20:20] code 501, message Unsupported method ('CONNECT')",
        "65.49.1.69 - - [11/Sep/2025 12:20:20] \"CONNECT www.shadowserver.org:443 HTTP/1.1\" 501 -",
        "175.19.75.241 - - [11/Sep/2025 12:20:22] code 404, message File not found",
        "175.19.75.241 - - [11/Sep/2025 12:20:22] \"HEAD http://110.242.68.4/ HTTP/1.1\" 404 -",
        "221.207.34.91 - - [11/Sep/2025 12:20:43] \"GET http://www.epochtimes.com/ HTTP/1.1\" 301 -",
        "221.207.34.91 - - [11/Sep/2025 12:20:43] code 404, message File not found",
        "221.207.34.91 - - [11/Sep/2025 12:20:43] \"GET http://www.epochtimes.com/login.html HTTP/1.0\" 404 -",
        "221.207.34.91 - - [11/Sep/2025 12:20:43] \"GET http://www.minghui.org/ HTTP/1.1\" 301 -",
        "221.207.34.91 - - [11/Sep/2025 12:20:44] code 404, message File not found",
        "221.207.34.91 - - [11/Sep/2025 12:20:44] \"GET http://www.minghui.org/login.html HTTP/1.0\" 404 -",
        "221.207.34.91 - - [11/Sep/2025 12:20:44] \"GET http://www.soso.com/ HTTP/1.1\" 301 -",
        "221.207.34.91 - - [11/Sep/2025 12:20:44] code 404, message File not found",
        "221.207.34.91 - - [11/Sep/2025 12:20:44] \"GET http://www.soso.com/login.html HTTP/1.0\" 404 -",
        "221.207.34.91 - - [11/Sep/2025 12:20:44] \"GET http://www.wujieliulan.com/ HTTP/1.1\" 301 -",
        "221.207.34.91 - - [11/Sep/2025 12:20:44] code 404, message File not found",
        "221.207.34.91 - - [11/Sep/2025 12:20:44] \"GET http://www.wujieliulan.com/login.html HTTP/1.0\" 404 -",
        "221.207.34.91 - - [11/Sep/2025 12:20:45] code 404, message File not found",
        "221.207.34.91 - - [11/Sep/2025 12:20:45] \"GET http://www.rfa.org/english/ HTTP/1.1\" 404 -",
        "122.188.35.190 - - [11/Sep/2025 12:20:50] code 501, message Unsupported method ('CONNECT')",
        "122.188.35.190 - - [11/Sep/2025 12:20:50] \"CONNECT www.so.com:443 HTTP/1.1\" 501 -",
        "122.188.35.190 - - [11/Sep/2025 12:20:51] \"GET http://dongtaiwang.com/ HTTP/1.1\" 301 -",
        "122.188.35.190 - - [11/Sep/2025 12:20:51] code 404, message File not found",
        "122.188.35.190 - - [11/Sep/2025 12:20:51] \"GET http://dongtaiwang.com/login.html HTTP/1.0\" 404 -",
        "122.188.35.190 - - [11/Sep/2025 12:20:51] code 501, message Unsupported method ('CONNECT')",
        "122.188.35.190 - - [11/Sep/2025 12:20:51] \"CONNECT cn.bing.com:443 HTTP/1.1\" 501 -",
        "122.207.34.91 - - [11/Sep/2025 12:20:51] code 501, message Unsupported method ('CONNECT')",
        "122.188.35.190 - - [11/Sep/2025 12:20:51] \"CONNECT www.baidu.com:443 HTTP/1.1\" 501 -",
        "127.0.0.1 - - [11/Sep/2025 12:21:32] \"GET / HTTP/1.0\" 301 -",
        "127.0.0.1 - - [11/Sep/2025 12:22:54] \"GET / HTTP/1.0\" 301 -",
        "127.0.0.1 - - [11/Sep/2025 12:22:54] \"GET /login.html HTTP/1.0\" 200 -",
        "127.0.0.1 - - [11/Sep/2025 12:22:54] \"GET /css/common.css HTTP/1.0\" 200 -",
        "127.0.0.1 - - [11/Sep/2025 12:22:54] \"GET /js/common.js HTTP/1.0\" 200 -",
        "127.0.0.1 - - [11/Sep/2025 12:22:55] \"GET /js/login.js HTTP/1.0\" 200 -",
        "127.0.0.1 - - [11/Sep/2025 12:22:55] \"GET /js/config.js HTTP/1.0\" 200 -",
        "127.0.0.1 - - [11/Sep/2025 12:22:55] \"GET /css/login.css HTTP/1.0\" 200 -",
        "127.0.0.1 - - [11/Sep/2025 12:23:10] \"GET / HTTP/1.0\" 301 -"
    ]
    
    print("=" * 80)
    print("                   8000端口攻击日志分析报告")
    print("=" * 80)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 提取IP地址
    ip_pattern = r'(\d+\.\d+\.\d+\.\d+)'
    ips = []
    for entry in log_entries:
        match = re.search(ip_pattern, entry)
        if match:
            ips.append(match.group(1))
    
    # 统计IP访问次数
    ip_counts = Counter(ips)
    
    print("=== 攻击源IP分析 ===")
    print(f"总访问次数: {len(log_entries)}")
    print(f"唯一IP数量: {len(ip_counts)}")
    print()
    
    print("IP访问统计:")
    for ip, count in ip_counts.most_common():
        if ip != "127.0.0.1":  # 排除本地访问
            print(f"  {ip:15} - {count:3} 次访问")
    
    print()
    
    # 分析攻击类型
    print("=== 攻击类型分析 ===")
    
    # 1. CONNECT方法攻击（代理隧道攻击）
    connect_attacks = [entry for entry in log_entries if "CONNECT" in entry]
    print(f"1. CONNECT方法攻击: {len(connect_attacks)} 次")
    print("   目的: 尝试建立代理隧道，绕过防火墙")
    print("   目标网站: shadowserver.org, so.com, cn.bing.com, baidu.com")
    print()
    
    # 2. 恶意域名访问
    malicious_domains = [
        "epochtimes.com", "minghui.org", "soso.com", 
        "wujieliulan.com", "rfa.org", "dongtaiwang.com"
    ]
    domain_attacks = [entry for entry in log_entries if any(domain in entry for domain in malicious_domains)]
    print(f"2. 恶意域名访问: {len(domain_attacks)} 次")
    print("   目的: 尝试访问被屏蔽的网站")
    print("   特征: 访问敏感政治网站")
    print()
    
    # 3. 登录页面扫描
    login_attacks = [entry for entry in log_entries if "login.html" in entry]
    print(f"3. 登录页面扫描: {len(login_attacks)} 次")
    print("   目的: 寻找登录入口，准备暴力破解")
    print()
    
    # 4. 正常访问（本地）
    local_access = [entry for entry in log_entries if "127.0.0.1" in entry]
    print(f"4. 正常本地访问: {len(local_access)} 次")
    print("   说明: 这些是正常的本地访问")
    print()
    
    # 威胁等级评估
    print("=== 威胁等级评估 ===")
    total_attacks = len(log_entries) - len(local_access)
    if total_attacks > 20:
        threat_level = "🔴 高危"
    elif total_attacks > 10:
        threat_level = "🟡 中危"
    else:
        threat_level = "🟢 低危"
    
    print(f"威胁等级: {threat_level}")
    print(f"攻击次数: {total_attacks}")
    print(f"攻击IP数: {len([ip for ip in ip_counts.keys() if ip != '127.0.0.1'])}")
    print()
    
    # 攻击特征
    print("=== 攻击特征 ===")
    print("1. 多IP协同攻击")
    print("2. 使用CONNECT方法尝试建立代理隧道")
    print("3. 访问敏感政治网站")
    print("4. 扫描登录页面")
    print("5. 使用HTTP/1.0和HTTP/1.1协议")
    print()
    
    return {
        'total_attacks': total_attacks,
        'threat_level': threat_level,
        'attack_ips': [ip for ip in ip_counts.keys() if ip != '127.0.0.1'],
        'attack_types': ['CONNECT攻击', '恶意域名访问', '登录页面扫描']
    }

def generate_security_recommendations():
    """生成安全建议"""
    print("=== 安全防护建议 ===")
    print()
    
    print("🔒 立即措施:")
    print("1. 限制8000端口访问")
    print("   - 只允许特定IP访问")
    print("   - 使用防火墙规则")
    print()
    
    print("2. 启用访问日志监控")
    print("   - 实时监控异常访问")
    print("   - 设置告警机制")
    print()
    
    print("3. 配置nginx反向代理")
    print("   - 隐藏真实服务端口")
    print("   - 添加访问控制")
    print()
    
    print("🛡️ 长期防护:")
    print("1. 部署Web应用防火墙(WAF)")
    print("2. 启用DDoS防护")
    print("3. 定期安全扫描")
    print("4. 更新安全补丁")
    print()
    
    print("📊 监控建议:")
    print("1. 设置IP黑名单")
    print("2. 监控异常流量")
    print("3. 定期分析访问日志")
    print("4. 建立安全事件响应流程")

if __name__ == "__main__":
    result = analyze_attack_logs()
    generate_security_recommendations()
    
    print()
    print("=" * 80)
    print("                   分析完成")
    print("=" * 80)
    print("建议立即采取安全防护措施！")
