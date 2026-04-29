<template>
  <div class="my-ratings">
    <div class="ratings-header">
      <h1>我的评分</h1>
      <p>查看和管理你的游戏评分记录</p>
    </div>

    <div class="content-wrapper">
      <el-card shadow="hover">
        <div v-loading="loading">
          <el-empty v-if="ratings.length === 0" description="你还没有评分任何游戏">
            <el-button type="primary" @click="$router.push('/games')">去评分</el-button>
          </el-empty>

          <div v-else class="ratings-list">
            <div v-for="rating in ratings" :key="rating.id" class="rating-item">
              <div class="rating-content">
                <!-- 左侧：游戏信息 -->
                <div class="rating-game" @click="$router.push(`/games/${rating.game_id}`)">
                  <img :src="rating.game?.cover_image || 'https://via.placeholder.com/120x90'" class="game-thumb" />
                  <div class="game-info">
                    <h3>{{ rating.game?.title || '未知游戏' }}</h3>
                    <div class="game-meta">
                      <el-tag size="small" type="primary">{{ rating.game?.category_name }}</el-tag>
                      <span class="game-developer">{{ rating.game?.developer }}</span>
                    </div>
                    <div class="rating-time">
                      <el-icon><Clock /></el-icon>
                      <span>{{ formatDate(rating.created_at) }}</span>
                    </div>
                  </div>
                </div>

                <!-- 中间：详细评分 -->
                <div class="rating-scores">
                  <div class="score-item">
                    <span class="score-label">玩法</span>
                    <el-rate v-model="rating.gameplay_display" disabled show-score text-color="#ff9900" />
                    <span class="score-value">{{ rating.gameplay_score }}/10</span>
                  </div>
                  <div class="score-item">
                    <span class="score-label">画面</span>
                    <el-rate v-model="rating.graphics_display" disabled show-score text-color="#ff9900" />
                    <span class="score-value">{{ rating.graphics_score }}/10</span>
                  </div>
                  <div class="score-item">
                    <span class="score-label">剧情</span>
                    <el-rate v-model="rating.story_display" disabled show-score text-color="#ff9900" />
                    <span class="score-value">{{ rating.story_score }}/10</span>
                  </div>
                  <div class="score-item">
                    <span class="score-label">音效</span>
                    <el-rate v-model="rating.sound_display" disabled show-score text-color="#ff9900" />
                    <span class="score-value">{{ rating.sound_score }}/10</span>
                  </div>
                </div>

                <!-- 右侧：综合评分 -->
                <div class="rating-overall">
                  <div class="overall-label">综合评分</div>
                  <div class="overall-score">{{ rating.overall_score }}</div>
                  <el-rate v-model="rating.overall_display" disabled show-score text-color="#ff9900" />
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="$router.push(`/games/${rating.game_id}`)"
                    style="margin-top: 10px"
                  >
                    查看详情
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const ratings = ref([])
const loading = ref(false)

const fetchMyRatings = async () => {
  loading.value = true
  try {
    const res = await api.get('/ratings/my/all')
    // 转换评分数据，将数值转换为适合el-rate显示的格式（5星制）
    ratings.value = res.data.ratings.map(rating => ({
      ...rating,
      gameplay_display: rating.gameplay_score / 2, // 10分制转5星制
      graphics_display: rating.graphics_score / 2,
      story_display: rating.story_score / 2,
      sound_display: rating.sound_score / 2,
      overall_display: rating.overall_score / 2
    }))
  } catch (error) {
    console.error('获取评分失败:', error)
    ElMessage.error('获取评分失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

onMounted(() => {
  fetchMyRatings()
})
</script>

<style scoped>
.my-ratings {
  background-color: #f5f7fa;
  min-height: calc(100vh - 64px);
}

.ratings-header {
  background: linear-gradient(135deg,#7117ea,#ea6060);
  color: white;
  padding: 60px 20px;
  text-align: center;
}

.ratings-header h1 {
  font-size: 42px;
  margin-bottom: 15px;
}

.ratings-header p {
  font-size: 18px;
  opacity: 0.9;
}

.content-wrapper {
  max-width: 1200px;
  margin: -40px auto 0;
  padding: 0 20px 40px;
}

.ratings-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.rating-item {
  padding: 20px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.rating-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #c0c4cc;
}

.rating-content {
  display: flex;
  gap: 30px;
  align-items: center;
}

/* 游戏信息区域 */
.rating-game {
  display: flex;
  align-items: center;
  gap: 15px;
  cursor: pointer;
  flex-shrink: 0;
  width: 320px;
  transition: all 0.3s ease;
}

.rating-game:hover {
  transform: translateX(5px);
}

.game-thumb {
  width: 120px;
  height: 90px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.game-info {
  flex: 1;
}

.game-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.game-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.game-developer {
  font-size: 13px;
  color: #909399;
}

.rating-time {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #909399;
}

/* 评分详情区域 */
.rating-scores {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.score-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.score-value {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

/* 综合评分区域 */
.rating-overall {
  flex-shrink: 0;
  width: 160px;
  background: linear-gradient(135deg,#7117ea,#ea6060);
  padding: 20px;
  border-radius: 12px;
  color: white;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.overall-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 10px;
}

.overall-score {
  font-size: 48px;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 10px;
}

.rating-overall :deep(.el-rate) {
  justify-content: center;
}

.rating-overall :deep(.el-rate__icon) {
  color: white !important;
}

.rating-overall :deep(.el-rate__text) {
  color: white !important;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .rating-content {
    flex-direction: column;
    align-items: stretch;
  }

  .rating-game {
    width: 100%;
  }

  .rating-scores {
    grid-template-columns: 1fr;
  }

  .rating-overall {
    width: 100%;
  }
}
</style>
