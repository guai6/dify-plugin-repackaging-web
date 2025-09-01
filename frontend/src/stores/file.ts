import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FileInfo } from '@/types'
import { fileApi } from '@/api'
import { ElMessage } from '@/utils/element'

export const useFileStore = defineStore('file', () => {
  // 状态
  const files = ref<FileInfo[]>([])
  const loading = ref(false)

  // 方法
  const fetchFiles = async (fileType: string = 'all') => {
    try {
      loading.value = true
      const data = await fileApi.getFiles(fileType)
      files.value = data
    } catch (error) {
      console.error('获取文件列表失败:', error)
      ElMessage.error('获取文件列表失败')
    } finally {
      loading.value = false
    }
  }

  const deleteFile = async (fileType: string, filename: string) => {
    try {
      await fileApi.deleteFile(fileType, filename)
      
      // 从本地列表中移除
      const index = files.value.findIndex(file => file.name === filename && file.type === fileType)
      if (index !== -1) {
        files.value.splice(index, 1)
      }
      
      ElMessage.success('文件删除成功')
    } catch (error) {
      console.error('删除文件失败:', error)
    }
  }

  const cleanupTempFiles = async () => {
    try {
      const result = await fileApi.cleanupTempFiles()
      ElMessage.success(result.message)
      
      // 刷新文件列表
      await fetchFiles()
    } catch (error) {
      console.error('清理临时文件失败:', error)
    }
  }

  const downloadFile = (fileType: string, filename: string) => {
    const url = fileApi.downloadFile(fileType, filename)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return {
    // 状态
    files,
    loading,
    
    // 方法
    fetchFiles,
    deleteFile,
    cleanupTempFiles,
    downloadFile
  }
})