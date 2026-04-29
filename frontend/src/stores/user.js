import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  const initialized = ref(false)

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const setUser = (userData) => {
    user.value = userData
  }

  const login = async (username, password) => {
    const res = await api.post('/auth/login', { username, password })
    setToken(res.data.token)
    setUser(res.data.user)
    initialized.value = true
    return res.data
  }

  const register = async (username, email, password) => {
    const res = await api.post('/auth/register', { username, email, password })
    return res.data
  }

  const logout = () => {
    token.value = ''
    user.value = null
    initialized.value = false
    localStorage.removeItem('token')
  }

  const fetchProfile = async () => {
    if (!token.value) {
      initialized.value = true
      return
    }
    
    try {
      const res = await api.get('/auth/profile')
      setUser(res.data.user)
      initialized.value = true
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果 token 无效，清除登录状态
      if (error.response?.status === 401 || error.response?.status === 422) {
        logout()
      }
      initialized.value = true
    }
  }

  // 初始化用户状态
  const init = async () => {
    if (token.value && !user.value) {
      await fetchProfile()
    } else if (!token.value) {
      initialized.value = true
    }
  }

  return {
    user,
    token,
    initialized,
    isLoggedIn,
    isAdmin,
    login,
    register,
    logout,
    fetchProfile,
    init,
    setToken,
    setUser
  }
})
