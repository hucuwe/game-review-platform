"""
推荐系统API路由
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.services.recommendation import RecommendationService

bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')


@bp.route('/personalized', methods=['GET'])
def get_personalized_recommendations():
    """
    获取个性化推荐
    
    支持登录和未登录用户：
    - 登录用户：基于协同过滤推荐
    - 未登录用户：基于冷启动策略推荐
    
    Query参数：
    - limit: 推荐数量，默认8
    """
    limit = request.args.get('limit', 8, type=int)
    
    # 尝试获取用户ID（如果已登录）
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user_id = int(identity)
    except:
        pass
    
    # 获取推荐游戏
    games = RecommendationService.get_recommended_games(user_id, limit)
    
    # 返回游戏信息
    return jsonify({
        'games': [game.to_dict(include_stats=True) for game in games],
        'algorithm': 'collaborative_filtering' if user_id and len(games) > 0 else 'cold_start',
        'user_id': user_id
    }), 200


@bp.route('/similar-users', methods=['GET'])
@jwt_required()
def get_similar_users():
    """
    获取相似用户列表（需要登录）
    
    Query参数：
    - limit: 返回数量，默认10
    """
    user_id = int(get_jwt_identity())
    limit = request.args.get('limit', 10, type=int)
    
    similar_users = RecommendationService.find_similar_users(user_id, limit)
    
    return jsonify({
        'similar_users': [
            {'user_id': uid, 'similarity': round(sim, 4)}
            for uid, sim in similar_users
        ]
    }), 200


@bp.route('/cold-start', methods=['GET'])
def get_cold_start_recommendations():
    """
    获取冷启动推荐（公开接口）
    
    Query参数：
    - limit: 推荐数量，默认8
    """
    limit = request.args.get('limit', 8, type=int)
    
    game_ids = RecommendationService.cold_start_recommend(limit)
    
    from app.models import Game
    games = Game.query.filter(Game.id.in_(game_ids)).all()
    
    # 按推荐顺序排序
    game_dict = {g.id: g for g in games}
    ordered_games = [game_dict[gid] for gid in game_ids if gid in game_dict]
    
    return jsonify({
        'games': [game.to_dict(include_stats=True) for game in ordered_games],
        'algorithm': 'cold_start'
    }), 200
