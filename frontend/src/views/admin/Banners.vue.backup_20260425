<template>
  <div class="admin-banners">
    <div class="page-header">
      <h2>轮播图管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        <span>添加轮播图</span>
      </el-button>
    </div>

    <!-- 轮播图列表 -->
    <el-card shadow="never">
      <el-table :data="banners" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="预览" width="200">
          <template #default="{ row }">
            <el-image
              :src="row.image_url"
              :preview-src-list="[row.image_url]"
              fit="cover"
              style="width: 160px; height: 60px; border-radius: 4px"
            />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" width="200" />
        <el-table-column prop="link_url" label="跳转链接" show-overflow-tooltip />
        <el-table-column prop="sort_order" label="排序" width="100" sortable />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
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
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="editingBanner ? '编辑轮播图' : '添加轮播图'"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="图片">
          <el-radio-group v-model="imageType" style="margin-bottom: 10px">
            <el-radio label="url">在线地址</el-radio>
            <el-radio label="upload">本地上传</el-radio>
          </el-radio-group>
          <el-input
            v-if="imageType === 'url'"
            v-model="form.image_url"
            placeholder="请输入图片URL（建议尺寸：1920x500）"
          />
          <el-upload
            v-else
            class="banner-uploader"
            :show-file-list="false"
            :before-upload="beforeImageUpload"
            :http-request="handleImageUpload"
          >
            <img v-if="form.image_url" :src="form.image_url" class="banner-image" />
            <el-icon v-else class="banner-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div v-if="form.image_url" style="margin-top: 10px">
            <el-image :src="form.image_url" style="width: 400px; height: 120px" fit="cover" />
          </div>
        </el-form-item>
        <el-form-item label="跳转链接">
          <el-input v-model="form.link_url" placeholder="例如：/games 或 /hot" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px">
            数字越小越靠前
          </div>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="轮播图详情" width="700px">
      <el-descriptions :column="2" border v-if="currentBanner">
        <el-descriptions-item label="ID">{{ currentBanner.id }}</el-descriptions-item>
        <el-descriptions-item label="标题">{{ currentBanner.title }}</el-descriptions-item>
        <el-descriptions-item label="跳转链接">{{ currentBanner.link_url || '无' }}</el-descriptions-item>
        <el-descriptions-item label="排序">{{ currentBanner.sort_order }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentBanner.status === 'active' ? 'success' : 'info'">
            {{ currentBanner.status === 'active' ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(currentBanner.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="图片" :span="2">
          <el-image
            :src="currentBanner.image_url"
            style="width: 100%; max-width: 600px"
            fit="cover"
          />
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">
          {{ currentBanner.description || '无' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const banners = ref([])
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const showDetailDialog = ref(false)
const editingBanner = ref(null)
const currentBanner = ref(null)
const imageType = ref('url')
const formRef = ref(null)

const form = ref({
  title: '',
  image_url: '',
  link_url: '',
  description: '',
  sort_order: 0,
  status: 'active'
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  sort_order: [{ required: true, message: '请输入排序', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const fetchBanners = async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/banners')
    banners.value = res.data.banners
  } catch (error) {
    console.error('获取轮播图列表失败:', error)
    ElMessage.error('获取轮播图列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  editingBanner.value = null
  form.value = {
    title: '',
    image_url: '',
    link_url: '',
    description: '',
    sort_order: 0,
    status: 'active'
  }
  imageType.value = 'url'
  showDialog.value = true
}

const handleEdit = (banner) => {
  editingBanner.value = banner
  form.value = { ...banner }
  imageType.value = 'url'
  showDialog.value = true
}

const handleView = (banner) => {
  currentBanner.value = banner
  showDetailDialog.value = true
}

const handleSave = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    if (!form.value.image_url) {
      ElMessage.error('请上传图片或输入图片地址')
      return
    }
    
    saving.value = true
    try {
      if (editingBanner.value) {
        await api.put(`/admin/banners/${editingBanner.value.id}`, form.value)
        ElMessage.success('更新成功')
      } else {
        await api.post('/admin/banners', form.value)
        ElMessage.success('添加成功')
      }
      showDialog.value = false
      fetchBanners()
    } catch (error) {
      console.error('保存失败:', error)
      ElMessage.error('保存失败')
    } finally {
      saving.value = false
    }
  })
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该轮播图吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/admin/banners/${id}`)
    ElMessage.success('删除成功')
    fetchBanners()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleDialogClose = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const beforeImageUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

const handleImageUpload = (options) => {
  const file = options.file
  const reader = new FileReader()
  
  reader.onload = (e) => {
    form.value.image_url = e.target.result
  }
  
  reader.readAsDataURL(file)
}

const formatDate = (dateStr) => {
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

onMounted(() => {
  fetchBanners()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.banner-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}

.banner-uploader:hover {
  border-color: #409eff;
}

.banner-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 400px;
  height: 120px;
  text-align: center;
  line-height: 120px;
}

.banner-image {
  width: 400px;
  height: 120px;
  display: block;
  object-fit: cover;
}
</style>
