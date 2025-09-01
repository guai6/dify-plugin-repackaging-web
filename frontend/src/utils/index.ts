import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { ElMessage } from './element'

// 配置dayjs插件
dayjs.extend(relativeTime)

// 格式化文件大小
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化时间
export function formatTime(timestamp: string): string {
  if (!timestamp) return '--'
  
  return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss')
}

// 格式化相对时间
export function formatRelativeTime(timestamp: string): string {
  if (!timestamp) return '--'
  
  return dayjs(timestamp).fromNow()
}

// 格式化百分比
export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`
}

// 获取任务状态的颜色
export function getTaskStatusColor(status: string): string {
  const colors = {
    pending: '#909399',
    downloading: '#409eff',
    extracting: '#e6a23c',
    packaging: '#e6a23c',
    completed: '#67c23a',
    failed: '#f56c6c',
    cancelled: '#909399'
  }
  return colors[status as keyof typeof colors] || '#909399'
}

// 获取任务状态的标签
export function getTaskStatusLabel(status: string): string {
  const labels = {
    pending: '等待中',
    downloading: '下载中',
    extracting: '解压中',
    packaging: '打包中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return labels[status as keyof typeof labels] || status
}

// 获取文件类型图标
export function getFileTypeIcon(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase()
  
  const icons = {
    difypkg: 'Document',
    zip: 'FolderOpened',
    tar: 'FolderOpened',
    gz: 'FolderOpened',
    txt: 'Document',
    log: 'Document',
    json: 'Document',
    py: 'Document'
  }
  
  return icons[ext as keyof typeof icons] || 'Document'
}

// 验证URL格式
export function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

// 验证版本号格式
export function isValidVersion(version: string): boolean {
  const versionRegex = /^(\d+)\.(\d+)\.(\d+)(-[\w\.-]+)?$/
  return versionRegex.test(version)
}

// 防抖函数
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// 节流函数
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  
  return function executedFunction(this: any, ...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// 生成随机ID
export function generateId(): string {
  return Math.random().toString(36).substr(2, 9)
}

// 复制到剪贴板
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
    return true
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
    return false
  }
}

// 下载文件
export function downloadFile(url: string, filename?: string) {
  const link = document.createElement('a')
  link.href = url
  if (filename) {
    link.download = filename
  }
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 格式化JSON
export function formatJson(obj: any): string {
  return JSON.stringify(obj, null, 2)
}

// 安全的JSON解析
export function safeJsonParse<T = any>(str: string, defaultValue: T): T {
  try {
    return JSON.parse(str)
  } catch {
    return defaultValue
  }
}