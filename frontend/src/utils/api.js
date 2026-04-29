import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 获取完整的图片 URL
const getFullImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('data:')) {
    return path
  }
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'
  return `${baseURL}${path}`
}

// 递归处理对象中的图片字段
const processImageFields = (obj) => {
  if (!obj || typeof obj !== 'object') return obj
  
  if (Array.isArray(obj)) {
    return obj.map(item => processImageFields(item))
  }
  
  const processed = { ...obj }
  
  // 处理常见的图片字段
  const imageFields = ['cover_image', 'avatar', 'image_url', 'images']
  
  for (const field of imageFields) {
    if (field in processed) {
      if (field === 'images' && Array.isArray(processed[field])) {
        // 处理图片数组
        processed[field] = processed[field].map(img => getFullImageUrl(img))
      } else if (typeof processed[field] === 'string') {
        // 处理单个图片
        processed[field] = getFullImageUrl(processed[field])
      }
    }
  }
  
  // 递归处理嵌套对象
  for (const key in processed) {
    if (typeof processed[key] === 'object' && processed[key] !== null) {
      processed[key] = processImageFields(processed[key])
    }
  }
  
  return processed
}

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    // 自动处理响应数据中的图片字段
    if (response.data) {
      response.data = processImageFields(response.data)
    }
    return response
  },
  (error) => {
    if (error.response) {
      const message = error.response.data.message || '请求失败'
      const status = error.response.status
      
      // 对于 401 和 422 错误（认证相关）
      if (status === 401 || status === 422) {
        // 清除无效的 token
        const oldToken = localStorage.getItem('token')
        if (oldToken) {
          localStorage.removeItem('token')
          
          // 只在不是登录/注册页面时才提示和跳转
          const currentPath = window.location.pathname
          if (!currentPath.includes('/login') && !currentPath.includes('/register')) {
            ElMessage.error('登录已过期，请重新登录')
            setTimeout(() => {
              window.location.href = '/login'
            }, 1500)
          }
        }
      } else if (status === 403) {
        ElMessage.error(message || '权限不足')
      } else if (status === 404) {
        ElMessage.error(message || '资源不存在')
      } else if (status >= 500) {
        ElMessage.error('服务器错误，请稍后重试')
      } else {
        ElMessage.error(message)
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error('请求失败')
    }
    return Promise.reject(error)
  }
)

export default api
