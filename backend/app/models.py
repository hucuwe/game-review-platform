from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.Enum('user', 'admin'), default='user')
    avatar = db.Column(db.Text)  # 支持 Base64 编码的图片
    status = db.Column(db.Enum('active', 'banned'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'avatar': self.avatar,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class GameCategory(db.Model):
    __tablename__ = 'game_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('game_categories.id'))
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255))  # 存储文件路径
    images = db.Column(db.JSON)
    release_date = db.Column(db.Date)
    developer = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    status = db.Column(db.Enum('published', 'draft'), default='published')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = db.relationship('GameCategory', backref='games')
    
    def to_dict(self, include_stats=False):
        data = {
            'id': self.id,
            'title': self.title,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'description': self.description,
            'cover_image': self.cover_image,
            'images': self.images if self.images else [],
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'developer': self.developer,
            'publisher': self.publisher,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_stats:
            ratings = GameRating.query.filter_by(game_id=self.id).all()
            if ratings:
                data['avg_score'] = round(sum(r.overall_score for r in ratings) / len(ratings), 1)
                data['rating_count'] = len(ratings)
            else:
                data['avg_score'] = 0
                data['rating_count'] = 0
        return data

class GameRating(db.Model):
    __tablename__ = 'game_ratings'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    gameplay_score = db.Column(db.Numeric(3, 1))
    graphics_score = db.Column(db.Numeric(3, 1))
    story_score = db.Column(db.Numeric(3, 1))
    sound_score = db.Column(db.Numeric(3, 1))
    overall_score = db.Column(db.Numeric(3, 1))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='ratings')
    game = db.relationship('Game', backref='ratings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'gameplay_score': float(self.gameplay_score) if self.gameplay_score else 0,
            'graphics_score': float(self.graphics_score) if self.graphics_score else 0,
            'story_score': float(self.story_score) if self.story_score else 0,
            'sound_score': float(self.sound_score) if self.sound_score else 0,
            'overall_score': float(self.overall_score) if self.overall_score else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    content = db.Column(db.Text, nullable=False)
    likes_count = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('normal', 'reported', 'deleted'), default='normal')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='comments')
    game = db.relationship('Game', backref='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self, include_replies=False):
        data = {
            'id': self.id,
            'game_id': self.game_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'avatar': self.user.avatar if self.user else None,
            'parent_id': self.parent_id,
            'content': self.content,
            'likes_count': self.likes_count,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_replies:
            data['replies'] = [r.to_dict() for r in self.replies if r.status == 'normal']
        return data

class CommentLike(db.Model):
    __tablename__ = 'comment_likes'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('pending', 'processed', 'rejected'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    comment = db.relationship('Comment', backref='reports')
    user = db.relationship('User', backref='reports')
    
    def to_dict(self):
        return {
            'id': self.id,
            'comment_id': self.comment_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }


class Banner(db.Model):
    __tablename__ = 'banners'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    link_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('active', 'inactive'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'image_url': self.image_url,
            'link_url': self.link_url,
            'description': self.description,
            'sort_order': self.sort_order,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum('system', 'event', 'maintenance', 'update'), default='system')
    priority = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('draft', 'published', 'archived'), default='draft')
    publish_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'priority': self.priority,
            'status': self.status,
            'publish_time': self.publish_time.isoformat() if self.publish_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

