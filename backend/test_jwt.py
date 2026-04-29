#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT Token 测试脚本
用于验证 JWT token 的生成和解析是否正常
"""

from app import create_app, db
from app.models import User
from flask_jwt_extended import create_access_token, decode_token
import sys

def test_jwt():
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("JWT Token 测试")
        print("=" * 60)
        
        # 1. 检查配置
        print("\n1. JWT 配置:")
        print(f"   JWT_SECRET_KEY: {app.config.get('JWT_SECRET_KEY')}")
        print(f"   JWT_TOKEN_LOCATION: {app.config.get('JWT_TOKEN_LOCATION')}")
        print(f"   JWT_HEADER_NAME: {app.config.get('JWT_HEADER_NAME')}")
        print(f"   JWT_HEADER_TYPE: {app.config.get('JWT_HEADER_TYPE')}")
        print(f"   JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")
        
        # 2. 查找测试用户
        print("\n2. 查找测试用户:")
        user = User.query.filter_by(username='张三').first()
        if not user:
            print("   ❌ 找不到测试用户 '张三'")
            print("   请先运行数据库初始化脚本")
            return False
        
        print(f"   ✓ 找到用户: {user.username} (ID: {user.id})")
        
        # 3. 生成 token
        print("\n3. 生成 JWT Token:")
        try:
            token = create_access_token(identity=str(user.id))
            print(f"   ✓ Token 生成成功")
            print(f"   Token (前50字符): {token[:50]}...")
            print(f"   Token 长度: {len(token)}")
        except Exception as e:
            print(f"   ❌ Token 生成失败: {e}")
            return False
        
        # 4. 解析 token
        print("\n4. 解析 JWT Token:")
        try:
            decoded = decode_token(token)
            print(f"   ✓ Token 解析成功")
            print(f"   用户ID: {decoded.get('sub')}")
            print(f"   过期时间: {decoded.get('exp')}")
            print(f"   Token类型: {decoded.get('type')}")
        except Exception as e:
            print(f"   ❌ Token 解析失败: {e}")
            return False
        
        # 5. 验证用户ID匹配
        print("\n5. 验证用户ID:")
        decoded_user_id = int(decoded.get('sub'))
        if decoded_user_id == user.id:
            print(f"   ✓ 用户ID匹配: {user.id}")
        else:
            print(f"   ❌ 用户ID不匹配: 期望 {user.id}, 实际 {decoded_user_id}")
            return False
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！JWT 配置正常")
        print("=" * 60)
        return True

if __name__ == '__main__':
    success = test_jwt()
    sys.exit(0 if success else 1)
