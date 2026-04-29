<template>
  <div class="admin-announcements">
    <div class="page-header">
      <h2>公告管理</h2>
    </div>

    <!-- 搜索和筛选 -->
    <el-card shadow="never" style="margin-bottom: 20px">
      <el-form :inline="true">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="标题或内容"
            clearable
            @clear="handleSearch"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable @change="handleSearch" style="width:120px;">
            <el-option label="全部" value="" />
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            <span>搜索</span>
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            <span>重置</span>
          </el-button>
          <el-button type="success" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            <span>新增公告</span>
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 公告列表 -->
    <el-card shadow="never">
      <el-table :data="announcements" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.type)">
              {{ getTypeName(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publish_time" label="发布时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.publish_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        :current-page="page"
        :page-size="perPage"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="showFormDialog"
      :title="formMode === 'add' ? '新增公告' : '编辑公告'"
      width="700px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="公告标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公告标题" />
        </el-form-item>
        <el-form-item label="公告类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="系统公告" value="system" />
            <el-option label="活动公告" value="event" />
            <el-option label="维护公告" value="maintenance" />
            <el-option label="更新公告" value="update" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="form.priority" :min="0" :max="100" />
          <span style="margin-left: 10px; color: #909399; font-size: 12px">数字越大优先级越高</span>
        </el-form-item>
        <el-form-item label="公告内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="6"
            placeholder="请输入公告内容"
          />
        </el-form-item>
        <el-form-item label="发布时间" prop="publish_time">
          <el-date-picker
            v-model="form.publish_time"
            type="datetime"
            placeholder="选择发布时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="published">发布</el-radio>
            <el-radio label="archived">归档</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFormDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="公告详情" width="700px">
      <el-descriptions :column="2" border v-if="currentAnnouncement">
        <el-descriptions-item label="ID">{{ currentAnnouncement.id }}</el-descriptions-item>
        <el-descriptions-item label="标题">{{ currentAnnouncement.title }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :type="getTypeColor(currentAnnouncement.type)">
            {{ getTypeName(currentAnnouncement.type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="优先级">{{ currentAnnouncement.priority }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusColor(currentAnnouncement.status)">
            {{ getStatusName(currentAnnouncement.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发布时间">
          {{ formatDate(currentAnnouncement.publish_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(currentAnnouncement.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatDate(currentAnnouncement.updated_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="内容" :span="2">
          <div style="white-space: pre-wrap">{{ currentAnnouncement.content }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'

const announcements = ref([])
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const loading = ref(false)
const showFormDialog = ref(false)
const showDetailDialog = ref(false)
const formMode = ref('add')
const submitLoading = ref(false)
const formRef = ref()
const currentAnnouncement = ref(null)

const searchForm = ref({
  keyword: '',
  status: ''
})

const form = ref({
  title: '',
  content: '',
  type: 'system',
  priority: 0,
  status: 'draft',
  publish_time: null
})

const rules = {
  title: [{ required: true, message: '请输入公告标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入公告内容', trigger: 'blur' }],
  type: [{ required: true, message: '请选择公告类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const fetchAnnouncements = async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/announcements', {
      params: {
        page: page.value,
        per_page: perPage.value,
        keyword: searchForm.value.keyword,
        status: searchForm.value.status
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

const handleAdd = () => {
  formMode.value = 'add'
  form.value = {
    title: '',
    content: '',
    type: 'system',
    priority: 0,
    status: 'draft',
    publish_time: null
  }
  showFormDialog.value = true
}

const handleEdit = (row) => {
  formMode.value = 'edit'
  form.value = {
    id: row.id,
    title: row.title,
    content: row.content,
    type: row.type,
    priority: row.priority,
    status: row.status,
    publish_time: row.publish_time
  }
  showFormDialog.value = true
}

const handleView = (row) => {
  currentAnnouncement.value = row
  showDetailDialog.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    if (formMode.value === 'add') {
      await api.post('/admin/announcements', form.value)
      ElMessage.success('创建成功')
    } else {
      await api.put(`/admin/announcements/${form.value.id}`, form.value)
      ElMessage.success('更新成功')
    }
    showFormDialog.value = false
    fetchAnnouncements()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该公告吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.delete(`/admin/announcements/${id}`)
    ElMessage.success('删除成功')
    fetchAnnouncements()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleSearch = () => {
  page.value = 1
  fetchAnnouncements()
}

const handleReset = () => {
  searchForm.value = {
    keyword: '',
    status: ''
  }
  page.value = 1
  fetchAnnouncements()
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchAnnouncements()
}

const handleSizeChange = (newSize) => {
  perPage.value = newSize
  page.value = 1
  fetchAnnouncements()
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

const getStatusName = (status) => {
  const map = {
    draft: '草稿',
    published: '已发布',
    archived: '已归档'
  }
  return map[status] || status
}

const getStatusColor = (status) => {
  const map = {
    draft: 'info',
    published: 'success',
    archived: 'warning'
  }
  return map[status] || ''
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}
</style>
