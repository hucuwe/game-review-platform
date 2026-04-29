from flask import Blueprint, request, jsonify
from app import db
from app.models import Announcement
from datetime import datetime

bp = Blueprint('announcements', __name__, url_prefix='/api/announcements')

@bp.route('', methods=['GET'])
def get_public_announcements():
    """获取公开的公告列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    type_filter = request.args.get('type', '')
    
    query = Announcement.query.filter_by(status='published')
    
    # 类型筛选
    if type_filter:
        query = query.filter_by(type=type_filter)
    
    # 按优先级和发布时间排序
    pagination = query.order_by(
        Announcement.priority.desc(),
        Announcement.publish_time.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'announcements': [a.to_dict() for a in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    }), 200

@bp.route('/latest', methods=['GET'])
def get_latest_announcement():
    """获取最新的一条公告（用于首页跑马灯）"""
    announcement = Announcement.query.filter_by(status='published')\
        .order_by(Announcement.priority.desc(), Announcement.publish_time.desc())\
        .first()
    
    if not announcement:
        return jsonify({'announcement': None}), 200
    
    return jsonify({'announcement': announcement.to_dict()}), 200

@bp.route('/<int:announcement_id>', methods=['GET'])
def get_announcement_detail(announcement_id):
    """获取公告详情"""
    announcement = Announcement.query.get(announcement_id)
    
    if not announcement:
        return jsonify({'message': '公告不存在'}), 404
    
    if announcement.status != 'published':
        return jsonify({'message': '公告未发布'}), 403
    
    return jsonify({'announcement': announcement.to_dict()}), 200
