<template>
  <div class="admin-games">
    <div class="page-header">
      <h2>游戏管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        <span>添加游戏</span>
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card shadow="never" style="margin-bottom: 20px">
      <el-form :inline="true">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="游戏名称或开发商"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.category_id" placeholder="全部" clearable @change="handleSearch" style="width:120px">
            <el-option label="全部" :value="null" />
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable @change="handleSearch" style="width:120px">
            <el-option label="全部" value="" />
            <el-option label="已发布" value="published" />
            <el-option label="草稿" value="draft" />
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
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 游戏列表 -->
    <el-card shadow="never">
      <el-table :data="games" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="封面" width="100">
          <template #default="{ row }">
            <el-image
              v-if="row.cover_image"
              :src="getFullImageUrl(row.cover_image)"
              :preview-src-list="[getFullImageUrl(row.cover_image)]"
              fit="cover"
              style="width: 60px; height: 40px; border-radius: 4px"
            />
            <span v-else style="color: #909399">无封面</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="游戏名称"/>
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column prop="developer" label="开发商" width="150" />
        <el-table-column prop="publisher" label="发行商" width="150" />
        <el-table-column prop="release_date" label="发行日期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : 'info'">
              {{ row.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right">
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

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="editingGame ? '编辑游戏' : '添加游戏'"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
        <el-form-item label="游戏名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入游戏名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="开发商" prop="developer">
          <el-input v-model="form.developer" placeholder="请输入开发商" />
        </el-form-item>
        <el-form-item label="发行商">
          <el-input v-model="form.publisher" placeholder="请输入发行商" />
        </el-form-item>
        <el-form-item label="发行日期">
          <el-date-picker
            v-model="form.release_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="封面图">
          <el-radio-group v-model="imageType" style="margin-bottom: 10px">
            <el-radio label="url">在线地址</el-radio>
            <el-radio label="upload">本地上传</el-radio>
          </el-radio-group>
          <el-input
            v-if="imageType === 'url'"
            v-model="form.cover_image"
            placeholder="请输入图片URL"
          />
          <el-upload
            v-else
            class="avatar-uploader"
            :show-file-list="false"
            :before-upload="beforeImageUpload"
            :http-request="handleImageUpload"
          >
            <img v-if="form.cover_image" :src="getFullImageUrl(form.cover_image)" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div v-if="form.cover_image" style="margin-top: 10px">
            <el-image :src="getFullImageUrl(form.cover_image)" style="width: 200px; height: 120px" fit="cover" />
          </div>
        </el-form-item>
        <el-form-item label="游戏图集">
          <el-radio-group v-model="galleryType" style="margin-bottom: 10px">
            <el-radio label="url">在线地址</el-radio>
            <el-radio label="upload">本地上传</el-radio>
          </el-radio-group>
          
          <!-- 在线地址方式 -->
          <div v-if="galleryType === 'url'">
            <div v-for="(img, index) in form.images" :key="index" style="margin-bottom: 10px; display: flex; gap: 10px">
              <el-input v-model="form.images[index]" placeholder="请输入图片URL" />
              <el-button type="danger" @click="removeGalleryImage(index)">删除</el-button>
            </div>
            <el-button @click="addGalleryImageUrl" style="width: 100%">+ 添加图片</el-button>
          </div>
          
          <!-- 本地上传方式 -->
          <div v-else>
            <el-upload
              :file-list="galleryFileList"
              list-type="picture-card"
              :before-upload="beforeGalleryUpload"
              :http-request="handleGalleryUpload"
              :on-remove="handleGalleryRemove"
              multiple
            >
              <el-icon><Plus /></el-icon>
            </el-upload>
          </div>
          
          <!-- 图集预览 -->
          <div v-if="form.images && form.images.length > 0" style="margin-top: 10px">
            <div style="display: flex; flex-wrap: wrap; gap: 10px">
              <el-image
                v-for="(img, index) in form.images"
                :key="index"
                :src="getFullImageUrl(img)"
                style="width: 100px; height: 60px"
                fit="cover"
                :preview-src-list="form.images.map(i => getFullImageUrl(i))"
                :initial-index="index"
              />
            </div>
          </div>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入游戏描述"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="已发布" value="published" />
            <el-option label="草稿" value="draft" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="游戏详情" width="600px">
      <el-descriptions :column="2" border v-if="currentGame">
        <el-descriptions-item label="ID">{{ currentGame.id }}</el-descriptions-item>
        <el-descriptions-item label="游戏名称">{{ currentGame.title }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ currentGame.category_name }}</el-descriptions-item>
        <el-descriptions-item label="开发商">{{ currentGame.developer }}</el-descriptions-item>
        <el-descriptions-item label="发行商">{{ currentGame.publisher || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="发行日期">{{ currentGame.release_date || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentGame.status === 'published' ? 'success' : 'info'">
            {{ currentGame.status === 'published' ? '已发布' : '草稿' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="平均评分">
          {{ currentGame.avg_score ? Number(currentGame.avg_score).toFixed(1) : '暂无评分' }}
        </el-descriptions-item>
        <el-descriptions-item label="封面图" :span="2">
          <el-image
            v-if="currentGame.cover_image"
            :src="getFullImageUrl(currentGame.cover_image)"
            style="width: 300px; height: 180px"
            fit="cover"
          />
          <span v-else>无封面</span>
        </el-descriptions-item>
        <el-descriptions-item label="游戏图集" :span="2">
          <div v-if="currentGame.images && currentGame.images.length > 0" style="display: flex; flex-wrap: wrap; gap: 10px">
            <el-image
              v-for="(img, index) in currentGame.images"
              :key="index"
              :src="getFullImageUrl(img)"
              style="width: 120px; height: 80px"
              fit="cover"
              :preview-src-list="currentGame.images.map(i => getFullImageUrl(i))"
              :initial-index="index"
            />
          </div>
          <span v-else>暂无图集</span>
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">
          {{ currentGame.description || '暂无描述' }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">
          {{ formatDate(currentGame.created_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/utils/api'
import { getImageUrl } from '@/utils/image'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'

const games = ref([])
const categories = ref([])
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const loading = ref(false)
const saving = ref(false)

const searchForm = ref({
  keyword: '',
  category_id: null,
  status: ''
})

const showDialog = ref(false)
const showDetailDialog = ref(false)
const editingGame = ref(null)
const currentGame = ref(null)
const imageType = ref('url')
const galleryType = ref('url')
const galleryFileList = ref([])
const formRef = ref(null)

const form = ref({
  title: '',
  category_id: null,
  developer: '',
  publisher: '',
  release_date: '',
  cover_image: '',
  images: [],
  description: '',
  status: 'published'
})

const rules = {
  title: [{ required: true, message: '请输入游戏名称', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  developer: [{ required: true, message: '请输入开发商', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const fetchGames = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      per_page: perPage.value
    }
    
    if (searchForm.value.keyword) {
      params.keyword = searchForm.value.keyword
    }
    if (searchForm.value.category_id) {
      params.categories = searchForm.value.category_id
    }
    if (searchForm.value.status) {
      // 需要后端支持status筛选
      params.status = searchForm.value.status
    }
    
    const res = await api.get('/games', { params })
    games.value = res.data.games
    total.value = res.data.total
  } catch (error) {
    console.error('获取游戏列表失败:', error)
    ElMessage.error('获取游戏列表失败')
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/games/categories')
    categories.value = res.data.categories
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

const handleAdd = () => {
  editingGame.value = null
  form.value = {
    title: '',
    category_id: null,
    developer: '',
    publisher: '',
    release_date: '',
    cover_image: '',
    images: [],
    description: '',
    status: 'published'
  }
  imageType.value = 'url'
  galleryType.value = 'url'
  galleryFileList.value = []
  showDialog.value = true
}

const handleEdit = (game) => {
  editingGame.value = game
  form.value = { 
    ...game,
    images: game.images || []
  }
  imageType.value = 'url'
  galleryType.value = 'url'
  galleryFileList.value = []
  showDialog.value = true
}

const handleView = (game) => {
  currentGame.value = game
  showDetailDialog.value = true
}

const handleSave = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    try {
      if (editingGame.value) {
        await api.put(`/games/${editingGame.value.id}`, form.value)
        ElMessage.success('更新成功')
      } else {
        await api.post('/games', form.value)
        ElMessage.success('添加成功')
      }
      showDialog.value = false
      fetchGames()
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
    await ElMessageBox.confirm('确定要删除该游戏吗？删除后无法恢复！', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/games/${id}`)
    ElMessage.success('删除成功')
    fetchGames()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleSearch = () => {
  page.value = 1
  fetchGames()
}

const handleReset = () => {
  searchForm.value = {
    keyword: '',
    category_id: null,
    status: ''
  }
  page.value = 1
  fetchGames()
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchGames()
}

const handleSizeChange = (newSize) => {
  perPage.value = newSize
  page.value = 1
  fetchGames()
}

const handleDialogClose = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const beforeImageUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB!')
    return false
  }
  return true
}

const handleImageUpload = async (options) => {
  const file = options.file
  
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const res = await api.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    form.value.cover_image = res.data.url
    ElMessage.success('图片上传成功')
  } catch (error) {
    console.error('图片上传失败:', error)
    ElMessage.error('图片上传失败')
  }
}

// 图集管理函数
const addGalleryImageUrl = () => {
  if (!form.value.images) {
    form.value.images = []
  }
  form.value.images.push('')
}

const removeGalleryImage = (index) => {
  form.value.images.splice(index, 1)
}

const beforeGalleryUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB!')
    return false
  }
  return true
}

const handleGalleryUpload = async (options) => {
  const file = options.file
  
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const res = await api.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (!form.value.images) {
      form.value.images = []
    }
    form.value.images.push(res.data.url)
    galleryFileList.value.push({
      name: file.name,
      url: res.data.url
    })
    
    ElMessage.success('图片上传成功')
  } catch (error) {
    console.error('图片上传失败:', error)
    ElMessage.error('图片上传失败')
  }
}

const handleGalleryRemove = (file) => {
  const index = galleryFileList.value.findIndex(f => f.url === file.url)
  if (index > -1) {
    form.value.images.splice(index, 1)
    galleryFileList.value.splice(index, 1)
  }
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

// 获取完整的图片 URL
const getFullImageUrl = (path) => {
  return getImageUrl(path)
}

onMounted(() => {
  fetchGames()
  fetchCategories()
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

.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}

.avatar-uploader:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
  line-height: 178px;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
  object-fit: cover;
}
</style>
