<template>
  <div class="game-library">
    <div class="library-header">
      <h1>游戏库</h1>
      <p>探索海量精品游戏，发现你的下一个最爱</p>
    </div>

    <div class="content-wrapper">
      <el-row :gutter="24">
        <!-- 筛选侧边栏 -->
        <el-col :span="5">
          <el-card shadow="hover">
            <template #header>
              <div class="filter-header">
                <span>筛选条件</span>
                <el-button text @click="resetFilters">重置</el-button>
              </div>
            </template>

            <!-- 分类筛选 -->
            <div class="filter-section">
              <h4>游戏分类</h4>
              <el-checkbox-group v-model="selectedCategories" @change="applyFilters">
                <el-checkbox v-for="cat in categories" :key="cat.id" :label="cat.id">
                  {{ cat.name }}
                </el-checkbox>
              </el-checkbox-group>
            </div>

            <!-- 评分筛选 -->
            <div class="filter-section">
              <h4>评分范围</h4>
              <el-slider v-model="ratingRange" range :min="0" :max="10" @change="applyFilters" />
              <div class="range-display">{{ ratingRange[0] }} - {{ ratingRange[1] }} 分</div>
            </div>
          </el-card>
        </el-col>

        <!-- 游戏列表 -->
        <el-col :span="19">
          <!-- 工具栏 -->
          <el-card class="toolbar" shadow="hover">
            <el-row :gutter="20" align="middle">
              <el-col :span="12">
                <el-input
                  v-model="keyword"
                  placeholder="搜索游戏..."
                  prefix-icon="Search"
                  @input="handleSearch"
                  clearable
                  size="large"
                />
              </el-col>
              <el-col :span="6">
                <el-select v-model="sortBy" @change="applyFilters" size="large" style="width: 100%">
                  <el-option label="最新发布" value="latest" />
                  <el-option label="评分最高" value="rating" />
                  <el-option label="名称排序" value="name" />
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-radio-group v-model="viewMode" size="large">
                  <el-radio-button label="grid">
                    <el-icon><Grid /></el-icon>
                  </el-radio-button>
                  <el-radio-button label="list">
                    <el-icon><List /></el-icon>
                  </el-radio-button>
                </el-radio-group>
              </el-col>
            </el-row>
          </el-card>

          <!-- 游戏网格视图 -->
          <div v-if="viewMode === 'grid'" class="game-grid" v-loading="loading">
            <el-empty v-if="games.length === 0" description="没有找到相关游戏" />
            <el-row :gutter="20" v-else>
              <el-col :span="6" v-for="game in games" :key="game.id">
                <el-card class="game-card" shadow="hover" @click="$router.push(`/games/${game.id}`)">
                  <div class="game-cover-wrapper">
                    <img :src="game.cover_image || 'https://via.placeholder.com/300x200'" class="game-cover" />
                    <div class="game-badge" v-if="game.avg_score >= 9">
                      <el-tag type="danger" effect="dark">高分推荐</el-tag>
                    </div>
                  </div>
                  <div class="game-info">
                    <h3>{{ game.title }}</h3>
                    <el-tag size="small">{{ game.category_name }}</el-tag>
                    <div class="game-rating">
                      <el-rate v-model="game.display_score" disabled show-score :score-template="`${game.avg_score || 0}`" />
                      <span class="rating-count">({{ game.rating_count || 0 }})</span>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <!-- 游戏列表视图 -->
          <div v-else class="game-list-view" v-loading="loading">
            <el-empty v-if="games.length === 0" description="没有找到相关游戏" />
            <el-card v-for="game in games" :key="game.id" class="list-item" shadow="hover" @click="$router.push(`/games/${game.id}`)">
              <el-row :gutter="20">
                <el-col :span="4">
                  <img :src="game.cover_image || 'https://via.placeholder.com/200x150'" class="list-cover" />
                </el-col>
                <el-col :span="20">
                  <div class="list-content">
                    <div class="list-header">
                      <h3>{{ game.title }}</h3>
                      <el-tag>{{ game.category_name }}</el-tag>
                    </div>
                    <p class="list-desc">{{ game.description || '暂无描述' }}</p>
                    <div class="list-footer">
                      <div class="list-meta">
                        <span><el-icon><Calendar /></el-icon> {{ game.release_date || '未知' }}</span>
                        <span><el-icon><User /></el-icon> {{ game.developer || '未知' }}</span>
                      </div>
                      <div class="list-rating">
                        <el-rate v-model="game.display_score" disabled show-score :score-template="`${game.avg_score || 0}`" />
                        <span>({{ game.rating_count || 0 }} 评分)</span>
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </div>

          <!-- 分页 -->
          <div class="pagination-wrapper" v-if="total > 0">
            <el-pagination
              v-model:current-page="page"
              :page-size="perPage"
              :total="total"
              @current-change="handlePageChange"
              layout="prev, pager, next, jumper, total"
              background
            />
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'

