"""
快速设置数据库中测试用户的密码
运行此脚本前请确保：
1. 已经执行了 database/init.sql 初始化脚本
2. 已经配置好 .env 文件中的数据库连接信息
"""

import pymysql
from werkzeug.security import generate_password_hash
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

def setup_passwords():
    """设置所有测试用户的密码"""
    try:
        # 连接数据库
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 生成密码哈希
        admin_password = generate_password_hash('admin123')
        user_password = generate_password_hash('password123')
        
        print("正在设置密码...")
        
        # 更新管理员密码
        cursor.execute(
            "UPDATE users SET password = %s WHERE username = 'admin'",
            (admin_password,)
        )
        print("✓ 管理员密码已设置（admin / admin123）")
        
        # 更新所有普通用户密码
        cursor.execute(
            "UPDATE users SET password = %s WHERE role = 'user'",
            (user_password,)
        )
        affected_rows = cursor.rowcount
        print(f"✓ {affected_rows} 个普通用户密码已设置（密码：password123）")
        
        # 提交更改
        connection.commit()
        
        print("\n密码设置完成！")
        print("\n可用的测试账号：")
        print("=" * 50)
        print("管理员账号：")
        print("  用户名: admin")
        print("  密码: admin123")
        print("\n普通用户账号（密码统一为 password123）：")
        
        # 查询所有普通用户
        cursor.execute("SELECT username, email, status FROM users WHERE role = 'user' ORDER BY id")
        users = cursor.fetchall()
        
        for username, email, status in users:
            status_text = "正常" if status == "active" else "已封禁"
            print(f"  {username:12} ({email:30}) - {status_text}")
        
        print("=" * 50)
        
        # 关闭连接
        cursor.close()
        connection.close()
        
    except pymysql.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("=" * 50)
    print("游戏评论平台 - 密码设置工具")
    print("=" * 50)
    print()
    
    # 检查数据库连接
    try:
        connection = pymysql.connect(**DB_CONFIG)
        connection.close()
        print("✓ 数据库连接成功")
        print()
    except Exception as e:
        print(f"❌ 无法连接到数据库: {e}")
        print("\n请检查：")
        print("1. MySQL 服务是否已启动")
        print("2. .env 文件中的数据库配置是否正确")
        print("3. 数据库是否已创建（运行 database/init.sql）")
        exit(1)
    
    # 设置密码
    if setup_passwords():
        print("\n现在可以使用这些账号登录系统了！")
    else:
        print("\n密码设置失败，请检查错误信息。")
