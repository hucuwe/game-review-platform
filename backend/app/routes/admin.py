from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Comment, Report, Game, GameRating, GameCategory, Banner, Announcement, CommentLike
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required():
    """验证管理员权限"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return None
    return user

# ==================== 统计数据 ====================

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """获取后台统计数据"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    # 基础统计
    total_users = User.query.count()
    total_games = Game.query.count()
    total_comments = Comment.query.filter(Comment.status.in_(['normal', 'reported'])).count()
    total_ratings = GameRating.query.count()
    pending_reports = Report.query.filter_by(status='pending').count()
    
    # 今日新增
    today = datetime.utcnow().date()
    today_users = User.query.filter(func.date(User.created_at) == today).count()
    today_comments = Comment.query.filter(func.date(Comment.created_at) == today).count()
    today_ratings = GameRating.query.filter(func.date(GameRating.created_at) == today).count()
    
    # 用户状态统计
    active_users = User.query.filter_by(status='active').count()
    banned_users = User.query.filter_by(status='banned').count()
    
    # 游戏状态统计
    published_games = Game.query.filter_by(status='published').count()
    draft_games = Game.query.filter_by(status='draft').count()
    
    # 评论状态统计
    normal_comments = Comment.query.filter_by(status='normal').count()
    reported_comments = Comment.query.filter_by(status='reported').count()
    deleted_comments = Comment.query.filter_by(status='deleted').count()
    
    stats = {
        'total_users': total_users,
        'total_games': total_games,
        'total_comments': total_comments,
        'total_ratings': total_ratings,
        'pending_reports': pending_reports,
        'today_users': today_users,
        'today_comments': today_comments,
        'today_ratings': today_ratings,
        'active_users': active_users,
        'banned_users': banned_users,
        'published_games': published_games,
        'draft_games': draft_games,
        'normal_comments': normal_comments,
        'reported_comments': reported_comments,
        'deleted_comments': deleted_comments
    }
    
    return jsonify({'stats': stats}), 200

@bp.route('/stats/charts', methods=['GET'])
@jwt_required()
def get_chart_data():
    """获取图表数据"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    # 最近7天的用户注册趋势
    user_trend = []
    for i in range(6, -1, -1):
        date = datetime.utcnow().date() - timedelta(days=i)
        count = User.query.filter(func.date(User.created_at) == date).count()
        user_trend.append({'date': str(date), 'count': count})
    
    # 最近7天的评论趋势
    comment_trend = []
    for i in range(6, -1, -1):
        date = datetime.utcnow().date() - timedelta(days=i)
        count = Comment.query.filter(func.date(Comment.created_at) == date).count()
        comment_trend.append({'date': str(date), 'count': count})
    
    # 分类游戏数量统计
    category_stats = db.session.query(
        GameCategory.name,
        func.count(Game.id).label('count')
    ).join(Game, Game.category_id == GameCategory.id)\
     .filter(Game.status == 'published')\
     .group_by(GameCategory.id, GameCategory.name).all()
    
    category_data = [{'name': name, 'count': count} for name, count in category_stats]
    
    # 评分最高的游戏TOP10
    top_games = db.session.query(
        Game.title,
        func.avg(GameRating.overall_score).label('avg_score')
    ).join(GameRating, GameRating.game_id == Game.id)\
     .group_by(Game.id, Game.title)\
     .order_by(func.avg(GameRating.overall_score).desc())\
     .limit(10).all()
    
    top_games_data = [{'title': title, 'score': float(score)} for title, score in top_games]
    
    return jsonify({
        'user_trend': user_trend,
        'comment_trend': comment_trend,
        'category_data': category_data,
        'top_games': top_games_data
    }), 200

# ==================== 用户管理 ====================

@bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    role = request.args.get('role', '')
    
    query = User.query
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            db.or_(
                User.username.like(f'%{keyword}%'),
                User.email.like(f'%{keyword}%')
            )
        )
    
    # 状态筛选
    if status:
        query = query.filter_by(status=status)
    
    # 角色筛选
    if role:
        query = query.filter_by(role=role)
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [u.to_dict() for u in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    }), 200

@bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_detail(user_id):
    """获取用户详情"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    # 获取用户的统计数据
    rating_count = GameRating.query.filter_by(user_id=user_id).count()
    comment_count = Comment.query.filter_by(user_id=user_id)\
        .filter(Comment.status.in_(['normal', 'reported'])).count()
    
    user_data = user.to_dict()
    user_data['rating_count'] = rating_count
    user_data['comment_count'] = comment_count
    
    return jsonify({'user': user_data}), 200

