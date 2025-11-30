#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试密码哈希修复
"""

import sys
import os

# 添加backend_api到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend_api'))

from auth import get_password_hash

def test_normal_password():
    """测试正常密码"""
    print("测试1: 正常密码（10个字符）")
    try:
        password = "password123"
        hash_result = get_password_hash(password)
        print(f"✅ 成功: 密码长度 {len(password.encode('utf-8'))} 字节")
        print(f"   哈希值: {hash_result[:50]}...")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

def test_long_password():
    """测试长密码（超过72字节）"""
    print("\n测试2: 长密码（100个字符，超过72字节）")
    try:
        password = "a" * 100  # 100个字符
        password_bytes = len(password.encode('utf-8'))
        print(f"   原始密码长度: {password_bytes} 字节")
        hash_result = get_password_hash(password)
        print(f"✅ 成功: 密码已自动截断并生成哈希")
        print(f"   哈希值: {hash_result[:50]}...")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_very_long_password():
    """测试超长密码（200个字符）"""
    print("\n测试3: 超长密码（200个字符）")
    try:
        password = "b" * 200  # 200个字符
        password_bytes = len(password.encode('utf-8'))
        print(f"   原始密码长度: {password_bytes} 字节")
        hash_result = get_password_hash(password)
        print(f"✅ 成功: 密码已自动截断并生成哈希")
        print(f"   哈希值: {hash_result[:50]}...")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unicode_password():
    """测试包含Unicode字符的密码"""
    print("\n测试4: Unicode密码（中文+英文）")
    try:
        password = "密码password123" * 10  # 包含中文
        password_bytes = len(password.encode('utf-8'))
        print(f"   原始密码长度: {password_bytes} 字节")
        hash_result = get_password_hash(password)
        print(f"✅ 成功: 密码已处理并生成哈希")
        print(f"   哈希值: {hash_result[:50]}...")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("密码哈希修复测试")
    print("=" * 60)
    
    results = []
    results.append(test_normal_password())
    results.append(test_long_password())
    results.append(test_very_long_password())
    results.append(test_unicode_password())
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if all(results):
        print("\n🎉 所有测试通过！密码哈希修复成功。")
        print("\n⚠️  重要提示：请重启后端服务以使修复生效！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())

