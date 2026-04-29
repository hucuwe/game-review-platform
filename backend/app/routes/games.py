from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Game, GameCategory, User
from datetime import datetime

bp = Blueprint('games', __name__, url_prefix='/api/games')

@bp.route('', methods=['GET'])
def get_games():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category_ids = request.args.get('categories', '')  # 逗号分隔的分类ID
    keyword = request.args.get('keyword', '')
    min_rating = request.args.get('min_rating', type=float)
    max_rating = request.args.get('max_rating', type=float)
    sort_by = request.args.get('sort_by', 'latest')  # latest, rating, name
    
    query = Game.query.filter_by(status='published')
    
    # 分类筛选（支持多选）
    if category_ids:
        cat_list = [int(x) for x in category_ids.split(',') if x.strip()]
        if cat_list:
            query = query.filter(Game.category_id.in_(cat_list))
    
    # 关键词搜索
    if keyword:
        query = query.filter(Game.title.like(f'%{keyword}%'))
    
    # 评分范围筛选
    if min_rating is not None or max_rating is not None:
        # 需要关联评分表进行筛选
        from app.models import GameRating
        from sqlalchemy import func
        
        # 子查询：计算每个游戏的平均评分
        subquery = db.session.query(
            GameRating.game_id,
            func.avg(GameRating.overall_score).label('avg_score')
        ).group_by(GameRating.game_id).subquery()
        
        query = query.outerjoin(subquery, Game.id == subquery.c.game_id)
        
        if min_rating is not None:
            query = query.filter(
                db.or_(
                    subquery.c.avg_score >= min_rating,
                    subquery.c.avg_score == None  # 包含没有评分的游戏
                )
            )
        if max_rating is not None:
            query = query.filter(
                db.or_(
                    subquery.c.avg_score <= max_rating,
                    subquery.c.avg_score == None
                )
            )
    
    # 排序
    if sort_by == 'latest':
        query = query.order_by(Game.created_at.desc())
    elif sort_by == 'rating':
        # 按评分排序（MySQL兼容）
        from app.models import GameRating
        from sqlalchemy import func, case
        
        subquery = db.session.query(
            GameRating.game_id,
            func.avg(GameRating.overall_score).label('avg_score')
        ).group_by(GameRating.game_id).subquery()
        
        query = query.outerjoin(subquery, Game.id == subquery.c.game_id)
        # MySQL不支持NULLS LAST，使用CASE WHEN将NULL值排到最后
        query = query.order_by(
            case((subquery.c.avg_score == None, 1), else_=0),
            subquery.c.avg_score.desc()
        )
    elif sort_by == 'comments':
        # 按评论数排序
        from app.models import Comment
        from sqlalchemy import func, case
        
        subquery = db.session.query(
            Comment.game_id,
            func.count(Comment.id).label('comment_count')
        ).filter(Comment.status.in_(['normal', 'reported'])).group_by(Comment.game_id).subquery()
        
        query = query.outerjoin(subquery, Game.id == subquery.c.game_id)
        # 将NULL值排到最后
        query = query.order_by(
            case((subquery.c.comment_count == None, 1), else_=0),
            subquery.c.comment_count.desc()
        )
    elif sort_by == 'name':
        query = query.order_by(Game.title.asc())
    
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'games': [game.to_dict(include_stats=True) for game in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    }), 200

@bp.route('/<int:game_id>', methods=['GET'])
def get_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'message': '游戏不存在'}), 404
    return jsonify({'game': game.to_dict(include_stats=True)}), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_game():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'message': '权限不足'}), 403
    
    data = request.get_json()
    
    game = Game(
        title=data.get('title'),
        category_id=data.get('category_id'),
        description=data.get('description'),
        cover_image=data.get('cover_image'),
        images=data.get('images', []),
        developer=data.get('developer'),
        publisher=data.get('publisher'),
        status=data.get('status', 'published')
    )
    
    if data.get('release_date'):
        game.release_date = datetime.strptime(data['release_date'], '%Y-%m-%d').date()
    
    db.session.add(game)
    db.session.commit()
    
    return jsonify({'message': '创建成功', 'game': game.to_dict()}), 201

@bp.route('/<int:game_id>', methods=['PUT'])
@jwt_required()
def update_game(game_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'message': '权限不足'}), 403
    
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'message': '游戏不存在'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        game.title = data['title']
    if 'category_id' in data:
        game.category_id = data['category_id']
    if 'description' in data:
        game.description = data['description']
    if 'cover_image' in data:
        game.cover_image = data['cover_image']
    if 'images' in data:
        game.images = data['images']
    if 'developer' in data:
        game.developer = data['developer']
    if 'publisher' in data:
        game.publisher = data['publisher']
    if 'status' in data:
        game.status = data['status']
    if 'release_date' in data:
        game.release_date = datetime.strptime(data['release_date'], '%Y-%m-%d').date()
    
    db.session.commit()
    
    return jsonify({'message': '更新成功', 'game': game.to_dict()}), 200

@bp.route('/<int:game_id>', methods=['DELETE'])
@jwt_required()
def delete_game(game_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'message': '权限不足'}), 403
    
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'message': '游戏不存在'}), 404
    
    db.session.delete(game)
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200

@bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有分类，包含每个分类的游戏数量"""
    from sqlalchemy import func
    
    # 查询每个分类的游戏数量
    category_counts = db.session.query(
        Game.category_id,
        func.count(Game.id).label('game_count')
    ).filter(Game.status == 'published').group_by(Game.category_id).all()
    
    # 创建分类ID到游戏数量的映射
    count_map = {cat_id: count for cat_id, count in category_counts}
    
    # 获取所有分类
    categories = GameCategory.query.all()
    
    # 为每个分类添加游戏数量
    result = []
    for category in categories:
        cat_dict = category.to_dict()
        cat_dict['game_count'] = count_map.get(category.id, 0)
        result.append(cat_dict)
    
    return jsonify({'categories': result}), 200


# ==================== 轮播图公开API ====================

@bp.route('/banners', methods=['GET'])
def get_public_banners():
    """获取前台轮播图（公开接口）"""
    from app.models import Banner
    
    # 只返回启用状态的轮播图，按排序和创建时间排序
    banners = Banner.query.filter_by(status='active')\
        .order_by(Banner.sort_order.asc(), Banner.created_at.desc())\
        .all()
    
    return jsonify({'banners': [b.to_dict() for b in banners]}), 200
