<template>
  <div class="announcements-page">
    <div class="page-header">
      <h1>系统公告</h1>
      <p>了解平台最新动态和重要通知</p>
    </div>

    <!-- 筛选 -->
    <el-card shadow="never" style="margin-bottom: 20px">
      <el-radio-group v-model="typeFilter" @change="handleFilterChange">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="system">系统公告</el-radio-button>
        <el-radio-button label="event">活动公告</el-radio-button>
        <el-radio-button label="maintenance">维护公告</el-radio-button>
        <el-radio-button label="update">更新公告</el-radio-button>
      </el-radio-group>
    </el-card>

    <!-- 公告列表 -->
    <div v-loading="loading">
      <el-empty v-if="!loading && announcements.length === 0" description="暂无公告" />
      
      <el-card
        v-for="announcement in announcements"
        :key="announcement.id"
        shadow="hover"
        style="margin-bottom: 20px; cursor: pointer"
        @click="handleView(announcement)"
      >
        <div class="announcement-item">
          <div class="announcement-header">
            <div class="announcement-title">
              <el-tag :type="getTypeColor(announcement.type)" size="small" style="margin-right: 10px">
                {{ getTypeName(announcement.type) }}
              </el-tag>
              <span>{{ announcement.title }}</span>
            </div>
            <div class="announcement-time">
              {{ formatDate(announcement.publish_time) }}
            </div>
          </div>
          <div class="announcement-content">
            {{ announcement.content.substring(0, 150) }}{{ announcement.content.length > 150 ? '...' : '' }}
          </div>
        </div>
      </el-card>

      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        :current-page="page"
        :page-size="perPage"
        :total="total"
        @current-change="handlePageChange"
        layout="prev, pager, next, total"
        style="margin-top: 20px; justify-content: center"
      />
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="currentAnnouncement?.title"
      width="700px"
    >
      <div v-if="currentAnnouncement" class="announcement-detail">
        <div class="detail-meta">
          <el-tag :type="getTypeColor(currentAnnouncement.type)" size="small">
            {{ getTypeName(currentAnnouncement.type) }}
          </el-tag>
          <span class="detail-time">{{ formatDate(currentAnnouncement.publish_time) }}</span>
        </div>
        <div class="detail-content">
          {{ currentAnnouncement.content }}
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

const announcements = ref([])
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const loading = ref(false)
const typeFilter = ref('')
const showDetailDialog = ref(false)
const currentAnnouncement = ref(null)

const fetchAnnouncements = async () => {
  loading.value = true
  try {
    const res = await api.get('/announcements', {
      params: {
        page: page.value,
        per_page: perPage.value,
        type: typeFilter.value
      }
    })
    announcements.value = res.data.announcements
    total.value = res.data.total
  } catch (error) {
    console.error('获取公告列表失败:', error)
    ElMessage.error('获取公告列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  page.value = 1
  fetchAnnouncements()
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchAnnouncements()
}

const handleView = (announcement) => {
  currentAnnouncement.value = announcement
  showDetailDialog.value = true
}

const getTypeName = (type) => {
  const map = {
    system: '系统公告',
    event: '活动公告',
    maintenance: '维护公告',
    update: '更新公告'
  }
  return map[type] || type
}

const getTypeColor = (type) => {
  const map = {
    system: 'info',
    event: 'success',
    maintenance: 'warning',
    update: 'primary'
  }
  return map[type] || ''
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<style scoped>
.announcements-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 32px;
  margin: 0 0 10px 0;
  color: #303133;
}

.page-header p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.announcement-item {
  padding: 10px 0;
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.announcement-title {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.announcement-time {
  font-size: 14px;
  color: #909399;
}

.announcement-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.announcement-detail {
  padding: 10px 0;
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.detail-time {
  font-size: 14px;
  color: #909399;
}

.detail-content {
  font-size: 15px;
  color: #303133;
  line-height: 1.8;
  white-space: pre-wrap;
}
</style>
