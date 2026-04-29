#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试登录功能
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def test_login(username, password):
    print(f"\n测试登录: {username} / {password}")
    print("-" * 50)
    
    login_data = {
        'username': username,
        'password': password
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            print("✓ 登录成功！")
            return response.json().get('token')
        else:
            print("✗ 登录失败")
            return None
            
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return None

if __name__ == '__main__':
    print("=" * 60)
    print("登录功能测试")
    print("=" * 60)
    
    # 测试管理员账号
    test_login('admin', 'admin123')
    
    # 测试普通用户
    test_login('张三', 'password123')
    
    # 测试错误密码
    test_login('张三', 'wrongpassword')
    
    # 测试不存在的用户
    test_login('notexist', 'password123')
    
    print("\n" + "=" * 60)
