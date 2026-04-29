<template>
  <div class="login-container">
    <!-- 左侧推广信息 -->
    <div class="promo-section">
      <div class="promo-content">
        <div class="logo-section">
          <el-icon :size="60" color="#fff"><Trophy /></el-icon>
          <h1>游戏评论平台</h1>
        </div>
        <div class="promo-features">
          <div class="feature-item">
            <el-icon :size="40"><Star /></el-icon>
            <h3>专业评分系统</h3>
            <p>多维度评分，帮你找到最适合的游戏</p>
          </div>
          <div class="feature-item">
            <el-icon :size="40"><ChatDotRound /></el-icon>
            <h3>真实玩家评论</h3>
            <p>来自真实玩家的游戏体验分享</p>
          </div>
          <div class="feature-item">
            <el-icon :size="40"><TrendCharts /></el-icon>
            <h3>热门游戏推荐</h3>
            <p>实时更新的游戏排行榜</p>
          </div>
        </div>
        <div class="promo-stats">
          <div class="stat-item">
            <div class="stat-number">1000+</div>
            <div class="stat-label">游戏收录</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">10000+</div>
            <div class="stat-label">用户评分</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">5000+</div>
            <div class="stat-label">玩家评论</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="form-section">
      <div class="form-wrapper">
        <div class="form-header">
          <h2>欢迎回来</h2>
          <p>登录您的账号，继续探索游戏世界</p>
        </div>

        <el-form :model="loginForm" :rules="rules" ref="formRef" class="login-form">
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              style="width: 100%"
              :loading="loading"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <span>还没有账号？</span>
          <el-button type="primary" link @click="$router.push('/register')">
            立即注册
          </el-button>
        </div>

        <div class="quick-links">
          <el-button link @click="$router.push('/')">
            <el-icon><HomeFilled /></el-icon>
            <span>返回首页</span>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock, Trophy, Star, ChatDotRound, TrendCharts, HomeFilled } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const loginForm = ref({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      await userStore.login(loginForm.value.username, loginForm.value.password)
      ElMessage.success('登录成功')
      
      // 根据用户角色跳转
      if (userStore.isAdmin) {
        router.push('/admin')
      } else {
        router.push('/')
      }
    } catch (error) {
      console.error('登录失败:', error)
      ElMessage.error(error.response?.data?.message || '登录失败，请检查用户名和密码')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
}

/* 左侧推广区域 */
.promo-section {
  flex: 1;
  background: #3498db;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: white;
}

.promo-content {
  max-width: 600px;
}

.logo-section {
  text-align: center;
  margin-bottom: 60px;
}

.logo-section h1 {
  font-size: 42px;
  margin: 20px 0 0 0;
  font-weight: bold;
}

.promo-features {
  display: flex;
  flex-direction: column;
  gap: 30px;
  margin-bottom: 60px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  transition: all 0.3s;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(10px);
}

.feature-item h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
}

.feature-item p {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.promo-stats {
  display: flex;
  justify-content: space-around;
  padding: 30px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

/* 右侧表单区域 */
.form-section {
  flex: 0 0 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: white;
}

.form-wrapper {
  width: 100%;
  max-width: 400px;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.form-header h2 {
  font-size: 32px;
  margin: 0 0 10px 0;
  color: #303133;
}

.form-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.login-form {
  margin-bottom: 20px;
}

.form-footer {
  text-align: center;
  padding: 20px 0;
  border-top: 1px solid #e4e7ed;
  color: #606266;
}

.quick-links {
  text-align: center;
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .promo-section {
    display: none;
  }
  
  .form-section {
    flex: 1;
  }
}
</style>
