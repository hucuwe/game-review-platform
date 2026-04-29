from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

bp = Blueprint('upload', __name__, url_prefix='/api/upload')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/image', methods=['POST'])
@jwt_required()
def upload_image():
    """上传单张图片"""
    if 'file' not in request.files:
        return jsonify({'message': '没有文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'message': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'message': '不支持的文件类型'}), 400
    
    try:
        # 生成唯一文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # 按日期创建子目录
        date_dir = datetime.now().strftime('%Y%m%d')
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], date_dir)
        
        # 确保目录存在
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # 返回访问URL
        file_url = f"/uploads/{date_dir}/{filename}"
        
        return jsonify({
            'message': '上传成功',
            'url': file_url
        }), 200
        
    except Exception as e:
        print(f"上传失败: {str(e)}")
        return jsonify({'message': '上传失败'}), 500

@bp.route('/images', methods=['POST'])
@jwt_required()
def upload_images():
    """批量上传图片"""
    if 'files' not in request.files:
        return jsonify({'message': '没有文件'}), 400
    
    files = request.files.getlist('files')
    
    if not files or len(files) == 0:
        return jsonify({'message': '没有选择文件'}), 400
    
    uploaded_urls = []
    
    try:
        # 按日期创建子目录
        date_dir = datetime.now().strftime('%Y%m%d')
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], date_dir)
        
        # 确保目录存在
        os.makedirs(upload_dir, exist_ok=True)
        
        for file in files:
            if file and allowed_file(file.filename):
                # 生成唯一文件名
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                
                # 保存文件
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                
                # 添加到结果列表
                file_url = f"/uploads/{date_dir}/{filename}"
                uploaded_urls.append(file_url)
        
        return jsonify({
            'message': '上传成功',
            'urls': uploaded_urls
        }), 200
        
    except Exception as e:
        print(f"批量上传失败: {str(e)}")
        return jsonify({'message': '批量上传失败'}), 500
