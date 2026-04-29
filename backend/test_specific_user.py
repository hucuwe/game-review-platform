#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试特定用户的密码
"""

from app import create_app, db
from app.models import User

def test_user(username):
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"用户 '{username}' 不存在")
            return
        
        print(f"用户信息:")
        print(f"  ID: {user.id}")
        print(f"  用户名: {user.username}")
        print(f"  邮箱: {user.email}")
        print(f"  密码哈希: {user.password}")
        print()
        
        # 测试各种密码
        test_passwords = ['password123', 'admin123', '123456', 'aaa', 'aaa123']
        
        print("测试密码:")
        for pwd in test_passwords:
            result = user.check_password(pwd)
            status = "✓" if result else "✗"
            print(f"  {status} {pwd}: {result}")

if __name__ == '__main__':
    import sys
    username = sys.argv[1] if len(sys.argv) > 1 else 'aaa'
    test_user(username)
