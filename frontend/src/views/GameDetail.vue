<template>
  <div class="game-detail-container">
    <div class="game-detail" v-if="game">
      <!-- 游戏基本信息 -->
      <el-card class="game-info-card">
        <el-row :gutter="30">
          <el-col :span="8">
            <img :src="game.cover_image || '/placeholder.jpg'" class="game-cover" />
          </el-col>
          <el-col :span="16">
            <h1 class="game-title">{{ game.title }}</h1>
            <div class="game-meta">
              <p><strong>分类：</strong>{{ game.category_name }}</p>
              <p><strong>开发商：</strong>{{ game.developer }}</p>
              <p><strong>发行商：</strong>{{ game.publisher }}</p>
              <p><strong>发行日期：</strong>{{ game.release_date }}</p>
            </div>
            <div class="game-description">
              <h3>游戏简介</h3>
              <p>{{ game.description }}</p>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 游戏图集 -->
      <el-card class="gallery-card" v-if="game.images && game.images.length > 0">
        <h2 class="section-title">
          <el-icon style="margin-right: 8px"><Picture /></el-icon>
          游戏图集
        </h2>
        <div class="gallery-container">
          <div class="gallery-scroll">
            <div 
              v-for="(image, index) in game.images" 
              :key="index"
              class="gallery-item"
              @click="handleImagePreview(index)"
            >
              <el-image
                :src="image"
                fit="cover"
                class="gallery-image"
                lazy
              >
                <template #placeholder>
                  <div class="image-loading">
                    <el-icon class="is-loading"><Loading /></el-icon>
                  </div>
                </template>
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
              <div class="gallery-overlay">
                <el-icon><ZoomIn /></el-icon>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 图片预览对话框 -->
      <el-dialog
        v-model="showImagePreview"
        width="80%"
        :show-close="true"
        append-to-body
      >
        <div class="preview-container">
          <el-image
            :src="game.images[currentImageIndex]"
            fit="contain"
            style="width: 100%; max-height: 70vh"
          />
          <div class="preview-controls">
            <el-button 
              @click="prevImage" 
              :disabled="currentImageIndex === 0"
              circle
            >
              <el-icon><ArrowLeft /></el-icon>
            </el-button>
            <span class="preview-index">{{ currentImageIndex + 1 }} / {{ game.images.length }}</span>
            <el-button 
              @click="nextImage" 
              :disabled="currentImageIndex === game.images.length - 1"
              circle
            >
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </el-dialog>

      <!-- 游戏评分 -->
      <el-card class="rating-card">
        <h2 class="section-title">游戏评分</h2>
        <div v-if="ratingStats" class="rating-stats">
          <div class="overall-rating">
            <div class="rating-number">{{ ratingStats.overall_avg }}</div>
            <div class="rating-label">综合评分</div>
            <div class="rating-count">{{ ratingStats.count }} 人评分</div>
          </div>
          <div class="rating-details">
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="rating-item">
                  <div class="rating-name">玩法</div>
                  <div class="rating-value">{{ ratingStats.gameplay_avg }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="rating-item">
                  <div class="rating-name">画面</div>
                  <div class="rating-value">{{ ratingStats.graphics_avg }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="rating-item">
                  <div class="rating-name">剧情</div>
                  <div class="rating-value">{{ ratingStats.story_avg }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="rating-item">
                  <div class="rating-name">音效</div>
                  <div class="rating-value">{{ ratingStats.sound_avg }}</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>
        <el-button 
          v-if="userStore.isLoggedIn" 
          @click="showRatingDialog = true" 
          type="primary"
          class="rate-button"
        >
          {{ myRating ? '修改评分' : '我要评分' }}
        </el-button>
        <el-alert 
          v-else 
          title="请先登录后再进行评分" 
          type="info" 
          :closable="false"
          class="login-tip"
        />
      </el-card>

      <!-- 用户评论 -->
      <el-card class="comment-card">
        <h2 class="section-title">用户评论</h2>
        
        <!-- 发表评论 -->
        <div v-if="userStore.isLoggedIn" class="comment-form">
          <el-input
            v-model="commentContent"
            type="textarea"
            placeholder="发表你的评论..."
            :rows="4"
            maxlength="500"
            show-word-limit
          />
          <el-button 
            type="primary" 
            @click="submitComment"
            class="submit-comment-btn"
          >
            发表评论
          </el-button>
        </div>
        <el-alert 
          v-else 
          title="请先登录后再发表评论" 
          type="info" 
          :closable="false"
          class="login-tip"
        />
        
        <!-- 评论列表 -->
        <div class="comments-list">
          <div v-if="comments.length === 0" class="no-comments">
            <el-empty description="暂无评论，快来发表第一条评论吧！" />
          </div>
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-header">
              <div class="comment-user">
                <el-avatar :size="40" class="user-avatar">
                  {{ comment.username.charAt(0) }}
                </el-avatar>
                <div class="user-info">
                  <strong class="username">{{ comment.username }}</strong>
                  <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
                </div>
              </div>
            </div>
            <div class="comment-content">
              {{ comment.content }}
            </div>
            <div class="comment-actions">
              <el-button 
                size="small" 
                @click="likeComment(comment.id)"
                :icon="userStore.isLoggedIn ? 'Like' : ''"
              >
                点赞 ({{ comment.likes_count }})
              </el-button>
              <el-button 
                size="small" 
                @click="replyTo(comment)"
                v-if="userStore.isLoggedIn"
              >
                回复
              </el-button>
              <el-button 
                size="small" 
                @click="reportComment(comment.id)"
                v-if="userStore.isLoggedIn"
              >
                举报
              </el-button>
            </div>
            
            <!-- 回复列表 -->
            <div v-if="comment.replies && comment.replies.length" class="replies">
              <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                <strong class="reply-username">{{ reply.username }}：</strong>
                <span class="reply-content">{{ reply.content }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 评分对话框 -->
      <el-dialog v-model="showRatingDialog" title="游戏评分" width="500px">
        <el-form :model="ratingForm" label-width="80px">
          <el-form-item label="玩法">
            <el-rate v-model="ratingForm.gameplay_score" :max="10" />
            <span class="rate-value">{{ ratingForm.gameplay_score }} 分</span>
          </el-form-item>
          <el-form-item label="画面">
            <el-rate v-model="ratingForm.graphics_score" :max="10" />
            <span class="rate-value">{{ ratingForm.graphics_score }} 分</span>
          </el-form-item>
          <el-form-item label="剧情">
            <el-rate v-model="ratingForm.story_score" :max="10" />
            <span class="rate-value">{{ ratingForm.story_score }} 分</span>
          </el-form-item>
          <el-form-item label="音效">
            <el-rate v-model="ratingForm.sound_score" :max="10" />
            <span class="rate-value">{{ ratingForm.sound_score }} 分</span>
          </el-form-item>
          <el-form-item label="综合">
            <el-rate v-model="ratingForm.overall_score" :max="10" />
            <span class="rate-value">{{ ratingForm.overall_score }} 分</span>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showRatingDialog = false">取消</el-button>
          <el-button type="primary" @click="submitRating">提交</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const userStore = useUserStore()

const game = ref(null)
const comments = ref([])
const commentContent = ref('')
const ratingStats = ref(null)
const myRating = ref(null)
const showRatingDialog = ref(false)
const showImagePreview = ref(false)
const currentImageIndex = ref(0)
const ratingForm = ref({
  gameplay_score: 0,
  graphics_score: 0,
  story_score: 0,
  sound_score: 0,
  overall_score: 0
})

const fetchGame = async () => {
  const res = await api.get(`/games/${route.params.id}`)
  game.value = res.data.game
}

const fetchComments = async () => {
  const res = await api.get('/comments', { params: { game_id: route.params.id } })
  comments.value = res.data.comments
}

const fetchRatings = async () => {
  try {
    const res = await api.get('/ratings', { params: { game_id: route.params.id } })
    ratingStats.value = res.data.stats
    
    if (userStore.isLoggedIn) {
      try {
        const myRes = await api.get('/ratings/my', { params: { game_id: route.params.id } })
        myRating.value = myRes.data.rating
        if (myRating.value) {
          ratingForm.value = { ...myRating.value }
        }
      } catch (error) {
        // 如果获取个人评分失败，不影响页面其他内容的显示
        console.error('获取个人评分失败:', error)
      }
    }
  } catch (error) {
    console.error('获取评分统计失败:', error)
  }
}

const submitComment = async () => {
  if (!commentContent.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  try {
    await api.post('/comments', {
      game_id: route.params.id,
      content: commentContent.value
    })
    ElMessage.success('评论成功')
    commentContent.value = ''
    fetchComments()
  } catch (error) {
    console.error('评论失败:', error)
  }
}

const likeComment = async (commentId) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    await api.post(`/comments/${commentId}/like`)
    fetchComments()
  } catch (error) {
    console.error('点赞失败:', error)
  }
}

const reportComment = async (commentId) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    const { value } = await ElMessageBox.prompt('请输入举报理由', '举报评论')
    await api.post(`/comments/${commentId}/report`, { reason: value })
    ElMessage.success('举报成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('举报失败:', error)
    }
  }
}

const replyTo = async (comment) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    const { value } = await ElMessageBox.prompt(`回复 ${comment.username}`, '发表回复', {
      inputPlaceholder: '请输入回复内容...',
      inputType: 'textarea'
    })
    if (value && value.trim()) {
      await api.post('/comments', {
        game_id: route.params.id,
        parent_id: comment.id,
        content: value
      })
      ElMessage.success('回复成功')
      fetchComments()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('回复失败:', error)
    }
  }
}

