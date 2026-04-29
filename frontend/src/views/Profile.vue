<template>
  <div class="profile-container">
    <div class="profile">
      <el-card class="profile-card">
        <template #header>
          <div class="card-header">
            <h2>个人信息</h2>
            <el-tag v-if="userStore.user?.role === 'admin'" type="danger">管理员</el-tag>
          </div>
        </template>

        <el-form :model="form" label-width="100px" class="profile-form">
          <!-- 头像预览 -->
          <el-form-item label="当前头像">
            <div class="avatar-preview">
              <el-avatar :size="100" :src="form.avatar || undefined">
                {{ form.username?.charAt(0) }}
              </el-avatar>
            </div>
          </el-form-item>

          <!-- 用户名 -->
          <el-form-item label="用户名">
            <el-input v-model="form.username" disabled>
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <!-- 邮箱 -->
          <el-form-item label="邮箱">
            <el-input v-model="form.email" type="email">
              <template #prefix>
                <el-icon><Message /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <!-- 头像设置 -->
          <el-form-item label="头像设置">
            <el-radio-group v-model="avatarMode" class="avatar-mode-group">
              <el-radio label="url">在线图片地址</el-radio>
              <el-radio label="upload">上传图片</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 在线图片地址 -->
          <el-form-item v-if="avatarMode === 'url'" label="图片地址">
            <el-input 
              v-model="form.avatar" 
              placeholder="请输入图片URL，例如：https://example.com/avatar.jpg"
            >
              <template #prefix>
                <el-icon><Picture /></el-icon>
              </template>
            </el-input>
            <div class="form-tip">
              支持常见图片格式（jpg, png, gif等），建议使用正方形图片
            </div>
          </el-form-item>

          <!-- 上传图片 -->
          <el-form-item v-if="avatarMode === 'upload'" label="上传图片">
            <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :http-request="handleAvatarUpload"
              accept="image/*"
            >
              <el-button type="primary">
                <el-icon><Upload /></el-icon>
                选择图片
              </el-button>
            </el-upload>
            <div class="form-tip">
              支持 jpg、png、gif 格式，文件大小不超过 2MB
            </div>
            <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
              <el-progress :percentage="uploadProgress" />
            </div>
          </el-form-item>

          <!-- 修改密码 -->
          <el-form-item label="新密码">
            <el-input 
              v-model="form.password" 
              type="password" 
              placeholder="不修改请留空"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
            <div class="form-tip">
              留空表示不修改密码
            </div>
          </el-form-item>

          <!-- 确认密码 -->
          <el-form-item v-if="form.password" label="确认密码">
            <el-input 
              v-model="form.confirmPassword" 
              type="password" 
              placeholder="请再次输入新密码"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <!-- 按钮 -->
          <el-form-item>
            <el-button type="primary" @click="updateProfile" :loading="saving">
              保存修改
            </el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 账号统计 -->
      <el-card class="stats-card">
        <template #header>
          <h3>账号统计</h3>
        </template>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-icon">
              <el-icon :size="32"><Star /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.ratings }}</div>
              <div class="stat-label">评分数</div>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon">
              <el-icon :size="32"><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.comments }}</div>
              <div class="stat-label">评论数</div>
            </div>
          </div>
          <div class="stat-item stat-item-full">
            <div class="stat-icon">
              <el-icon :size="32"><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ formatDate(userStore.user?.created_at) }}</div>
              <div class="stat-label">注册时间</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'
import { User, Message, Picture, Upload, Lock, Star, ChatDotRound, Calendar } from '@element-plus/icons-vue'

const userStore = useUserStore()

const form = ref({
  username: '',
  email: '',
  avatar: '',
  password: '',
  confirmPassword: ''
})

const avatarMode = ref('url') // 'url' 或 'upload'
const saving = ref(false)
const uploadProgress = ref(0)

const stats = ref({
  ratings: 0,
  comments: 0
})

const loadProfile = () => {
  if (userStore.user) {
    form.value.username = userStore.user.username
    form.value.email = userStore.user.email
    form.value.avatar = userStore.user.avatar || ''
  }
}

const loadStats = async () => {
  try {
    // 获取评分数
    const ratingsRes = await api.get('/ratings/my/all')
    stats.value.ratings = ratingsRes.data.total || 0
    
    // 获取评论数
    const commentsRes = await api.get('/comments/my/stats')
    stats.value.comments = commentsRes.data.total || 0
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const beforeAvatarUpload = (file) => {
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

const handleAvatarUpload = async (options) => {
  const { file } = options
  
  try {
    uploadProgress.value = 0
    
    // 将图片转换为 Base64
    const reader = new FileReader()
    reader.onload = (e) => {
      form.value.avatar = e.target.result
      uploadProgress.value = 100
      ElMessage.success('图片加载成功')
      
      // 2秒后隐藏进度条
      setTimeout(() => {
        uploadProgress.value = 0
      }, 2000)
    }
    reader.onerror = () => {
      ElMessage.error('图片读取失败')
      uploadProgress.value = 0
    }
    reader.onprogress = (e) => {
      if (e.lengthComputable) {
        uploadProgress.value = Math.round((e.loaded / e.total) * 100)
      }
    }
    reader.readAsDataURL(file)
  } catch (error) {
    ElMessage.error('图片上传失败')
    uploadProgress.value = 0
  }
}

const updateProfile = async () => {
  // 验证密码
  if (form.value.password && form.value.password !== form.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  saving.value = true
  try {
    const data = {
      email: form.value.email,
      avatar: form.value.avatar
    }
    if (form.value.password) {
      data.password = form.value.password
    }
    
    await api.put('/users/profile', data)
    ElMessage.success('更新成功')
    await userStore.fetchProfile()
    form.value.password = ''
    form.value.confirmPassword = ''
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error('更新失败')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  loadProfile()
  form.value.password = ''
  form.value.confirmPassword = ''
  uploadProgress.value = 0
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadProfile()
  loadStats()
})
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
  min-height: calc(100vh - 200px);
}

.profile {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 30px;
  align-items: start;
}

.profile-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.profile-form {
  padding: 20px 0;
}

.avatar-preview {
  display: flex;
  justify-content: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.avatar-mode-group {
  width: 100%;
}

.form-tip {
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.avatar-uploader {
  margin-bottom: 10px;
}

.upload-progress {
  margin-top: 15px;
}

.stats-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 20px;
}

.stats-card h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.stats-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 10px 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: linear-gradient(135deg,#7117ea,#ea6060);
  border-radius: 12px;
  color: white;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.stat-item-full {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 4px;
  line-height: 1;
  word-break: break-all;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

@media (max-width: 992px) {
  .profile {
    grid-template-columns: 1fr;
  }
  
  .stats-card {
    position: static;
  }
  
  .stats-grid {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .stat-item {
    flex: 1;
    min-width: calc(50% - 8px);
  }
  
  .stat-item-full {
    flex-basis: 100%;
  }
}

@media (max-width: 768px) {
  .profile-container {
    padding: 20px 15px;
  }
  
  .stats-grid {
    flex-direction: column;
  }
  
  .stat-item {
    min-width: 100%;
  }
}
</style>
