<template>
  <div class="register-page">
    <div class="register-container">
      <!-- 左侧推广信息 -->
      <div class="promo-section">
        <div class="promo-content">
          <h1>加入游戏评论社区</h1>
          <p class="subtitle">发现、评价、分享你喜爱的游戏</p>
          <div class="features">
            <div class="feature-item">
              <el-icon size="32"><Star /></el-icon>
              <h3>评分评论</h3>
              <p>为你玩过的游戏打分，分享你的游戏体验</p>
            </div>
            <div class="feature-item">
              <el-icon size="32"><Collection /></el-icon>
              <h3>游戏收藏</h3>
              <p>收藏你喜欢的游戏，随时查看游戏详情</p>
            </div>
            <div class="feature-item">
              <el-icon size="32"><ChatDotRound /></el-icon>
              <h3>社区交流</h3>
              <p>与其他玩家交流，发现更多精彩游戏</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧注册表单 -->
      <div class="form-section">
        <div class="form-wrapper">
          <h2>用户注册</h2>
          <p class="form-subtitle">创建账号，开启游戏评论之旅</p>
          
          <el-form :model="form" :rules="rules" ref="formRef" size="large">
            <el-form-item prop="username">
              <el-input 
                v-model="form.username" 
                placeholder="请输入用户名" 
                prefix-icon="User"
              />
            </el-form-item>
            
            <el-form-item prop="email">
              <el-input 
                v-model="form.email" 
                placeholder="请输入邮箱" 
                prefix-icon="Message"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input 
                v-model="form.password" 
                type="password" 
                placeholder="请输入密码（至少6位）" 
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            
            <el-form-item prop="confirmPassword">
              <el-input 
                v-model="form.confirmPassword" 
                type="password" 
                placeholder="请再次输入密码" 
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                @click="handleRegister" 
                :loading="loading" 
                style="width: 100%"
              >
                立即注册
              </el-button>
            </el-form-item>
          </el-form>
          
          <div class="footer">
            已有账号？<router-link to="/login">立即登录</router-link>
          </div>
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
import { Star, Collection, ChatDotRound } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validatePass = (rule, value, callback) => {
  if (value !== form.value.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    await userStore.register(form.value.username, form.value.email, form.value.password)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3498db;
}

.register-container {
  display: flex;
  width: 1000px;
  min-height: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

/* 左侧推广区域 */
.promo-section {
  flex: 1;
  background: #3498db;
  color: white;
  padding: 60px 40px;
  display: flex;
  align-items: center;
}

.promo-content h1 {
  font-size: 36px;
  margin: 0 0 16px 0;
  font-weight: 600;
}

.subtitle {
  font-size: 18px;
  margin-bottom: 50px;
  opacity: 0.95;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.feature-item .el-icon {
  margin-bottom: 8px;
}

.feature-item h3 {
  font-size: 20px;
  margin: 0;
  font-weight: 500;
}

.feature-item p {
  font-size: 14px;
  margin: 0;
  opacity: 0.9;
  line-height: 1.6;
}

/* 右侧表单区域 */
.form-section {
  flex: 1;
  padding: 60px 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-wrapper {
  width: 100%;
  max-width: 400px;
}

.form-wrapper h2 {
  font-size: 28px;
  margin: 0 0 8px 0;
  color: #303133;
  text-align: center;
}

.form-subtitle {
  text-align: center;
  color: #909399;
  margin-bottom: 40px;
  font-size: 14px;
}

.footer {
  text-align: center;
  margin-top: 24px;
  color: #606266;
  font-size: 14px;
}

.footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.footer a:hover {
  color: #764ba2;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .register-container {
    flex-direction: column;
    width: 90%;
    min-height: auto;
  }

  .promo-section {
    padding: 40px 30px;
  }

  .promo-content h1 {
    font-size: 28px;
  }

  .features {
    gap: 20px;
  }

  .form-section {
    padding: 40px 30px;
  }
}
</style>
