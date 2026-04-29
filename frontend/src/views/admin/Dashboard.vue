<template>
  <div class="dashboard">
    <h2>数据概览</h2>
    
    <!-- 核心统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg,#7117ea,#ea6060)">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_users }}</div>
              <div class="stat-label">总用户数</div>
              <div class="stat-extra">今日新增: {{ stats.today_users }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
              <el-icon :size="32"><Tickets /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_games }}</div>
              <div class="stat-label">游戏总数</div>
              <div class="stat-extra">已发布: {{ stats.published_games }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
              <el-icon :size="32"><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_comments }}</div>
              <div class="stat-label">评论总数</div>
              <div class="stat-extra">今日新增: {{ stats.today_comments }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%)">
              <el-icon :size="32"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending_reports }}</div>
              <div class="stat-label">待处理举报</div>
              <div class="stat-extra" :class="stats.pending_reports > 0 ? 'warning' : ''">
                {{ stats.pending_reports > 0 ? '需要关注' : '无待处理' }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 用户增长趋势 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><TrendCharts /></el-icon> 用户增长趋势（最近7天）</span>
            </div>
          </template>
          <div class="chart-container">
            <div v-if="chartData.user_trend.length > 0" class="bar-chart">
              <div v-for="item in chartData.user_trend" :key="item.date" class="bar-item">
                <div class="bar-wrapper">
                  <div 
                    class="bar" 
                    :style="{ height: getBarHeight(item.count, maxUserCount) + '%' }"
                    :title="`${item.count}人`"
                  >
                    <span class="bar-value">{{ item.count }}</span>
                  </div>
                </div>
                <div class="bar-label">{{ formatDate(item.date) }}</div>
              </div>
            </div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-card>
      </el-col>

      <!-- 评论活跃度 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><ChatLineRound /></el-icon> 评论活跃度（最近7天）</span>
            </div>
          </template>
          <div class="chart-container">
            <div v-if="chartData.comment_trend.length > 0" class="bar-chart">
              <div v-for="item in chartData.comment_trend" :key="item.date" class="bar-item">
                <div class="bar-wrapper">
                  <div 
                    class="bar comment-bar" 
                    :style="{ height: getBarHeight(item.count, maxCommentCount) + '%' }"
                    :title="`${item.count}条`"
                  >
                    <span class="bar-value">{{ item.count }}</span>
                  </div>
                </div>
                <div class="bar-label">{{ formatDate(item.date) }}</div>
              </div>
            </div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 游戏分类分布 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><PieChart /></el-icon> 游戏分类分布</span>
            </div>
          </template>
          <div class="chart-container">
            <div v-if="chartData.category_data.length > 0" class="category-chart">
              <div v-for="(item, index) in chartData.category_data" :key="item.name" class="category-item">
                <div class="category-info">
                  <span class="category-name">{{ item.name }}</span>
                  <span class="category-count">{{ item.count }}款</span>
                </div>
                <div class="category-bar-wrapper">
                  <div 
                    class="category-bar" 
                    :style="{ 
                      width: getPercentage(item.count, totalGames) + '%',
                      background: getCategoryColor(index)
                    }"
                  >
                    <span class="category-percent">{{ getPercentage(item.count, totalGames).toFixed(1) }}%</span>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-card>
      </el-col>

      <!-- 评分TOP10游戏 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Trophy /></el-icon> 评分TOP10游戏</span>
            </div>
          </template>
          <div class="chart-container">
            <div v-if="chartData.top_games.length > 0" class="top-games-list">
              <div v-for="(game, index) in chartData.top_games" :key="game.title" class="top-game-item">
                <div class="game-rank" :class="`rank-${index + 1}`">{{ index + 1 }}</div>
                <div class="game-info">
                  <div class="game-title">{{ game.title }}</div>
                  <div class="game-score-bar">
                    <div class="score-fill" :style="{ width: (game.score / 10 * 100) + '%' }"></div>
                    <span class="score-text">{{ game.score.toFixed(1) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细统计 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>用户统计</span>
            </div>
          </template>
          <el-row :gutter="10">
            <el-col :span="12">
              <div class="detail-stat">
                <div class="detail-label">活跃用户</div>
                <div class="detail-value">{{ stats.active_users }}</div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-stat">
                <div class="detail-label">封禁用户</div>
                <div class="detail-value danger">{{ stats.banned_users }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>内容统计</span>
            </div>
          </template>
          <el-row :gutter="10">
            <el-col :span="8">
              <div class="detail-stat">
                <div class="detail-label">总评分数</div>
                <div class="detail-value">{{ stats.total_ratings }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-stat">
                <div class="detail-label">正常评论</div>
                <div class="detail-value">{{ stats.normal_comments }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-stat">
                <div class="detail-label">已举报</div>
                <div class="detail-value warning">{{ stats.reported_comments }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>快捷操作</span>
        </div>
      </template>
      <el-row :gutter="15">
        <el-col :span="6">
          <el-button type="primary" @click="$router.push('/admin/users')" style="width: 100%">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="success" @click="$router.push('/admin/games')" style="width: 100%">
            <el-icon><Tickets /></el-icon>
            <span>游戏管理</span>
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="info" @click="$router.push('/admin/comments')" style="width: 100%">
            <el-icon><ChatDotRound /></el-icon>
            <span>评论管理</span>
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="warning" @click="$router.push('/admin/reports')" style="width: 100%">
            <el-icon><Warning /></el-icon>
            <span>举报管理</span>
          </el-button>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'
import { TrendCharts, ChatLineRound, PieChart, Trophy } from '@element-plus/icons-vue'

const stats = ref({
  total_users: 0,
  total_games: 0,
  total_comments: 0,
  total_ratings: 0,
  pending_reports: 0,
  today_users: 0,
  today_comments: 0,
  today_ratings: 0,
  active_users: 0,
  banned_users: 0,
  published_games: 0,
  draft_games: 0,
  normal_comments: 0,
  reported_comments: 0,
  deleted_comments: 0
})

const chartData = ref({
  user_trend: [],
  comment_trend: [],
  category_data: [],
  top_games: []
})

const maxUserCount = computed(() => {
  return Math.max(...chartData.value.user_trend.map(item => item.count), 1)
})

const maxCommentCount = computed(() => {
  return Math.max(...chartData.value.comment_trend.map(item => item.count), 1)
})

const totalGames = computed(() => {
  return chartData.value.category_data.reduce((sum, item) => sum + item.count, 0)
})

const fetchStats = async () => {
  try {
    const res = await api.get('/admin/stats')
    stats.value = res.data.stats
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  }
}

const fetchChartData = async () => {
  try {
    const res = await api.get('/admin/stats/charts')
    chartData.value = res.data
  } catch (error) {
    console.error('获取图表数据失败:', error)
  }
}

const getBarHeight = (value, max) => {
  if (max === 0) return 0
  return Math.max((value / max) * 100, 5) // 最小5%高度
}

const getPercentage = (value, total) => {
  if (total === 0) return 0
  return (value / total) * 100
}

const getCategoryColor = (index) => {
  const colors = [
    'linear-gradient(135deg,#7117ea,#ea6060)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)'
  ]
  return colors[index % colors.length]
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

onMounted(() => {
  fetchStats()
  fetchChartData()
})
</script>

<style scoped>
.dashboard {
  padding-bottom: 20px;
}

.dashboard h2 {
  margin-bottom: 25px;
  font-size: 24px;
  color: #303133;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
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
  margin-bottom: 5px;
}

.stat-extra {
  font-size: 12px;
  color: #67c23a;
}

.stat-extra.warning {
  color: #e6a23c;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.chart-container {
  min-height: 250px;
}

/* 柱状图样式 */
.bar-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 220px;
  padding: 10px 0;
}

.bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.bar-wrapper {
  width: 100%;
  height: 180px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.bar {
  width: 60%;
  background: linear-gradient(135deg,#7117ea,#ea6060);
  border-radius: 4px 4px 0 0;
  position: relative;
  transition: all 0.3s;
  cursor: pointer;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 5px;
}

.bar:hover {
  opacity: 0.8;
}

.comment-bar {
  background: linear-gradient(180deg, #4facfe 0%, #00f2fe 100%);
}

.bar-value {
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.bar-label {
  font-size: 12px;
  color: #606266;
  text-align: center;
}

/* 分类图表样式 */
.category-chart {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 10px 0;
}

.category-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.category-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.category-name {
  color: #303133;
  font-weight: 500;
}

.category-count {
  color: #909399;
}

.category-bar-wrapper {
  height: 24px;
  background: #f5f7fa;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.category-bar {
  height: 100%;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 10px;
  transition: width 0.5s;
}

.category-percent {
  color: white;
  font-size: 12px;
  font-weight: bold;
}

/* TOP游戏列表样式 */
.top-games-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 10px 0;
}

.top-game-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
  transition: all 0.3s;
}

.top-game-item:hover {
  background: #e8eaf0;
  transform: translateX(5px);
}

.game-rank {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
  background: #909399;
  flex-shrink: 0;
}

.game-rank.rank-1 {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  font-size: 16px;
}

.game-rank.rank-2 {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.game-rank.rank-3 {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.game-info {
  flex: 1;
  min-width: 0;
}

.game-title {
  font-size: 14px;
  color: #303133;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.game-score-bar {
  height: 20px;
  background: #e4e7ed;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #67c23a 0%, #85ce61 100%);
  border-radius: 10px;
  transition: width 0.5s;
}

.score-text {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  font-weight: bold;
  color: #303133;
}

.detail-stat {
  text-align: center;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.detail-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.detail-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.detail-value.danger {
  color: #f56c6c;
}

.detail-value.warning {
  color: #e6a23c;
}
</style>
