from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Comment, CommentLike, Report, User

bp = Blueprint('comments', __name__, url_prefix='/api/comments')

@bp.route('', methods=['GET'])
def get_comments():
    game_id = request.args.get('game_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if not game_id:
        return jsonify({'message': '缺少游戏ID'}), 400
    
    query = Comment.query.filter_by(game_id=game_id, parent_id=None, status='normal')
    pagination = query.order_by(Comment.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'comments': [c.to_dict(include_replies=True) for c in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    }), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_comment():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    comment = Comment(
        game_id=data.get('game_id'),
        user_id=user_id,
        parent_id=data.get('parent_id'),
        content=data.get('content')
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({'message': '评论成功', 'comment': comment.to_dict()}), 201

@bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    comment = Comment.query.get(comment_id)
    
    if not comment:
        return jsonify({'message': '评论不存在'}), 404
    
    if comment.user_id != user_id and user.role != 'admin':
        return jsonify({'message': '权限不足'}), 403
    
    comment.status = 'deleted'
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200

@bp.route('/<int:comment_id>/like', methods=['POST'])
@jwt_required()
def like_comment(comment_id):
    user_id = int(get_jwt_identity())
    comment = Comment.query.get(comment_id)
    
    if not comment:
        return jsonify({'message': '评论不存在'}), 404
    
    existing_like = CommentLike.query.filter_by(
        comment_id=comment_id, user_id=user_id
    ).first()
    
    if existing_like:
        db.session.delete(existing_like)
        comment.likes_count = max(0, comment.likes_count - 1)
        message = '取消点赞'
    else:
        like = CommentLike(comment_id=comment_id, user_id=user_id)
        db.session.add(like)
        comment.likes_count += 1
        message = '点赞成功'
    
    db.session.commit()
    
    return jsonify({'message': message, 'likes_count': comment.likes_count}), 200

@bp.route('/<int:comment_id>/report', methods=['POST'])
@jwt_required()
def report_comment(comment_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'message': '评论不存在'}), 404
    
    existing_report = Report.query.filter_by(
        comment_id=comment_id, user_id=user_id
    ).first()
    
    if existing_report:
        return jsonify({'message': '您已举报过该评论'}), 400
    
    report = Report(
        comment_id=comment_id,
        user_id=user_id,
        reason=data.get('reason', '')
    )
    
    # 不直接改变评论状态，仅创建举报记录，等管理员审核处理
    # 检查该评论的举报次数，达到3次才自动隐藏
    report_count = Report.query.filter_by(comment_id=comment_id).count()
    if report_count >= 2:  # 加上本次共3次
        comment.status = 'reported'
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify({'message': '举报成功'}), 201

@bp.route('/my/stats', methods=['GET'])
@jwt_required()
def get_my_comment_stats():
    user_id = int(get_jwt_identity())
    
    # 统计用户的评论数（不包括已删除的）
    total_comments = Comment.query.filter_by(user_id=user_id).filter(
        Comment.status.in_(['normal', 'reported'])
    ).count()
    
    return jsonify({'total': total_comments}), 200

@bp.route('/recent', methods=['GET'])
def get_recent_comments():
    """获取最新评论（跨所有游戏）"""
    limit = request.args.get('limit', 6, type=int)
    
    # 获取最新的评论，包含用户名和游戏标题
    comments = Comment.query.filter_by(status='normal', parent_id=None)\
        .order_by(Comment.created_at.desc())\
        .limit(limit)\
        .all()
    
    result = []
    for comment in comments:
        comment_dict = comment.to_dict()
        # 添加用户名
        user = User.query.get(comment.user_id)
        comment_dict['username'] = user.username if user else '未知用户'
        # 添加游戏标题
        from app.models import Game
        game = Game.query.get(comment.game_id)
        comment_dict['game_title'] = game.title if game else '未知游戏'
        result.append(comment_dict)
    
    return jsonify({'comments': result}), 200
