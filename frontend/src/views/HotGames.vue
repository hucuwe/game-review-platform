<template>
  <div class="hot-games">
    <div class="hot-header">
      <h1>🔥 热门游戏</h1>
      <p>最受玩家喜爱的精品游戏推荐</p>
    </div>

    <div class="content-wrapper">
      <!-- 排行榜 -->
      <el-card shadow="hover" class="ranking-card">
        <template #header>
          <el-segmented v-model="rankingType" :options="rankingOptions" size="large" />
        </template>

        <div v-loading="loading">
          <el-empty v-if="hotGames.length === 0" description="暂无数据" />
          <div v-else class="ranking-list">
            <div v-for="(game, index) in hotGames" :key="game.id" class="ranking-item" @click="$router.push(`/games/${game.id}`)">
              <div class="rank-number" :class="`rank-${index + 1}`">
                {{ index + 1 }}
              </div>
              <img :src="game.cover_image || 'https://via.placeholder.com/120x80'" class="rank-cover" />
              <div class="rank-info">
                <h3>{{ game.title }}</h3>
                <div class="rank-meta">
                  <el-tag size="small">{{ game.category_name }}</el-tag>
                  <span class="developer">{{ game.developer }}</span>
                </div>
                <p class="rank-desc">{{ game.description || '暂无描述' }}</p>
              </div>
              <div class="rank-stats">
                <div class="stat-item">
                  <div class="stat-value">{{ game.avg_score || 0 }}</div>
                  <div class="stat-label">评分</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ game.rating_count || 0 }}</div>
                  <div class="stat-label">评分数</div>
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
import { ref, onMounted, watch } from 'vue'
import api from '@/utils/api'

const rankingType = ref('评分最高')
const rankingOptions = ['评分最高', '最新发布', '最多评论']
const hotGames = ref([])
const loading = ref(false)

const fetchHotGames = async () => {
  loading.value = true
  try {
    let sortBy = 'rating' // 默认按评分排序
    
    // 根据排序类型设置参数
    if (rankingType.value === '评分最高') {
      sortBy = 'rating'
    } else if (rankingType.value === '最新发布') {
      sortBy = 'latest'
    } else if (rankingType.value === '最多评论') {
      sortBy = 'comments' // 需要后端支持
    }
    
    const res = await api.get('/games', { 
      params: { 
        per_page: 20,
        sort_by: sortBy
      } 
    })
    
    hotGames.value = res.data.games.map(game => ({
      ...game,
      display_score: (game.avg_score || 0) / 2
    }))
  } catch (error) {
    console.error('获取热门游戏失败:', error)
  } finally {
    loading.value = false
  }
}

watch(rankingType, () => {
  // 根据不同排序类型重新获取数据
  fetchHotGames()
})

onMounted(() => {
  fetchHotGames()
})
</script>

<style scoped>
.hot-games {
  background-color: #f5f7fa;
  min-height: calc(100vh - 64px);
}

.hot-header {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  padding: 60px 20px;
  text-align: center;
}

.hot-header h1 {
  font-size: 42px;
  margin-bottom: 15px;
}

.hot-header p {
  font-size: 18px;
  opacity: 0.9;
}

.content-wrapper {
  max-width: 1200px;
  margin: -40px auto 0;
  padding: 0 20px 40px;
}

.ranking-card {
  border-radius: 12px;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  cursor: pointer;
  transition: all 0.3s;
}

.ranking-item:hover {
  transform: translateX(10px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.rank-number {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  background: linear-gradient(135deg,#7117ea,#ea6060);
  color: white;
  border-radius: 12px;
  flex-shrink: 0;
}

.rank-number.rank-1 {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  font-size: 28px;
}

.rank-number.rank-2 {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  font-size: 26px;
}

.rank-number.rank-3 {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  font-size: 26px;
}

.rank-cover {
  width: 120px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}

.rank-info {
  flex: 1;
  min-width: 0;
}

.rank-info h3 {
  font-size: 18px;
  margin: 0 0 10px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rank-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.developer {
  color: #909399;
  font-size: 13px;
}

.rank-desc {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.rank-stats {
  display: flex;
  gap: 30px;
  flex-shrink: 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
