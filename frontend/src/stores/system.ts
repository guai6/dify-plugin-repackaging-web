import { defineStore } from 'pinia'
import { ref, watch, computed } from 'vue'
import type { SystemStatus, ApiConfig, StorageInfo } from '@/types'
import { systemApi, fileApi } from '@/api'
import { ElMessage, ElMessageBox } from '@/utils/element'

export const useSystemStore = defineStore('system', () => {
  // 状态
  const systemStatus = ref<SystemStatus | null>(null)
  const apiConfig = ref<ApiConfig | null>(null)
  const storageInfo = ref<StorageInfo | null>(null)
  const loading = ref(false)
  const storageWarningShown = ref(false)
  
  // 计算属性
  const storageUsagePercent = computed(() => {
    if (!storageInfo.value) return 0
    return Math.round((storageInfo.value.used_space / storageInfo.value.total_space) * 100)
  })
  
  const isStorageLow = computed(() => {
    return storageUsagePercent.value >= 85 // 85%以上警告
  })
  
  const isStorageCritical = computed(() => {
    return storageUsagePercent.value >= 95 // 95%以上严重警告
  })
  
  // 监听存储空间变化
  watch(storageInfo, (newInfo) => {
    if (newInfo && isStorageLow.value && !storageWarningShown.value) {
      showStorageWarning()
      storageWarningShown.value = true
    } else if (newInfo && !isStorageLow.value) {
      storageWarningShown.value = false
    }
  }, { deep: true })

  // 方法
  const fetchSystemStatus = async () => {
    try {
      loading.value = true
      const data = await systemApi.getSystemStatus()
      systemStatus.value = data
    } catch (error) {
      console.error('获取系统状态失败:', error)
    } finally {
      loading.value = false
    }
  }

  const fetchApiConfig = async () => {
    try {
      const data = await systemApi.getApiConfig()
      apiConfig.value = data
    } catch (error) {
      console.error('获取API配置失败:', error)
    }
  }

  const updateApiConfig = async (config: ApiConfig) => {
    try {
      await systemApi.updateApiConfig(config)
      apiConfig.value = config
      ElMessage.success('配置更新成功')
    } catch (error) {
      console.error('更新API配置失败:', error)
    }
  }

  const fetchStorageInfo = async () => {
    try {
      const data = await fileApi.getStorageInfo()
      storageInfo.value = data
    } catch (error) {
      console.error('获取存储信息失败:', error)
    }
  }

  const healthCheck = async () => {
    try {
      const data = await systemApi.healthCheck()
      return data
    } catch (error) {
      console.error('健康检查失败:', error)
      return { status: 'error', error: error }
    }
  }

  const getVersion = async () => {
    try {
      const data = await systemApi.getVersion()
      return data
    } catch (error) {
      console.error('获取版本信息失败:', error)
      return null
    }
  }
  
  const showStorageWarning = () => {
    const usagePercent = storageUsagePercent.value
    const isCritical = isStorageCritical.value
    
    const title = isCritical ? '存储空间严重不足' : '存储空间不足'
    const message = `磁盘使用率已达 ${usagePercent}%，建议清理不必要的文件。`
    
    ElMessageBox.alert(message, title, {
      type: isCritical ? 'error' : 'warning',
      showCancelButton: true,
      confirmButtonText: '去清理文件',
      cancelButtonText: '了解',
      callback: (action: string) => {
        if (action === 'confirm') {
          // 跳转到文件管理页面
          window.location.hash = '/files'
        }
      }
    })
  }
  
  const formatStorageUsage = () => {
    if (!storageInfo.value) return ''
    const usedGB = (storageInfo.value.used_space / (1024 * 1024 * 1024)).toFixed(1)
    const totalGB = (storageInfo.value.total_space / (1024 * 1024 * 1024)).toFixed(1)
    return `${usedGB}GB / ${totalGB}GB (${storageUsagePercent.value}%)`
  }

  return {
    // 状态
    systemStatus,
    apiConfig,
    storageInfo,
    loading,
    
    // 计算属性
    storageUsagePercent,
    isStorageLow,
    isStorageCritical,
    
    // 方法
    fetchSystemStatus,
    fetchApiConfig,
    updateApiConfig,
    fetchStorageInfo,
    healthCheck,
    getVersion,
    showStorageWarning,
    formatStorageUsage
  }
})