const games = ref([])
const categories = ref([])
const selectedCategories = ref([])
const ratingRange = ref([0, 10])
const keyword = ref('')
const sortBy = ref('latest')
const viewMode = ref('grid')
const page = ref(1)
const perPage = ref(12)
const total = ref(0)
const loading = ref(false)

const fetchGames = async () => {
  loading.value = true
  try {
    const params = { 
      page: page.value, 
      per_page: perPage.value 
    }
    
    // 关键词搜索
    if (keyword.value) {
      params.keyword = keyword.value
    }
    
    // 分类筛选
    if (selectedCategories.value.length > 0) {
      params.categories = selectedCategories.value.join(',')
    }
    
    // 评分范围筛选
    if (ratingRange.value[0] > 0 || ratingRange.value[1] < 10) {
      params.min_rating = ratingRange.value[0]
      params.max_rating = ratingRange.value[1]
    }
    
    // 排序
    params.sort_by = sortBy.value
    
    const res = await api.get('/games', { params })
    games.value = res.data.games.map(game => ({
      ...game,
      display_score: (game.avg_score || 0) / 2
    }))
    total.value = res.data.total
  } catch (error) {
    console.error('获取游戏列表失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/games/categories')
    categories.value = res.data.categories
  } catch (error) {
    console.error(error)
  }
}

const applyFilters = () => {
  page.value = 1
  fetchGames()
}

const resetFilters = () => {
  selectedCategories.value = []
  ratingRange.value = [0, 10]
  keyword.value = ''
  sortBy.value = 'latest'
  applyFilters()
}

let searchTimer = null

const handleSearch = () => {
  // 使用防抖，避免频繁请求
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchGames()
  }, 500)
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchGames()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  fetchCategories()
  fetchGames()
})
</script>

<style scoped>
.game-library {
  background-color: #f5f7fa;
  min-height: calc(100vh - 64px);
}

.library-header {
  background: linear-gradient(135deg,#7117ea,#ea6060);
  color: white;
  padding: 60px 20px;
  text-align: center;
}

.library-header h1 {
  font-size: 42px;
  margin-bottom: 15px;
}

.library-header p {
  font-size: 18px;
  opacity: 0.9;
}

.content-wrapper {
  max-width: 1400px;
  margin: -40px auto 0;
  padding: 0 20px 40px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 25px;
}

.filter-section h4 {
  margin-bottom: 12px;
  font-size: 14px;
  color: #606266;
}

.filter-section .el-checkbox {
  display: block;
  margin: 8px 0;
}

.range-display {
  text-align: center;
  margin-top: 10px;
  color: #909399;
  font-size: 13px;
}

.toolbar {
  margin-bottom: 20px;
}

/* 网格视图 */
.game-grid {
  min-height: 600px;
}

.game-card {
  margin-bottom: 20px;
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

.game-info h3 {
  font-size: 15px;
  margin: 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.game-rating {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.rating-count {
  color: #909399;
  font-size: 12px;
}

/* 列表视图 */
.game-list-view {
  min-height: 600px;
}

.list-item {
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.list-item:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.list-cover {
  width: 100%;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
}

.list-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.list-header h3 {
  font-size: 18px;
  margin: 0;
}

.list-desc {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 10px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.list-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.list-meta {
  display: flex;
  gap: 20px;
  color: #909399;
  font-size: 13px;
}

.list-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.list-rating {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 30px;
  padding: 20px 0;
}
</style>
