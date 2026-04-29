"""
测试文件上传功能
"""
import requests
import io
from PIL import Image

# 测试配置
BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
UPLOAD_URL = f"{BASE_URL}/api/upload/image"

# 1. 登录获取 token
print("1. 登录管理员账号...")
login_data = {
    "username": "admin",
    "password": "admin123"
}
response = requests.post(LOGIN_URL, json=login_data)
if response.status_code == 200:
    token = response.json()['access_token']
    print(f"✓ 登录成功")
else:
    print(f"✗ 登录失败: {response.text}")
    exit(1)

# 2. 创建测试图片
print("\n2. 创建测试图片...")
img = Image.new('RGB', (100, 100), color='red')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)
print(f"✓ 创建了一个 100x100 的红色图片")

# 3. 上传图片
print("\n3. 上传图片...")
headers = {
    "Authorization": f"Bearer {token}"
}
files = {
    'file': ('test.png', img_bytes, 'image/png')
}
response = requests.post(UPLOAD_URL, files=files, headers=headers)
if response.status_code == 200:
    result = response.json()
    print(f"✓ 图片上传成功！")
    print(f"  文件URL: {result['url']}")
    print(f"  完整访问地址: {BASE_URL}{result['url']}")
else:
    print(f"✗ 图片上传失败: {response.status_code}")
    print(f"  错误信息: {response.text}")

print("\n测试完成！")
