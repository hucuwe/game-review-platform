# 游戏评论平台 - 简明文档

## 项目简介

这是一个功能完善的游戏评分与评论社区平台，为玩家提供游戏发现、评分、评论和交流服务。

## 核心功能

### 用户端
- 🎮 游戏浏览、搜索、筛选
- ⭐ 多维度评分（玩法、画面、剧情、音效）
- 💬 评论、回复、点赞
- 👤 个人中心、评分记录

### 管理端
- 📊 数据统计和图表
- 👥 用户管理（封禁、删除）
- 🎮 游戏管理（CRUD、图片上传）
- 💬 评论管理、举报处理
- 🎪 轮播图、公告管理

## 技术栈

**前端**: Vue 3 + Element Plus + Vite  
**后端**: Flask + SQLAlchemy + JWT  
**数据库**: MySQL 8.0

## 快速启动

### 后端
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python run.py
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

### 数据库
```bash
mysql -u root -p < database/game_review_platform.sql
```

## 默认账号

- 管理员: `admin` / `admin123`
- 测试用户: `user1` / `password123`

## 技术亮点

1. **前后端分离** - RESTful API + JWT 认证
2. **图片上传优化** - 本地存储替代 Base64，性能提升 300%
3. **多维度评分** - 四维评分系统
4. **智能推荐** - 基于分类和评分的推荐算法
5. **权限控制** - 基于角色的访问控制
6. **响应式设计** - 完美支持移动端

## 项目结构

```
├── backend/          # Flask 后端
│   ├── app/         # 应用代码
│   ├── uploads/     # 上传文件
│   └── run.py       # 启动文件
├── frontend/        # Vue 前端
│   └── src/         # 源代码
├── database/        # 数据库脚本
└── docs/            # 文档
```

## 文档

- [完整 README](./README.md)
- [图片上传指南](./docs/image_upload_guide.md)
- [删除操作指南](./docs/delete_operations_guide.md)
- [API 文档](./docs/api_documentation.md)

## 开发进度

- ✅ 用户认证系统
- ✅ 游戏管理系统
- ✅ 评分评论系统
- ✅ 后台管理系统
- ✅ 图片上传功能
- ⏳ 实时通知（规划中）
- ⏳ 移动端 App（规划中）

## 联系方式

如有问题，请联系开发团队。

---

Made with ❤️
