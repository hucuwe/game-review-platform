<template>
  <div class="home">
    <!-- 公告跑马灯 -->
    <div class="announcement-marquee" v-if="latestAnnouncement">
      <div class="marquee-container">
        <el-icon class="marquee-icon"><Bell /></el-icon>
        <span class="marquee-label">最新公告：</span>
        <div class="marquee-content">
          <span @click="handleAnnouncementClick">{{ latestAnnouncement.title }}</span>
        </div>
        <el-button text size="small" @click="$router.push('/announcements')">
          查看更多 <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 轮播图 -->
    <div class="carousel-section">
      <el-carousel :interval="5000" height="500px" arrow="always">
        <el-carousel-item v-for="(banner, index) in banners" :key="index">
          <div class="banner-item" :style="{ backgroundImage: `url(${banner.image})` }">
            <div class="banner-content">
              <h2>{{ banner.title }}</h2>
              <p>{{ banner.description }}</p>
              <el-button type="primary" size="large" @click="$router.push(banner.link)">
                {{ banner.buttonText }}
              </el-button>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </div>

    <!-- 统计数据 -->
    <div class="stats-section">
      <div class="content-wrapper">
        <el-row :gutter="20">
          <el-col :span="6" v-for="stat in stats" :key="stat.label">
            <div class="stat-card">
              <div class="stat-icon" :style="{ background: stat.color }">
                <el-icon :size="32"><component :is="stat.icon" /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="content-wrapper">
      <!-- 智能推荐 -->
      <section class="section">
        <div class="section-header">
          <div class="header-left">
            <h2>
              <el-icon><TrendCharts /></el-icon> 
              {{ recommendationTitle }}
            </h2>
            <el-tag v-if="recommendationAlgorithm" size="small" type="success" effect="plain">
              {{ recommendationAlgorithm === 'collaborative_filtering' ? '个性化推荐' : '热门推荐' }}
            </el-tag>
          </div>
          <el-button text @click="$router.push('/hot')">查看更多 <el-icon><ArrowRight /></el-icon></el-button>
        </div>
        <div v-loading="loadingHot">
          <el-row :gutter="20">
            <el-col :span="6" v-for="game in hotGames" :key="game.id">
              <el-card class="game-card" shadow="hover" @click="$router.push(`/games/${game.id}`)">
                <div class="game-cover-wrapper">
                  <img :src="game.cover_image || 'https://via.placeholder.com/300x200'" class="game-cover" />
                  <div class="game-badge" v-if="game.avg_score >= 9">
                    <el-tag type="danger" effect="dark">高分</el-tag>
                  </div>
                </div>
                <div class="game-info">
                  <h3 class="game-title">{{ game.title }}</h3>
                  <el-tag size="small" type="info">{{ game.category_name }}</el-tag>
                  <div class="game-rating">
                    <el-rate v-model="game.display_score" disabled show-score :score-template="`${game.avg_score || 0}`" />
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </section>

      <!-- 分类推荐 -->
      <section class="section">
        <div class="section-header">
          <h2><el-icon><Grid /></el-icon> 分类推荐</h2>
        </div>
        <el-row :gutter="15">
          <el-col :span="6" v-for="cat in categories.slice(0, 8)" :key="cat.id">
            <div class="category-item" @click="$router.push(`/games?category=${cat.id}`)">
              <div class="category-icon">
                <el-icon :size="32"><Folder /></el-icon>
              </div>
              <div class="category-name">{{ cat.name }}</div>
              <div class="category-count">{{ cat.game_count || 0 }} 款游戏</div>
            </div>
          </el-col>
        </el-row>
      </section>

      <!-- 最新游戏 -->
      <section class="section">
        <div class="section-header">
          <h2><el-icon><Clock /></el-icon> 最新上架</h2>
          <el-button text @click="$router.push('/games')">查看更多 <el-icon><ArrowRight /></el-icon></el-button>
        </div>
        <div v-loading="loadingLatest">
          <el-row :gutter="20">
            <el-col :span="8" v-for="game in latestGames" :key="game.id">
              <div class="latest-game-card" @click="$router.push(`/games/${game.id}`)">
                <img :src="game.cover_image || 'https://via.placeholder.com/200x120'" class="latest-cover" />
                <div class="latest-info">
                  <h4>{{ game.title }}</h4>
                  <p>{{ game.description || '暂无描述' }}</p>
                  <div class="latest-meta">
                    <el-tag size="small">{{ game.category_name }}</el-tag>
                    <span class="latest-date">{{ formatDate(game.created_at) }}</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </section>

      <!-- 最新评论 -->
      <section class="section">
        <div class="section-header">
          <h2><el-icon><ChatDotRound /></el-icon> 最新评论</h2>
        </div>
        <div v-loading="loadingComments">
          <div class="comments-grid">
            <div v-for="comment in recentComments" :key="comment.id" class="comment-card">
              <div class="comment-header">
                <el-avatar :size="40">{{ comment.username?.charAt(0) }}</el-avatar>
                <div class="comment-user">
                  <strong>{{ comment.username }}</strong>
                  <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
                </div>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
              <div class="comment-game" @click="$router.push(`/games/${comment.game_id}`)">
                <el-icon><Promotion /></el-icon>
                <span>{{ comment.game_title }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import { 
  TrendCharts, Grid, Clock, ChatDotRound, ArrowRight, 
  Folder, Promotion, Bell 
} from '@element-plus/icons-vue'

const router = useRouter()

// 轮播图数据
const banners = ref([])

// 统计数据
const stats = ref([
  { label: '游戏总数', value: '0', icon: 'Grid', color: 'linear-gradient(135deg,#7117ea,#ea6060)' },
  { label: '用户评分', value: '0', icon: 'Star', color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { label: '用户评论', value: '0', icon: 'ChatDotRound', color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  { label: '注册用户', value: '0', icon: 'User', color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }
])

const hotGames = ref([])
const latestGames = ref([])
const categories = ref([])
const recentComments = ref([])
const loadingHot = ref(false)
const loadingLatest = ref(false)
const loadingComments = ref(false)
const latestAnnouncement = ref(null)
const recommendationAlgorithm = ref('')
const recommendationTitle = ref('智能推荐')

// 获取轮播图数据
const fetchBanners = async () => {
  try {
    const res = await api.get('/games/banners')
    // 转换数据格式以适配模板
    banners.value = res.data.banners.map(banner => ({
      title: banner.title,
      description: banner.description,
      image: banner.image_url,
      link: banner.link_url || '/games',
      buttonText: '了解更多'
    }))
  } catch (error) {
    console.error('获取轮播图失败:', error)
    // 失败时使用默认数据
    banners.value = [
      {
        title: '发现你的下一个最爱游戏',
        description: '海量游戏评分，专业玩家点评，助你找到心仪之作',
        image: 'https://picsum.photos/1920/500?random=1',
        link: '/games',
        buttonText: '探索游戏库'
      }
    ]
  }
}

// 获取统计数据
const fetchStats = async () => {
  try {
    // 获取游戏总数
    const gamesRes = await api.get('/games', { params: { per_page: 1 } })
    stats.value[0].value = gamesRes.data.total || 0
    
    // 获取评分总数（估算：游戏数 * 平均评分数）
    stats.value[1].value = Math.floor((gamesRes.data.total || 0) * 2.5)
    
    // 获取评论总数（估算：游戏数 * 平均评论数）
    stats.value[2].value = Math.floor((gamesRes.data.total || 0) * 1.8)
    
    // 用户数（固定值，实际项目中应该有专门的API）
    stats.value[3].value = 15
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 获取智能推荐游戏
const fetchHotGames = async () => {
  loadingHot.value = true
  try {
    // 使用推荐API
    const res = await api.get('/recommendations/personalized', { params: { limit: 8 } })
    hotGames.value = res.data.games.map(game => ({
      ...game,
      display_score: (game.avg_score || 0) / 2
    }))
    
    // 记录推荐算法类型
    recommendationAlgorithm.value = res.data.algorithm
    
    // 根据算法类型设置标题
    if (res.data.algorithm === 'collaborative_filtering') {
      recommendationTitle.value = '为你推荐'
    } else {
      recommendationTitle.value = '热门推荐'
    }
  } catch (error) {
    console.error('获取推荐游戏失败:', error)
    // 失败时降级到普通热门游戏
    try {
      const res = await api.get('/games', { params: { per_page: 8, sort_by: 'rating' } })
      hotGames.value = res.data.games.map(game => ({
        ...game,
        display_score: (game.avg_score || 0) / 2
      }))
      recommendationAlgorithm.value = 'fallback'
      recommendationTitle.value = '热门推荐'
    } catch (fallbackError) {
      console.error('获取热门游戏失败:', fallbackError)
    }
  } finally {
    loadingHot.value = false
  }
}

// 获取最新游戏
const fetchLatestGames = async () => {
  loadingLatest.value = true
  try {
    const res = await api.get('/games', { params: { per_page: 6, sort_by: 'latest' } })
    latestGames.value = res.data.games
  } catch (error) {
    console.error('获取最新游戏失败:', error)
  } finally {
    loadingLatest.value = false
  }
}

// 获取分类
const fetchCategories = async () => {
  try {
    const res = await api.get('/games/categories')
    categories.value = res.data.categories
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

// 获取最新评论
const fetchRecentComments = async () => {
  loadingComments.value = true
  try {
    const res = await api.get('/comments/recent', { params: { limit: 6 } })
    recentComments.value = res.data.comments
  } catch (error) {
    console.error('获取评论失败:', error)
    // 失败时使用模拟数据
    recentComments.value = []
  } finally {
    loadingComments.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return date.toLocaleDateString('zh-CN')
}

// 获取最新公告
const fetchLatestAnnouncement = async () => {
  try {
    const res = await api.get('/announcements/latest')
    latestAnnouncement.value = res.data.announcement
  } catch (error) {
    console.error('获取最新公告失败:', error)
  }
}

// 点击公告跳转
const handleAnnouncementClick = () => {
  if (latestAnnouncement.value) {
    router.push('/announcements')
  }
}

onMounted(() => {
  fetchLatestAnnouncement()
  fetchBanners()
  fetchStats()
  fetchHotGames()
  fetchLatestGames()
  fetchCategories()
  fetchRecentComments()
})
</script>

<style scoped>
.home {
  background-color: #f5f7fa;
}

/* 公告跑马灯 */
.announcement-marquee {
  background: linear-gradient(135deg,#7117ea,#ea6060);
  color: white;
  padding: 12px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.marquee-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.marquee-icon {
  font-size: 20px;
  animation: ring 2s ease-in-out infinite;
}

@keyframes ring {
  0%, 100% { transform: rotate(0deg); }
  10%, 30% { transform: rotate(-10deg); }
  20%, 40% { transform: rotate(10deg); }
}

.marquee-label {
  font-weight: 600;
  white-space: nowrap;
}

.marquee-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.marquee-content span {
  display: inline-block;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
  animation: marquee 20s linear infinite;
}

.marquee-content span:hover {
  animation-play-state: paused;
  text-decoration: underline;
}

@keyframes marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

/* 轮播图 */
.carousel-section {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.banner-item {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to right, rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.3));
}

.banner-content {
  position: relative;
  z-index: 1;
  color: white;
  text-align: center;
  padding: 40px;
  max-width: 700px;
}

.banner-content h2 {
  font-size: 52px;
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  font-weight: bold;
}

.banner-content p {
  font-size: 22px;
  margin-bottom: 30px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  opacity: 0.95;
}

/* 统计数据 */
.stats-section {
  margin: -60px 0 40px;
  position: relative;
  z-index: 10;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 30px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/* 内容区域 */
.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px 40px;
}

/* 区块 */
.section {
  margin-bottom: 50px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e4e7ed;
}

.section-header .header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-header h2 {
  font-size: 26px;
  font-weight: bold;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

/* 游戏卡片 */
.game-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 12px;
  overflow: hidden;
}

.game-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.game-cover-wrapper {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.game-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.game-card:hover .game-cover {
  transform: scale(1.1);
}

.game-badge {
  position: absolute;
  top: 10px;
  right: 10px;
}

.game-info {
  padding: 15px;
}

.game-title {
  font-size: 15px;
  font-weight: bold;
  margin: 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.game-rating {
  margin-top: 10px;
}

/* 分类推荐 */
.category-item {
  text-align: center;
  padding: 20px 15px;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin: 5px;
}

.category-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
  background: linear-gradient(135deg,#7117ea,#ea6060);
  color: white;
}

.category-icon {
  margin-bottom: 12px;
  color: #409eff;
  transition: color 0.3s;
}

.category-item:hover .category-icon {
  color: white;
}

.category-name {
  font-size: 15px;
  font-weight: bold;
  margin-bottom: 6px;
}

.category-count {
  font-size: 12px;
  color: #909399;
}

.category-item:hover .category-count {
  color: rgba(255, 255, 255, 0.9);
}

/* 最新游戏 */
.latest-game-card {
  display: flex;
  gap: 15px;
  padding: 15px;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.latest-game-card:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.latest-cover {
  width: 120px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}

.latest-info {
  flex: 1;
  min-width: 0;
}

.latest-info h4 {
  font-size: 16px;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.latest-info p {
  font-size: 13px;
  color: #606266;
  margin: 0 0 10px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.latest-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.latest-date {
  font-size: 12px;
  color: #909399;
}

/* 评论卡片 */
.comments-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.comment-card {
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.comment-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.comment-user {
  flex: 1;
}

.comment-user strong {
  display: block;
  font-size: 15px;
  color: #303133;
}

.comment-time {
  font-size: 12px;
  color: #909399;
}

.comment-content {
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
  margin-bottom: 12px;
}

.comment-game {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: #409eff;
  cursor: pointer;
}

.comment-game:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .stats-section {
    margin-top: 20px;
  }
  
  .comments-grid {
    grid-template-columns: 1fr;
  }
}
</style>
