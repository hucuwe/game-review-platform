"""
测试数据库连接
"""
import pymysql
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'game_review_platform'),
    'charset': 'utf8mb4'
}

print("=" * 60)
print("测试数据库连接")
print("=" * 60)
print()
print("配置信息：")
print(f"  主机: {DB_CONFIG['host']}")
print(f"  端口: {DB_CONFIG['port']}")
print(f"  用户: {DB_CONFIG['user']}")
print(f"  密码: {'*' * len(DB_CONFIG['password']) if DB_CONFIG['password'] else '(空)'}")
print(f"  数据库: {DB_CONFIG['database']}")
print()

try:
    print("正在连接数据库...")
    connection = pymysql.connect(**DB_CONFIG)
    print("✅ 数据库连接成功！")
    
    cursor = connection.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"✅ MySQL 版本: {version[0]}")
    
    cursor.execute("SELECT DATABASE()")
    db = cursor.fetchone()
    print(f"✅ 当前数据库: {db[0]}")
    
    cursor.close()
    connection.close()
    
    print()
    print("=" * 60)
    print("数据库连接测试通过！现在可以启动 Flask 服务了。")
    print("=" * 60)
    
except pymysql.err.OperationalError as e:
    print(f"❌ 数据库连接失败: {e}")
    print()
    print("可能的原因：")
    print("1. MySQL 服务未启动")
    print("2. 数据库密码错误")
    print("3. 数据库不存在")
    print("4. 用户权限不足")
    print()
    print("解决方案：")
    print("1. 检查 MySQL 服务是否运行")
    print("2. 确认 .env 文件中的 DB_PASSWORD 是否正确")
    print("3. 确认已执行 database/init.sql 创建数据库")
    print("4. 尝试使用 MySQL 命令行登录测试")
    
except Exception as e:
    print(f"❌ 发生错误: {e}")
