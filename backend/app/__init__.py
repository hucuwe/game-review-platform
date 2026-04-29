from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # JWT 错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token 已过期'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': f'Token 无效: {str(error)}'}), 422
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({'message': f'缺少 Token: {str(error)}'}), 401
    
    @jwt.token_verification_failed_loader
    def token_verification_failed_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token 验证失败'}), 422
    
    # 注册蓝图
    from app.routes import auth, users, games, comments, ratings, admin, announcements, recommendations, upload
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(games.bp)
    app.register_blueprint(comments.bp)
    app.register_blueprint(ratings.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(announcements.bp)
    app.register_blueprint(recommendations.bp)
    app.register_blueprint(upload.bp)
    
    return app