const submitRating = async () => {
  try {
    await api.post('/ratings', {
      game_id: route.params.id,
      ...ratingForm.value
    })
    ElMessage.success('评分成功')
    showRatingDialog.value = false
    fetchRatings()
  } catch (error) {
    console.error('评分失败:', error)
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

// 图片预览相关函数
const handleImagePreview = (index) => {
  currentImageIndex.value = index
  showImagePreview.value = true
}

const prevImage = () => {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
  }
}

const nextImage = () => {
  if (currentImageIndex.value < game.value.images.length - 1) {
    currentImageIndex.value++
  }
}

onMounted(() => {
  fetchGame()
  fetchComments()
  fetchRatings()
})
</script>

<style scoped>
.game-detail-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 40px;
  min-height: calc(100vh - 200px);
}

.game-detail {
  width: 100%;
}

/* 游戏信息卡片 */
.game-info-card {
  margin-bottom: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.game-cover {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
}

.game-cover:hover {
  transform: scale(1.02);
}

.game-title {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 20px 0;
}

.game-meta {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.game-meta p {
  margin: 8px 0;
  font-size: 15px;
  color: #606266;
  line-height: 1.6;
}

.game-meta strong {
  color: #303133;
  margin-right: 8px;
}

.game-description {
  margin-top: 20px;
  padding: 20px;
  background: #fff;
  border-left: 4px solid #409eff;
  border-radius: 4px;
}

.game-description h3 {
  font-size: 18px;
  color: #303133;
  margin: 0 0 12px 0;
}

.game-description p {
  font-size: 15px;
  line-height: 1.8;
  color: #606266;
  margin: 0;
  text-align: justify;
}

/* 评分卡片 */
.rating-card {
  margin-bottom: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 20px 0;
  padding-bottom: 15px;
  border-bottom: 2px solid #e4e7ed;
}

.rating-stats {
  display: flex;
  gap: 40px;
  margin-bottom: 25px;
  padding: 20px;
  background: linear-gradient(135deg,#7117ea,#ea6060);
  border-radius: 12px;
  color: white;
}

.overall-rating {
  text-align: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  min-width: 150px;
}

.rating-number {
  font-size: 48px;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 8px;
}

.rating-label {
  font-size: 16px;
  margin-bottom: 5px;
  opacity: 0.9;
}

.rating-count {
  font-size: 14px;
  opacity: 0.8;
}

.rating-details {
  flex: 1;
  display: flex;
  align-items: center;
}

.rating-item {
  text-align: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.rating-name {
  font-size: 14px;
  margin-bottom: 8px;
  opacity: 0.9;
}

.rating-value {
  font-size: 28px;
  font-weight: bold;
}

.rate-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  border-radius: 8px;
}

.login-tip {
  margin-top: 15px;
}

/* 图集卡片 */
.gallery-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.gallery-container {
  margin-top: 20px;
  position: relative;
}

.gallery-scroll {
  display: flex;
  gap: 15px;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 10px 0;
  scroll-behavior: smooth;
}

.gallery-scroll::-webkit-scrollbar {
  height: 8px;
}

.gallery-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.gallery-scroll::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.gallery-scroll::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.gallery-item {
  position: relative;
  flex-shrink: 0;
  width: 280px;
  height: 160px;
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.gallery-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.gallery-item:hover .gallery-overlay {
  opacity: 1;
}

.gallery-image {
  width: 100%;
  height: 100%;
  display: block;
}

.gallery-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.gallery-overlay .el-icon {
  font-size: 40px;
  color: white;
}

.image-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
}

.image-loading .el-icon {
  font-size: 30px;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
}

.image-error .el-icon {
  font-size: 40px;
}

/* 图片预览 */
.preview-container {
  text-align: center;
}

.preview-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.preview-index {
  font-size: 16px;
  color: #606266;
  min-width: 80px;
  text-align: center;
}

/* 评论卡片 */
.comment-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.comment-form {
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.submit-comment-btn {
  margin-top: 15px;
  width: 100%;
  height: 40px;
  font-size: 15px;
}

.comments-list {
  margin-top: 30px;
}

.no-comments {
  padding: 40px 0;
  text-align: center;
}

.comment-item {
  padding: 25px;
  margin-bottom: 20px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.comment-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #c0c4cc;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.comment-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  background: linear-gradient(135deg,#7117ea,#ea6060);
  color: white;
  font-weight: bold;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.username {
  font-size: 16px;
  color: #303133;
}

.comment-time {
  font-size: 13px;
  color: #909399;
}

.comment-content {
  font-size: 15px;
  line-height: 1.8;
  color: #606266;
  margin-bottom: 15px;
  padding: 15px;
  background: #fafafa;
  border-radius: 6px;
  word-wrap: break-word;
}

.comment-actions {
  display: flex;
  gap: 10px;
}

.comment-actions .el-button {
  border-radius: 6px;
}

.replies {
  margin-top: 20px;
  padding: 15px 20px;
  background: #f9fafb;
  border-left: 3px solid #409eff;
  border-radius: 4px;
}

.reply-item {
  padding: 10px 0;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
  border-bottom: 1px dashed #e4e7ed;
}

.reply-item:last-child {
  border-bottom: none;
}

.reply-username {
  color: #409eff;
  margin-right: 8px;
}

.reply-content {
  color: #606266;
}

/* 评分对话框 */
.rate-value {
  margin-left: 15px;
  font-size: 16px;
  font-weight: bold;
  color: #409eff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .game-detail-container {
    padding: 20px 15px;
  }
  
  .game-title {
    font-size: 24px;
  }
  
  .rating-stats {
    flex-direction: column;
    gap: 20px;
  }
  
  .overall-rating {
    min-width: auto;
  }
}
</style>
