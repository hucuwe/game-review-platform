/**
 * 获取完整的图片 URL
 * @param {string} path - 图片路径（可能是相对路径或完整 URL）
 * @returns {string} 完整的图片 URL
 */
export function getImageUrl(path) {
  if (!path) return ''
  
  // 如果已经是完整的 URL（http:// 或 https:// 或 data:）
  if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('data:')) {
    return path
  }
  
  // 如果是相对路径，拼接服务器地址
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'
  return `${baseURL}${path}`
}

/**
 * 获取多个图片的完整 URL
 * @param {Array<string>} paths - 图片路径数组
 * @returns {Array<string>} 完整的图片 URL 数组
 */
export function getImageUrls(paths) {
  if (!Array.isArray(paths)) return []
  return paths.map(path => getImageUrl(path))
}