@bp.route('/users/<int:user_id>/ban', methods=['POST'])
@jwt_required()
def ban_user(user_id):
    """封禁用户"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    if user.role == 'admin':
        return jsonify({'message': '不能封禁管理员'}), 400
    
    user.status = 'banned'
    db.session.commit()
    
    return jsonify({'message': '封禁成功'}), 200

@bp.route('/users/<int:user_id>/unban', methods=['POST'])
@jwt_required()
def unban_user(user_id):
    """解封用户"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    user.status = 'active'
    db.session.commit()
    
    return jsonify({'message': '解封成功'}), 200

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除用户（物理删除）"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    if user.role == 'admin':
        return jsonify({'message': '不能删除管理员'}), 400
    
    try:
        # 临时禁用外键检查，避免删除时的外键约束问题
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 0'))
        
        # 删除用户（数据库会自动级联删除相关数据）
        db.session.delete(user)
        db.session.commit()
        
        # 重新启用外键检查
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        # 确保重新启用外键检查
        try:
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
            db.session.commit()
        except:
            pass
        return jsonify({'message': '删除失败，请稍后重试'}), 500
    
    return jsonify({'message': '删除成功'}), 200

@bp.route('/users/create-admin', methods=['POST'])
@jwt_required()
def create_admin():
    """创建管理员账号"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'message': '缺少必要字段'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=email).first():
        return jsonify({'message': '邮箱已被注册'}), 400
    
    # 创建管理员用户
    admin_user = User(
        username=username,
        email=email,
        role='admin',
        status='active'
    )
    admin_user.set_password(password)
    
    db.session.add(admin_user)
    db.session.commit()
    
    return jsonify({
        'message': '管理员创建成功',
        'user': admin_user.to_dict()
    }), 201

# ==================== 评论管理 ====================

@bp.route('/comments', methods=['GET'])
@jwt_required()
def get_all_comments():
    """获取评论列表"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    keyword = request.args.get('keyword', '')
    
    query = Comment.query
    
    # 状态筛选
    if status:
        query = query.filter_by(status=status)
    
    # 关键词搜索
    if keyword:
        query = query.filter(Comment.content.like(f'%{keyword}%'))
    
    pagination = query.order_by(Comment.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 添加用户名和游戏标题
    comments_data = []
    for comment in pagination.items:
        comment_dict = comment.to_dict()
        user = User.query.get(comment.user_id)
        game = Game.query.get(comment.game_id)
        comment_dict['username'] = user.username if user else '未知用户'
        comment_dict['game_title'] = game.title if game else '未知游戏'
        comments_data.append(comment_dict)
    
    return jsonify({
        'comments': comments_data,
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    }), 200

# ==================== 举报管理 ====================

@bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """获取举报列表"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', 'pending')
    
    query = Report.query.filter_by(status=status)
    pagination = query.order_by(Report.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    reports_data = []
    for report in pagination.items:
        report_dict = report.to_dict()
        
        # 添加举报人信息
        user = User.query.get(report.user_id)
        report_dict['username'] = user.username if user else '未知用户'
        
        # 添加评论信息
        if report.comment:
            comment_dict = report.comment.to_dict()
            comment_user = User.query.get(report.comment.user_id)
            comment_dict['username'] = comment_user.username if comment_user else '未知用户'
            report_dict['comment'] = comment_dict
        else:
            report_dict['comment'] = None
        
        reports_data.append(report_dict)
    
    return jsonify({
        'reports': reports_data,
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    }), 200

@bp.route('/reports/<int:report_id>/process', methods=['POST'])
@jwt_required()
def process_report(report_id):
    """处理举报"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    report = Report.query.get(report_id)
    if not report:
        return jsonify({'message': '举报不存在'}), 404
    
    data = request.get_json()
    action = data.get('action')  # 'approve' or 'reject'
    
    if action == 'approve':
        report.status = 'processed'
        if report.comment:
            report.comment.status = 'deleted'
    elif action == 'reject':
        report.status = 'rejected'
        if report.comment and report.comment.status == 'reported':
            report.comment.status = 'normal'
    else:
        return jsonify({'message': '无效的操作'}), 400
    
    report.processed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '处理成功'}), 200

