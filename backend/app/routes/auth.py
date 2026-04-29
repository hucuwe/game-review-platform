from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not all([username, password, email]):
        return jsonify({'message': '缺少必要字段'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'message': '邮箱已被注册'}), 400
    
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': '注册成功', 'user': user.to_dict()}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # 详细调试日志
    print(f"[登录请求] 原始数据: {data}")
    print(f"[登录请求] 用户名: '{username}' (长度: {len(username) if username else 0})")
    print(f"[登录请求] 密码: '{password}' (长度: {len(password) if password else 0})")
    print(f"[登录请求] 用户名字节: {username.encode('utf-8') if username else None}")
    
    if not all([username, password]):
        print(f"[登录失败] 缺少必要字段")
        return jsonify({'message': '缺少用户名或密码'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        print(f"[登录失败] 用户不存在: {username}")
        return jsonify({'message': '用户名或密码错误'}), 401
    
    print(f"[登录请求] 找到用户: ID={user.id}, 用户名='{user.username}'")
    password_match = user.check_password(password)
    print(f"[登录请求] 密码验证结果: {password_match}")
    
    if not password_match:
        print(f"[登录失败] 密码错误，用户: {username}")
        return jsonify({'message': '用户名或密码错误'}), 401
    
    if user.status == 'banned':
        print(f"[登录失败] 账号已被封禁: {username}")
        return jsonify({'message': '账号已被封禁'}), 403
    
    access_token = create_access_token(identity=str(user.id))
    
    print(f"[登录成功] 用户: {username}, ID: {user.id}")
    
    return jsonify({
        'message': '登录成功',
        'token': access_token,
        'user': user.to_dict()
    }), 200

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    return jsonify({'user': user.to_dict()}), 200
