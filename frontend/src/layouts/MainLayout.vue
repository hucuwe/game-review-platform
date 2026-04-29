<template>
  <div class="main-layout">
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-content">
          <div class="logo" @click="$router.push('/')">
            <el-icon :size="28"><Trophy /></el-icon>
            <span>游戏评论平台</span>
          </div>
          
          <!-- 导航菜单 -->
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            :ellipsis="false"
            background-color="#2c3e50"
            text-color="#ecf0f1"
            active-text-color="#3498db"
            class="nav-menu"
            router
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/games">
              <el-icon><Grid /></el-icon>
              <span>游戏库</span>
            </el-menu-item>
            <el-menu-item index="/hot">
              <el-icon><TrendCharts /></el-icon>
              <span>热门游戏</span>
            </el-menu-item>
            <el-menu-item index="/my-ratings" v-if="userStore.isLoggedIn">
              <el-icon><Star /></el-icon>
              <span>我的评分</span>
            </el-menu-item>
            <el-menu-item index="/announcements">
              <el-icon><Bell /></el-icon>
              <span>公告</span>
            </el-menu-item>
            <el-menu-item index="/about">
              <el-icon><InfoFilled /></el-icon>
              <span>关于</span>
            </el-menu-item>
          </el-menu>

          <!-- 用户操作区 -->
          <div class="header-right">
            <template v-if="userStore.isLoggedIn">
              <el-button v-if="userStore.isAdmin" type="warning" @click="$router.push('/admin')" size="small">
                <el-icon><Setting /></el-icon>
                <span>管理后台</span>
              </el-button>
              <el-dropdown>
                <div class="user-info">
                  <el-avatar :size="32" :src="userStore.user?.avatar">
                    {{ userStore.user?.username?.charAt(0) }}
                  </el-avatar>
                  <span>{{ userStore.user?.username }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="$router.push('/profile')">
                      <el-icon><User /></el-icon>
                      个人中心
                    </el-dropdown-item>
                    <el-dropdown-item @click="$router.push('/my-ratings')">
                      <el-icon><Star /></el-icon>
                      我的评分
                    </el-dropdown-item>
                    <el-dropdown-item divided @click="handleLogout">
                      <el-icon><SwitchButton /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <template v-else>
              <el-button @click="$router.push('/login')" size="small">登录</el-button>
              <el-button type="primary" @click="$router.push('/register')" size="small">注册</el-button>
            </template>
          </div>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>

      <!-- 页脚 -->
      <el-footer class="footer">
        <div class="footer-content">
          <div class="footer-section">
            <h4>关于我们</h4>
            <p>游戏评论平台致力于为玩家提供专业、客观的游戏评分和评论服务。我们汇聚了众多游戏爱好者，共同分享游戏体验，帮助玩家发现优质游戏作品。</p>
            <p style="margin-top: 20px; color: #7f8c8d; font-size: 13px;">让每一次游戏选择都更加明智</p>
          </div>
          <div class="footer-section">
            <h4>快速链接</h4>
            <div class="footer-links">
              <a @click="$router.push('/')">首页</a>
              <a @click="$router.push('/games')">游戏库</a>
              <a @click="$router.push('/hot')">热门游戏</a>
              <a @click="$router.push('/my-ratings')" v-if="userStore.isLoggedIn">我的评分</a>
              <a @click="$router.push('/about')">关于平台</a>
              <a @click="$router.push('/register')" v-if="!userStore.isLoggedIn">注册账号</a>
            </div>
          </div>
          <div class="footer-section">
            <h4>联系方式</h4>
            <p>contact@gamerating.com</p>
            <p style="margin-top: 15px; color: #7f8c8d;">工作时间：周一至周五 9:00-18:00</p>
            <p style="margin-top: 15px; color: #7f8c8d;">地址：中国·北京</p>
          </div>
        </div>
        <div class="footer-bottom">
          <p>© 2026 游戏评论平台 Game Rating Platform. All rights reserved. | 毕业设计项目</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

const activeMenu = computed(() => route.path)

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('退出成功')
  router.push('/')
}

onMounted(() => {
  // 初始化用户状态
  userStore.init()
})
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.el-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
.header {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 0;
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #ecf0f1;
  font-size: 22px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  padding: 0 20px;
}

.logo:hover {
  color: #3498db;
  transform: scale(1.05);
}

.nav-menu {
  flex: 1;
  border: none;
  background: transparent;
}

.nav-menu .el-menu-item {
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.nav-menu .el-menu-item:hover {
  background-color: rgba(52, 152, 219, 0.1);
  border-bottom-color: #3498db;
}

.nav-menu .el-menu-item.is-active {
  border-bottom-color: #3498db;
  background-color: rgba(52, 152, 219, 0.15);
}

.header-right {
  display: flex;
  gap: 15px;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #ecf0f1;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s;
}

.user-info:hover {
  background-color: rgba(52, 152, 219, 0.2);
}

.user-info span {
  font-size: 14px;
  font-weight: 500;
}

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 0;
  background-color: #f5f7fa;
}

/* 页脚 */
.footer {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  color: #ecf0f1;
  padding: 50px 20px 30px;
  margin-top: auto;
  border-top: 3px solid #3498db;
  height: auto !important;
}


.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr;
  gap: 60px;
  padding-bottom: 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 20px;
}

.footer-section h4 {
  color: #3498db;
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-section h4::before {
  content: '';
  width: 4px;
  height: 20px;
  background: #3498db;
  border-radius: 2px;
}

.footer-section p {
  color: #bdc3c7;
  line-height: 1.8;
  font-size: 14px;
  margin: 0 0 12px 0;
}

.footer-section:first-child p {
  max-width: 400px;
  line-height: 2;
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer-links a {
  color: #bdc3c7;
  text-decoration: none;
  transition: all 0.3s;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-links a::before {
  content: '▸';
  color: #3498db;
  font-size: 12px;
  transition: transform 0.3s;
}

.footer-links a:hover {
  color: #3498db;
  padding-left: 8px;
}

.footer-links a:hover::before {
  transform: translateX(4px);
}

.footer-section:last-child p {
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-section:last-child p::before {
  content: '📧';
  font-size: 16px;
}

.footer-bottom {
  text-align: center;
  color: #95a5a6;
  font-size: 13px;
  padding-top: 20px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .header-content {
    max-width: 100%;
  }
  
  .footer-content {
    grid-template-columns: 1fr;
    gap: 30px;
  }
}
</style>