@bp.route('/reports/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """删除举报记录"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    report = Report.query.get(report_id)
    if not report:
        return jsonify({'message': '举报不存在'}), 404
    
    db.session.delete(report)
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200

# ==================== 游戏分类管理 ====================

@bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """获取分类列表"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    categories = GameCategory.query.all()
    
    # 添加每个分类的游戏数量
    result = []
    for category in categories:
        cat_dict = category.to_dict()
        cat_dict['game_count'] = Game.query.filter_by(category_id=category.id).count()
        result.append(cat_dict)
    
    return jsonify({'categories': result}), 200

@bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    """创建分类"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    data = request.get_json()
    
    category = GameCategory(
        name=data.get('name'),
        description=data.get('description', '')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({'message': '创建成功', 'category': category.to_dict()}), 201

@bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """更新分类"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    category = GameCategory.query.get(category_id)
    if not category:
        return jsonify({'message': '分类不存在'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    
    db.session.commit()
    
    return jsonify({'message': '更新成功', 'category': category.to_dict()}), 200

@bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """删除分类"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    category = GameCategory.query.get(category_id)
    if not category:
        return jsonify({'message': '分类不存在'}), 404
    
    # 检查是否有游戏使用该分类
    game_count = Game.query.filter_by(category_id=category_id).count()
    if game_count > 0:
        return jsonify({'message': f'该分类下还有{game_count}款游戏，无法删除'}), 400
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200


# ==================== 轮播图管理 ====================

@bp.route('/banners', methods=['GET'])
@jwt_required()
def get_banners():
    """获取轮播图列表"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    banners = Banner.query.order_by(Banner.sort_order.asc(), Banner.created_at.desc()).all()
    return jsonify({'banners': [b.to_dict() for b in banners]}), 200

@bp.route('/banners', methods=['POST'])
@jwt_required()
def create_banner():
    """创建轮播图"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    data = request.get_json()
    
    banner = Banner(
        title=data.get('title'),
        image_url=data.get('image_url'),
        link_url=data.get('link_url', ''),
        description=data.get('description', ''),
        sort_order=data.get('sort_order', 0),
        status=data.get('status', 'active')
    )
    
    db.session.add(banner)
    db.session.commit()
    
    return jsonify({'message': '创建成功', 'banner': banner.to_dict()}), 201

@bp.route('/banners/<int:banner_id>', methods=['PUT'])
@jwt_required()
def update_banner(banner_id):
    """更新轮播图"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    banner = Banner.query.get(banner_id)
    if not banner:
        return jsonify({'message': '轮播图不存在'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        banner.title = data['title']
    if 'image_url' in data:
        banner.image_url = data['image_url']
    if 'link_url' in data:
        banner.link_url = data['link_url']
    if 'description' in data:
        banner.description = data['description']
    if 'sort_order' in data:
        banner.sort_order = data['sort_order']
    if 'status' in data:
        banner.status = data['status']
    
    banner.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '更新成功', 'banner': banner.to_dict()}), 200

@bp.route('/banners/<int:banner_id>', methods=['DELETE'])
@jwt_required()
def delete_banner(banner_id):
    """删除轮播图"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    banner = Banner.query.get(banner_id)
    if not banner:
        return jsonify({'message': '轮播图不存在'}), 404
    
    db.session.delete(banner)
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200


# ==================== 公告管理 ====================

@bp.route('/announcements', methods=['GET'])
@jwt_required()
def get_announcements():
    """获取公告列表"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', '')
    keyword = request.args.get('keyword', '')
    
    query = Announcement.query
    
    # 状态筛选
    if status:
        query = query.filter_by(status=status)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            db.or_(
                Announcement.title.like(f'%{keyword}%'),
                Announcement.content.like(f'%{keyword}%')
            )
        )
    
    pagination = query.order_by(Announcement.priority.desc(), Announcement.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'announcements': [a.to_dict() for a in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    }), 200

@bp.route('/announcements', methods=['POST'])
@jwt_required()
def create_announcement():
    """创建公告"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    data = request.get_json()
    
    announcement = Announcement(
        title=data.get('title'),
        content=data.get('content'),
        type=data.get('type', 'system'),
        priority=data.get('priority', 0),
        status=data.get('status', 'draft'),
        publish_time=datetime.fromisoformat(data.get('publish_time')) if data.get('publish_time') else None
    )
    
    db.session.add(announcement)
    db.session.commit()
    
    return jsonify({'message': '创建成功', 'announcement': announcement.to_dict()}), 201

@bp.route('/announcements/<int:announcement_id>', methods=['GET'])
@jwt_required()
def get_announcement_detail(announcement_id):
    """获取公告详情"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return jsonify({'message': '公告不存在'}), 404
    
    return jsonify({'announcement': announcement.to_dict()}), 200

@bp.route('/announcements/<int:announcement_id>', methods=['PUT'])
@jwt_required()
def update_announcement(announcement_id):
    """更新公告"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return jsonify({'message': '公告不存在'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        announcement.title = data['title']
    if 'content' in data:
        announcement.content = data['content']
    if 'type' in data:
        announcement.type = data['type']
    if 'priority' in data:
        announcement.priority = data['priority']
    if 'status' in data:
        announcement.status = data['status']
    if 'publish_time' in data:
        announcement.publish_time = datetime.fromisoformat(data['publish_time']) if data['publish_time'] else None
    
    announcement.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '更新成功', 'announcement': announcement.to_dict()}), 200

@bp.route('/announcements/<int:announcement_id>', methods=['DELETE'])
@jwt_required()
def delete_announcement(announcement_id):
    """删除公告"""
    if not admin_required():
        return jsonify({'message': '权限不足'}), 403
    
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return jsonify({'message': '公告不存在'}), 404
    
    db.session.delete(announcement)
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200

