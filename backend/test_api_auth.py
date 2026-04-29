#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 认证测试脚本
测试完整的登录和认证流程
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def test_auth_flow():
    print("=" * 60)
    print("API 认证流程测试")
    print("=" * 60)
    
    # 1. 测试登录
    print("\n1. 测试登录:")
    login_data = {
        'username': '张三',
        'password': 'password123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            user = data.get('user')
            print(f"   ✓ 登录成功")
            print(f"   用户: {user.get('username')}")
            print(f"   Token (前50字符): {token[:50]}...")
        else:
            print(f"   ❌ 登录失败: {response.json()}")
            return False
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        print(f"   请确保 Flask 服务器正在运行 (python run.py)")
        return False
    
    # 2. 测试获取个人信息
    print("\n2. 测试获取个人信息 (/auth/profile):")
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(f'{BASE_URL}/auth/profile', headers=headers)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 获取成功")
            print(f"   用户: {data.get('user', {}).get('username')}")
        else:
            print(f"   ❌ 获取失败: {response.json()}")
            return False
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return False
    
    # 3. 测试获取我的评分
    print("\n3. 测试获取我的评分 (/ratings/my?game_id=1):")
    
    try:
        response = requests.get(f'{BASE_URL}/ratings/my?game_id=1', headers=headers)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 获取成功")
            rating = data.get('rating')
            if rating:
                print(f"   已评分: 综合评分 {rating.get('overall_score')}")
            else:
                print(f"   尚未评分")
        else:
            print(f"   ❌ 获取失败: {response.json()}")
            return False
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return False
    
    # 4. 测试创建评分
    print("\n4. 测试创建评分:")
    rating_data = {
        'game_id': 1,
        'gameplay_score': 9.0,
        'graphics_score': 8.5,
        'story_score': 9.5,
        'sound_score': 8.0,
        'overall_score': 9.0
    }
    
    try:
        response = requests.post(f'{BASE_URL}/ratings', json=rating_data, headers=headers)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   ✓ {data.get('message')}")
        else:
            print(f"   ❌ 创建失败: {response.json()}")
            return False
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return False
    
    # 5. 测试无效 token
    print("\n5. 测试无效 Token:")
    invalid_headers = {
        'Authorization': 'Bearer invalid_token_here'
    }
    
    try:
        response = requests.get(f'{BASE_URL}/auth/profile', headers=invalid_headers)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 422:
            print(f"   ✓ 正确返回 422 错误")
            print(f"   错误信息: {response.json().get('message')}")
        else:
            print(f"   ⚠ 状态码不是预期的 422: {response.json()}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！API 认证流程正常")
    print("=" * 60)
    return True

if __name__ == '__main__':
    import sys
    success = test_auth_flow()
    sys.exit(0 if success else 1)
