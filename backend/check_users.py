#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的用户信息
"""

from app import create_app, db
from app.models import User

def check_users():
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("数据库用户列表")
        print("=" * 60)
        
        users = User.query.all()
        
        if not users:
            print("数据库中没有用户！")
            return
        
        print(f"\n共有 {len(users)} 个用户：\n")
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"  用户名: {user.username}")
            print(f"  邮箱: {user.email}")
            print(f"  角色: {user.role}")
            print(f"  状态: {user.status}")
            print(f"  密码哈希: {user.password[:50] if user.password else 'None'}...")
            
            # 测试密码
            test_passwords = ['password123', 'admin123', '123456']
            for pwd in test_passwords:
                if user.check_password(pwd):
                    print(f"  ✓ 密码是: {pwd}")
                    break
            else:
                print(f"  ⚠ 密码未知（不在常用测试密码中）")
            
            print()

if __name__ == '__main__':
    check_users()
