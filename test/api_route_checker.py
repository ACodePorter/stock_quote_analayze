#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由规范检查脚本
用于验证所有API路由是否符合统一规范
"""

import os
import re
import sys
from pathlib import Path

def check_api_routes():
    """检查所有API路由是否符合规范"""
    
    # 项目根目录
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend_api"
    
    # 需要检查的文件模式
    patterns = [
        "*.py",
        "admin/*.py",
        "stock/*.py"
    ]
    
    # 收集所有Python文件
    python_files = []
    for pattern in patterns:
        python_files.extend(backend_dir.glob(pattern))
    
    # 过滤掉__pycache__和__init__.py
    python_files = [f for f in python_files if not f.name.startswith('__') and f.name != '__init__.py']
    
    print("🔍 开始检查API路由规范...")
    print("=" * 60)
    
    issues = []
    valid_routes = []
    
    # 检查每个文件
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 查找router = APIRouter行
            router_pattern = r'router\s*=\s*APIRouter\s*\(\s*prefix\s*=\s*["\']([^"\']+)["\']'
            matches = re.findall(router_pattern, content)
            
            for match in matches:
                prefix = match.strip()
                relative_path = file_path.relative_to(project_root)
                
                # 检查是否以/api开头
                if not prefix.startswith('/api/'):
                    issues.append({
                        'file': str(relative_path),
                        'prefix': prefix,
                        'issue': '缺少 /api/ 前缀'
                    })
                else:
                    valid_routes.append({
                        'file': str(relative_path),
                        'prefix': prefix
                    })
                    
        except Exception as e:
            print(f"❌ 读取文件 {file_path} 时出错: {e}")
    
    # 输出结果
    print(f"📊 检查结果:")
    print(f"   - 检查文件数: {len(python_files)}")
    print(f"   - 有效路由数: {len(valid_routes)}")
    print(f"   - 问题路由数: {len(issues)}")
    print()
    
    if valid_routes:
        print("✅ 符合规范的路由:")
        for route in valid_routes:
            print(f"   📁 {route['file']:<30} -> {route['prefix']}")
        print()
    
    if issues:
        print("❌ 需要修复的路由:")
        for issue in issues:
            print(f"   📁 {issue['file']:<30} -> {issue['prefix']:<20} ({issue['issue']})")
        print()
        
        print("🔧 修复建议:")
        for issue in issues:
            if not issue['prefix'].startswith('/api/'):
                suggested_prefix = f"/api{issue['prefix']}" if issue['prefix'].startswith('/') else f"/api/{issue['prefix']}"
                print(f"   {issue['file']}: {issue['prefix']} -> {suggested_prefix}")
        print()
        
        return False
    else:
        print("🎉 所有API路由都符合规范！")
        print()
        
        # 检查是否有重复的路由前缀
        prefixes = [route['prefix'] for route in valid_routes]
        duplicates = [p for p in set(prefixes) if prefixes.count(p) > 1]
        
        if duplicates:
            print("⚠️  发现重复的路由前缀:")
            for dup in duplicates:
                files = [route['file'] for route in valid_routes if route['prefix'] == dup]
                print(f"   {dup}: {', '.join(files)}")
            print()
            return False
        else:
            print("✅ 没有发现重复的路由前缀")
            return True

def check_frontend_api_config():
    """检查前端API配置"""
    print("🔍 检查前端API配置...")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    api_config_file = project_root / "admin" / "src" / "config" / "api.ts"
    
    if not api_config_file.exists():
        print("❌ 前端API配置文件不存在")
        return False
    
    try:
        with open(api_config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查生产环境配置
        production_pattern = r"production:\s*{[^}]*baseURL:\s*['\"]([^'\"]+)['\"]"
        match = re.search(production_pattern, content)
        
        if match:
            base_url = match.group(1)
            if '/api' in base_url:
                print(f"❌ 前端生产环境baseURL包含 /api: {base_url}")
                print("   建议: 移除 /api 前缀，因为后端路由已统一包含")
                return False
            else:
                print(f"✅ 前端生产环境baseURL配置正确: {base_url}")
                return True
        else:
            print("❌ 未找到生产环境baseURL配置")
            return False
            
    except Exception as e:
        print(f"❌ 读取前端API配置文件时出错: {e}")
        return False

def main():
    """主函数"""
    print("🚀 API路由规范检查工具")
    print("=" * 60)
    
    # 检查后端路由
    backend_ok = check_api_routes()
    
    print()
    
    # 检查前端配置
    frontend_ok = check_frontend_api_config()
    
    print()
    print("=" * 60)
    
    if backend_ok and frontend_ok:
        print("🎉 所有检查都通过！API路由规范统一。")
        return 0
    else:
        print("❌ 发现问题，请根据上述建议进行修复。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
