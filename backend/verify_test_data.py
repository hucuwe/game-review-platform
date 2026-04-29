"""
验证测试数据是否正确导入
"""

import pymysql
from dotenv import load_dotenv
import os
from tabulate import tabulate

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

def verify_data():
    """验证测试数据"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("=" * 70)
        print("游戏评论平台 - 测试数据验证")
        print("=" * 70)
        print()
        
        # 1. 统计总览
        print("📊 数据统计总览")
        print("-" * 70)
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
        stats['普通用户'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        stats['管理员'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM game_categories")
        stats['游戏分类'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM games")
        stats['游戏总数'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM game_ratings")
        stats['评分记录'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM comments WHERE status = 'normal'")
        stats['正常评论'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM comments WHERE status = 'reported'")
        stats['被举报评论'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM comment_likes")
        stats['点赞记录'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM reports WHERE status = 'pending'")
        stats['待处理举报'] = cursor.fetchone()[0]
        
        for key, value in stats.items():
            print(f"  {key:12}: {value:3} 条")
        
        print()
        
        # 2. 热门游戏
        print("🎮 热门游戏 TOP 5")
        print("-" * 70)
        
        cursor.execute("""
            SELECT 
                g.title,
                gc.name,
                COUNT(gr.id) AS rating_count,
                ROUND(AVG(gr.overall_score), 1) AS avg_score
            FROM games g
            LEFT JOIN game_categories gc ON g.category_id = gc.id
            LEFT JOIN game_ratings gr ON g.id = gr.game_id
            GROUP BY g.id
            HAVING COUNT(gr.id) > 0
            ORDER BY AVG(gr.overall_score) DESC, COUNT(gr.id) DESC
            LIMIT 5
        """)
        
        games = cursor.fetchall()
        game_table = []
        for title, category, count, score in games:
            game_table.append([title[:30], category, count, score])
        
        print(tabulate(game_table, 
                      headers=['游戏名称', '分类', '评分数', '平均分'],
                      tablefmt='simple'))
        print()
        
        # 3. 活跃用户
        print("👥 活跃用户 TOP 5")
        print("-" * 70)
        
        cursor.execute("""
            SELECT 
                u.username,
                COUNT(DISTINCT c.id) AS comment_count,
                COUNT(DISTINCT gr.id) AS rating_count
            FROM users u
            LEFT JOIN comments c ON u.id = c.user_id AND c.status = 'normal'
            LEFT JOIN game_ratings gr ON u.id = gr.user_id
            WHERE u.role = 'user'
            GROUP BY u.id
            HAVING (COUNT(DISTINCT c.id) + COUNT(DISTINCT gr.id)) > 0
            ORDER BY (COUNT(DISTINCT c.id) + COUNT(DISTINCT gr.id)) DESC
            LIMIT 5
        """)
        
        users = cursor.fetchall()
        user_table = []
        for username, comments, ratings in users:
            user_table.append([username, comments, ratings, comments + ratings])
        
        print(tabulate(user_table,
                      headers=['用户名', '评论数', '评分数', '总活跃度'],
                      tablefmt='simple'))
        print()
        
        # 4. 分类统计
        print("📁 游戏分类统计")
        print("-" * 70)
        
        cursor.execute("""
            SELECT 
                gc.name,
                COUNT(g.id) AS game_count
            FROM game_categories gc
            LEFT JOIN games g ON gc.id = g.category_id
            GROUP BY gc.id
            ORDER BY COUNT(g.id) DESC
        """)
        
        categories = cursor.fetchall()
        cat_table = []
        for name, count in categories:
            cat_table.append([name, count])
        
        print(tabulate(cat_table,
                      headers=['分类', '游戏数'],
                      tablefmt='simple'))
        print()
        
        # 5. 验证结果
        print("✅ 验证结果")
        print("-" * 70)
        
        issues = []
        
        if stats['普通用户'] < 10:
            issues.append("⚠️  普通用户数量少于预期（应该有14个）")
        
        if stats['管理员'] < 1:
            issues.append("❌ 缺少管理员账号")
        
        if stats['游戏总数'] < 20:
            issues.append("⚠️  游戏数量少于预期（应该有25个）")
        
        if stats['评分记录'] < 20:
            issues.append("⚠️  评分记录少于预期（应该有30+条）")
        
        if stats['正常评论'] < 20:
            issues.append("⚠️  评论数量少于预期（应该有30+条）")
        
        if stats['待处理举报'] < 1:
            issues.append("⚠️  缺少测试举报数据")
        
        if issues:
            print("发现以下问题：")
            for issue in issues:
                print(f"  {issue}")
            print("\n建议：重新运行 database/init.sql 初始化脚本")
        else:
            print("✅ 所有测试数据已正确导入！")
            print("\n下一步：")
            print("  1. 运行 python setup_passwords.py 设置用户密码")
            print("  2. 启动后端服务：python run.py")
            print("  3. 启动前端服务：cd ../frontend && npm run dev")
        
        print()
        print("=" * 70)
        
        cursor.close()
        connection.close()
        
    except pymysql.Error as e:
        print(f"❌ 数据库错误: {e}")
        print("\n请检查：")
        print("1. MySQL 服务是否已启动")
        print("2. .env 文件中的数据库配置是否正确")
        print("3. 数据库是否已创建并导入数据")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == '__main__':
    verify_data()
