# 删除操作修复 - 更新日志

## 更新时间
2026-01-21

## 问题描述

后台管理删除用户时出现错误：
```
sqlalchemy.exc.DataError: (pymysql.err.DataError) (1265, "Data truncated for column 'status' at row 1")
```

**原因**: 代码尝试将用户 status 设置为 'deleted'，但数据库字段只允许 'active' 和 'banned' 两个值。

## 解决方案

将用户删除从**软删除**改为**物理删除**，与其他管理模块保持一致。

## 主要变更

### 1. 修改用户删除逻辑

**文件**: `backend/app/routes/admin.py`

**修改前**:
```python
# 软删除：修改状态为deleted
user.status = 'deleted'
db.session.commit()
```

**修改后**:
```python
# 物理删除：直接从数据库删除
# 注意：由于外键约束设置了 CASCADE，相关的评论、评分等数据也会被删除
db.session.delete(user)
db.session.commit()
```

### 2. 数据库清理

清理了已有的 status='deleted' 的用户记录：
```sql
DELETE FROM users WHERE status='deleted';
```

### 3. 保持数据库结构不变

users 表的 status 字段保持为：
```sql
ENUM('active', 'banned') DEFAULT 'active'
```

## 删除策略总结

| 模块 | 删除方式 | 说明 |
|------|---------|------|
| 用户管理 | 物理删除 | 删除用户及其所有相关数据 |
| 游戏管理 | 物理删除 | 删除游戏及其所有相关数据 |
| 评论管理 | 软删除 | 设置 status='deleted'，保留数据 |
| 举报管理 | 物理删除 | 直接删除举报记录 |
| 分类管理 | 物理删除 | 需先确保无游戏使用 |
| 轮播图管理 | 物理删除 | 直接删除 |
| 公告管理 | 物理删除 | 直接删除 |

## 级联删除说明

### 删除用户时会级联删除：
- 用户的所有评分 (game_ratings)
- 用户的所有评论 (comments)
- 用户的所有点赞 (comment_likes)
- 用户的所有举报 (reports)

### 删除游戏时会级联删除：
- 游戏的所有评分 (game_ratings)
- 游戏的所有评论 (comments)

### 删除评论时会级联删除：
- 评论的所有点赞 (comment_likes)
- 评论的所有举报 (reports)
- 评论的所有回复（子评论）

## 安全措施

1. **权限控制**: 只有管理员可以删除用户
2. **管理员保护**: 不能删除管理员账号
3. **前端确认**: 删除前需要用户确认
4. **提示信息**: 明确告知删除的影响范围

## 前端建议

### 删除确认提示

**用户删除**:
```javascript
ElMessageBox.confirm(
  '确定要删除该用户吗？删除后该用户的所有评论、评分等数据也会被删除，且无法恢复！',
  '警告',
  {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning',
    confirmButtonClass: 'el-button--danger'
  }
)
```

**游戏删除**:
```javascript
ElMessageBox.confirm(
  '确定要删除该游戏吗？删除后该游戏的所有评论、评分等数据也会被删除，且无法恢复！',
  '警告',
  {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning',
    confirmButtonClass: 'el-button--danger'
  }
)
```

## 测试验证

### 测试步骤
1. 登录管理后台
2. 进入用户管理
3. 选择一个普通用户
4. 点击删除按钮
5. 确认删除
6. 验证用户及其相关数据是否被删除

### 预期结果
- 用户记录被删除
- 用户的评论被删除
- 用户的评分被删除
- 用户的点赞被删除
- 用户的举报被删除
- 不能删除管理员账号

## 注意事项

1. **数据备份**: 删除操作不可逆，建议定期备份数据库
2. **谨慎操作**: 删除用户会影响大量关联数据
3. **日志记录**: 建议记录删除操作日志用于审计
4. **用户通知**: 可考虑在删除前通知用户

## 相关文档

- [删除操作说明文档](./delete_operations_guide.md)
- [数据库设计文档](./database_design.md)
