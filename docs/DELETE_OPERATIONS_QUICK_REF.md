# 删除操作快速参考

## 🔴 物理删除（不可恢复）

### 用户
```
DELETE /api/admin/users/<user_id>
- 删除用户本身
- 级联删除：评论、评分、点赞、举报
- 限制：不能删除管理员
```

### 游戏
```
DELETE /api/games/<game_id>
- 删除游戏本身
- 级联删除：评论、评分
- 限制：仅管理员可删除
```

### 举报
```
DELETE /api/admin/reports/<report_id>
- 删除举报记录
- 无级联影响
```

### 分类
```
DELETE /api/admin/categories/<category_id>
- 删除分类
- 限制：分类下不能有游戏
```

### 轮播图
```
DELETE /api/admin/banners/<banner_id>
- 删除轮播图
- 无级联影响
```

### 公告
```
DELETE /api/admin/announcements/<announcement_id>
- 删除公告
- 无级联影响
```

## 🟡 软删除（可恢复）

### 评论
```
DELETE /api/comments/<comment_id>
- 设置 status='deleted'
- 数据保留在数据库
- 前端不显示
- 可通过修改 status 恢复
```

## ⚠️ 重要提示

1. **物理删除不可恢复** - 请谨慎操作
2. **级联删除** - 注意关联数据会被一起删除
3. **权限控制** - 确保只有管理员可以删除
4. **前端确认** - 所有删除操作都应该有确认提示
5. **数据备份** - 定期备份数据库

## 📋 前端确认模板

```javascript
// 用户/游戏删除（有级联）
ElMessageBox.confirm(
  '确定要删除吗？删除后相关的所有数据也会被删除，且无法恢复！',
  '警告',
  {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning',
    confirmButtonClass: 'el-button--danger'
  }
)

// 其他删除（无级联）
ElMessageBox.confirm(
  '确定要删除吗？删除后无法恢复！',
  '提示',
  {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }
)
```
