from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import GameRating, Game

bp = Blueprint('ratings', __name__, url_prefix='/api/ratings')

@bp.route('', methods=['GET'])
def get_ratings():
    game_id = request.args.get('game_id', type=int)
    
    if not game_id:
        return jsonify({'message': '缺少游戏ID'}), 400
    
    ratings = GameRating.query.filter_by(game_id=game_id).all()
    
    # 计算平均分
    stats = {
        'gameplay_avg': 0,
        'graphics_avg': 0,
        'story_avg': 0,
        'sound_avg': 0,
        'overall_avg': 0,
        'count': len(ratings)
    }
    
    if ratings:
        stats['gameplay_avg'] = round(sum(float(r.gameplay_score) for r in ratings) / len(ratings), 1)
        stats['graphics_avg'] = round(sum(float(r.graphics_score) for r in ratings) / len(ratings), 1)
        stats['story_avg'] = round(sum(float(r.story_score) for r in ratings) / len(ratings), 1)
        stats['sound_avg'] = round(sum(float(r.sound_score) for r in ratings) / len(ratings), 1)
        stats['overall_avg'] = round(sum(float(r.overall_score) for r in ratings) / len(ratings), 1)
    
    return jsonify({
        'ratings': [r.to_dict() for r in ratings],
        'stats': stats
    }), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_rating():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    game_id = data.get('game_id')
    
    if not game_id:
        return jsonify({'message': '缺少游戏ID'}), 400
    
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'message': '游戏不存在'}), 404
    
    # 检查是否已评分
    existing = GameRating.query.filter_by(game_id=game_id, user_id=user_id).first()
    
    if existing:
        # 更新评分
        existing.gameplay_score = data.get('gameplay_score', existing.gameplay_score)
        existing.graphics_score = data.get('graphics_score', existing.graphics_score)
        existing.story_score = data.get('story_score', existing.story_score)
        existing.sound_score = data.get('sound_score', existing.sound_score)
        existing.overall_score = data.get('overall_score', existing.overall_score)
        db.session.commit()
        return jsonify({'message': '评分已更新', 'rating': existing.to_dict()}), 200
    else:
        # 创建新评分
        rating = GameRating(
            game_id=game_id,
            user_id=user_id,
            gameplay_score=data.get('gameplay_score', 0),
            graphics_score=data.get('graphics_score', 0),
            story_score=data.get('story_score', 0),
            sound_score=data.get('sound_score', 0),
            overall_score=data.get('overall_score', 0)
        )
        
        db.session.add(rating)
        db.session.commit()
        
        return jsonify({'message': '评分成功', 'rating': rating.to_dict()}), 201

@bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_rating():
    user_id = int(get_jwt_identity())
    game_id = request.args.get('game_id', type=int)
    
    if not game_id:
        return jsonify({'message': '缺少游戏ID'}), 400
    
    rating = GameRating.query.filter_by(game_id=game_id, user_id=user_id).first()
    
    if not rating:
        return jsonify({'rating': None}), 200
    
    return jsonify({'rating': rating.to_dict()}), 200

@bp.route('/my/all', methods=['GET'])
@jwt_required()
def get_my_all_ratings():
    user_id = int(get_jwt_identity())
    
    # 获取用户的所有评分，并关联游戏信息
    ratings = GameRating.query.filter_by(user_id=user_id).order_by(GameRating.created_at.desc()).all()
    
    result = []
    for rating in ratings:
        rating_dict = rating.to_dict()
        # 添加游戏信息
        game = Game.query.get(rating.game_id)
        if game:
            rating_dict['game'] = game.to_dict()
        result.append(rating_dict)
    
    return jsonify({'ratings': result, 'total': len(result)}), 200
