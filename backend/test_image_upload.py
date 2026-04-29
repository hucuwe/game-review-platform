"""
测试图片上传功能
验证 cover_image 字段是否可以存储 Base64 编码的图片
"""
import requests
import base64
import json

# 测试配置
BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
UPDATE_GAME_URL = f"{BASE_URL}/api/games/1"

# 1. 登录获取 token
print("1. 登录管理员账号...")
login_data = {
    "username": "admin",
    "password": "admin123"
}
response = requests.post(LOGIN_URL, json=login_data)
if response.status_code == 200:
    token = response.json()['access_token']
    print(f"✓ 登录成功，获取到 token")
else:
    print(f"✗ 登录失败: {response.text}")
    exit(1)

# 2. 创建一个小的测试图片（1x1 像素的 PNG）
print("\n2. 创建测试图片...")
# 这是一个 1x1 像素的红色 PNG 图片的 base64 编码
test_image_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
print(f"✓ 测试图片大小: {len(test_image_base64)} 字符")

# 3. 更新游戏信息
print("\n3. 更新游戏封面图片...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
update_data = {
    "cover_image": test_image_base64
}
response = requests.put(UPDATE_GAME_URL, json=update_data, headers=headers)
if response.status_code == 200:
    print(f"✓ 图片上传成功！")
    print(f"响应: {response.json()}")
else:
    print(f"✗ 图片上传失败: {response.status_code}")
    print(f"错误信息: {response.text}")

print("\n测试完成！")
