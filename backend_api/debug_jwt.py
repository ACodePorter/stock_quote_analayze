#!/usr/bin/env python3
"""
JWT调试工具
用于诊断和测试JWT令牌相关问题
"""

import jwt
import json
from datetime import datetime, timedelta

# JWT配置（与admin模块保持一致）
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

def create_test_token(username: str = "admin", expires_minutes: int = None):
    """创建测试JWT令牌"""
    if expires_minutes is None:
        expires_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    # 创建令牌数据
    data = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    # 编码JWT
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_and_validate_token(token: str):
    """解码和验证JWT令牌"""
    try:
        # 解码令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 检查必要字段
        username = payload.get("sub")
        exp = payload.get("exp")
        iat = payload.get("iat")
        
        # 转换时间戳
        if exp:
            exp_time = datetime.fromtimestamp(exp)
            exp_str = exp_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            exp_str = "未设置"
            
        if iat:
            iat_time = datetime.fromtimestamp(iat)
            iat_str = iat_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            iat_str = "未设置"
        
        # 检查是否过期
        current_time = datetime.utcnow()
        is_expired = exp and current_time > exp_time
        
        return {
            "valid": True,
            "username": username,
            "exp": exp_str,
            "iat": iat_str,
            "is_expired": is_expired,
            "payload": payload
        }
        
    except jwt.ExpiredSignatureError:
        return {
            "valid": False,
            "error": "令牌已过期",
            "error_type": "ExpiredSignatureError"
        }
    except jwt.InvalidTokenError as e:
        return {
            "valid": False,
            "error": f"无效令牌: {str(e)}",
            "error_type": "InvalidTokenError"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"未知错误: {str(e)}",
            "error_type": "UnknownError"
        }

def test_jwt_functionality():
    """测试JWT功能"""
    print("🔐 JWT调试工具")
    print("=" * 50)
    
    # 测试1: 创建有效令牌
    print("\n📝 测试1: 创建有效令牌")
    valid_token = create_test_token("admin", 60)
    print(f"令牌: {valid_token[:50]}...")
    
    # 测试2: 验证有效令牌
    print("\n✅ 测试2: 验证有效令牌")
    result = decode_and_validate_token(valid_token)
    if result["valid"]:
        print(f"✅ 令牌有效")
        print(f"   用户: {result['username']}")
        print(f"   过期时间: {result['exp']}")
        print(f"   签发时间: {result['iat']}")
        print(f"   是否过期: {result['is_expired']}")
    else:
        print(f"❌ 令牌无效: {result['error']}")
    
    # 测试3: 创建过期令牌
    print("\n⏰ 测试3: 创建过期令牌")
    expired_token = create_test_token("admin", -1)  # 已过期
    result = decode_and_validate_token(expired_token)
    if result["valid"]:
        print(f"✅ 令牌有效")
    else:
        print(f"❌ 令牌无效: {result['error']}")
    
    # 测试4: 测试无效令牌
    print("\n❌ 测试4: 测试无效令牌")
    invalid_token = "invalid.token.here"
    result = decode_and_validate_token(invalid_token)
    if result["valid"]:
        print(f"✅ 令牌有效")
    else:
        print(f"❌ 令牌无效: {result['error']}")
    
    # 测试5: 测试空令牌
    print("\n🚫 测试5: 测试空令牌")
    result = decode_and_validate_token("")
    if result["valid"]:
        print(f"✅ 令牌有效")
    else:
        print(f"❌ 令牌无效: {result['error']}")

def debug_specific_token(token: str):
    """调试特定的JWT令牌"""
    print(f"\n🔍 调试令牌: {token[:50]}...")
    print("=" * 50)
    
    result = decode_and_validate_token(token)
    
    if result["valid"]:
        print("✅ 令牌分析结果:")
        print(f"   用户: {result['username']}")
        print(f"   过期时间: {result['exp']}")
        print(f"   签发时间: {result['iat']}")
        print(f"   是否过期: {result['is_expired']}")
        print(f"   完整载荷: {json.dumps(result['payload'], indent=2, ensure_ascii=False)}")
    else:
        print("❌ 令牌分析结果:")
        print(f"   错误类型: {result['error_type']}")
        print(f"   错误信息: {result['error']}")

if __name__ == "__main__":
    # 运行测试
    test_jwt_functionality()
    
    # 如果有命令行参数，调试特定令牌
    import sys
    if len(sys.argv) > 1:
        token = sys.argv[1]
        debug_specific_token(token)
