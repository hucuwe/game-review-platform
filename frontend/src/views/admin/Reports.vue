<template>
  <div class="admin-reports">
    <h2>举报管理</h2>
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="待处理" name="pending" />
      <el-tab-pane label="已处理" name="processed" />
      <el-tab-pane label="已驳回" name="rejected" />
    </el-tabs>
    
    <el-table :data="reports" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="举报人" />
      <el-table-column label="被举报评论">
        <template #default="{ row }">
          {{ row.comment?.content || '评论已删除' }}
        </template>
      </el-table-column>
      <el-table-column prop="reason" label="举报理由" />
      <el-table-column prop="created_at" label="举报时间" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button size="small" @click="handleView(row)">查看</el-button>
          <el-button
            v-if="row.status === 'pending'"
            size="small"
            type="success"
            @click="processReport(row.id, 'approve')"
          >
            通过
          </el-button>
          <el-button
            v-if="row.status === 'pending'"
            size="small"
            type="warning"
            @click="processReport(row.id, 'reject')"
          >
            驳回
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(row.id)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-pagination
      v-if="total > 0"
      :current-page="page"
      :page-size="perPage"
      :total="total"
      @current-change="handlePageChange"
      layout="prev, pager, next, total"
      style="margin-top: 20px"
    />

    <!-- 举报详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="举报详情" width="600px">
      <el-descriptions :column="2" border v-if="currentReport">
        <el-descriptions-item label="举报ID">{{ currentReport.id }}</el-descriptions-item>
        <el-descriptions-item label="举报人">{{ currentReport.username }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentReport.status === 'pending' ? 'warning' : currentReport.status === 'processed' ? 'success' : 'info'">
            {{ currentReport.status === 'pending' ? '待处理' : currentReport.status === 'processed' ? '已处理' : '已驳回' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="举报时间">
          {{ currentReport.created_at }}
        </el-descriptions-item>
        <el-descriptions-item label="举报理由" :span="2">
          <div style="white-space: pre-wrap; line-height: 1.6">{{ currentReport.reason || '无' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="被举报评论" :span="2" v-if="currentReport.comment">
          <el-card shadow="never" style="background: #f5f7fa">
            <div><strong>评论内容：</strong>{{ currentReport.comment.content }}</div>
            <div style="margin-top: 10px; color: #909399; font-size: 12px">
              <span>评论人：{{ currentReport.comment.username }}</span>
              <span style="margin-left: 20px">点赞数：{{ currentReport.comment.likes_count }}</span>
            </div>
          </el-card>
        </el-descriptions-item>
        <el-descriptions-item label="被举报评论" :span="2" v-else>
          <el-tag type="info">评论已删除</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const reports = ref([])
const activeTab = ref('pending')
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const showDetailDialog = ref(false)
const currentReport = ref(null)

const fetchReports = async () => {
  try {
    const res = await api.get('/admin/reports', {
      params: {
        page: page.value,
        per_page: perPage.value,
        status: activeTab.value
      }
    })
    reports.value = res.data.reports.map(report => ({
      ...report,
      created_at: formatDateTime(report.created_at),
      processed_at: formatDateTime(report.processed_at)
    }))
    total.value = res.data.total
  } catch (error) {
    console.error(error)
  }
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

const handleTabChange = () => {
  page.value = 1
  fetchReports()
}

const processReport = async (id, action) => {
  try {
    await api.post(`/admin/reports/${id}/process`, { action })
    ElMessage.success(action === 'approve' ? '已通过举报' : '已驳回举报')
    fetchReports()
  } catch (error) {
    console.error(error)
  }
}

const handleView = (report) => {
  currentReport.value = report
  showDetailDialog.value = true
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该举报记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/admin/reports/${id}`)
    ElMessage.success('删除成功')
    fetchReports()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchReports()
}

onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
.admin-reports h2 {
  margin-bottom: 20px;
}
</style>
