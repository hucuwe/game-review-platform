<template>
  <div class="admin-comments">
    <h2>评论管理</h2>
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="正常评论" name="normal" />
      <el-tab-pane label="已举报" name="reported" />
      <el-tab-pane label="已删除" name="deleted" />
    </el-tabs>
    
    <el-table :data="comments" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户" width="120" />
      <el-table-column prop="game_title" label="游戏" width="150" />
      <el-table-column prop="content" label="评论内容" show-overflow-tooltip />
      <el-table-column prop="likes_count" label="点赞数" width="100" />
      <el-table-column prop="created_at" label="发布时间" width="180" />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" @click="handleView(row)">查看</el-button>
          <el-button
            v-if="row.status !== 'deleted'"
            size="small"
            type="danger"
            @click="deleteComment(row.id)"
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

    <!-- 评论详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="评论详情" width="600px">
      <el-descriptions :column="2" border v-if="currentComment">
        <el-descriptions-item label="评论ID">{{ currentComment.id }}</el-descriptions-item>
        <el-descriptions-item label="用户">{{ currentComment.username }}</el-descriptions-item>
        <el-descriptions-item label="游戏">{{ currentComment.game_title }}</el-descriptions-item>
        <el-descriptions-item label="点赞数">{{ currentComment.likes_count }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentComment.status === 'normal' ? 'success' : currentComment.status === 'reported' ? 'warning' : 'danger'">
            {{ currentComment.status === 'normal' ? '正常' : currentComment.status === 'reported' ? '已举报' : '已删除' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发布时间">
          {{ currentComment.created_at }}
        </el-descriptions-item>
        <el-descriptions-item label="评论内容" :span="2">
          <div style="white-space: pre-wrap; line-height: 1.6">{{ currentComment.content }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const comments = ref([])
const activeTab = ref('normal')
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const showDetailDialog = ref(false)
const currentComment = ref(null)

const fetchComments = async () => {
  try {
    const res = await api.get('/admin/comments', {
      params: {
        page: page.value,
        per_page: perPage.value,
        status: activeTab.value
      }
    })
    comments.value = res.data.comments.map(comment => ({
      ...comment,
      created_at: formatDateTime(comment.created_at)
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
  fetchComments()
}

const deleteComment = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该评论吗？', '提示')
    await api.delete(`/comments/${id}`)
    ElMessage.success('删除成功')
    fetchComments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleView = (comment) => {
  currentComment.value = comment
  showDetailDialog.value = true
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchComments()
}

onMounted(() => {
  fetchComments()
})
</script>

<style scoped>
.admin-comments h2 {
  margin-bottom: 20px;
}
</style>
