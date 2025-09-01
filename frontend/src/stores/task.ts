import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Task, TaskProgress, WebSocketMessage } from '@/types'
import { taskApi, WebSocketClient } from '@/api'
import { ElMessage } from '@/utils/element'

export const useTaskStore = defineStore('task', () => {
  // 状态
  const tasks = ref<Task[]>([])
  const currentTask = ref<Task | null>(null)
  const loading = ref(false)
  const wsClients = ref<Map<string, WebSocketClient>>(new Map())

  // 计算属性
  const activeTasks = computed(() => 
    tasks.value.filter(task => 
      ['pending', 'downloading', 'extracting', 'packaging'].includes(task.status)
    )
  )

  const completedTasks = computed(() => 
    tasks.value.filter(task => task.status === 'completed')
  )

  const failedTasks = computed(() => 
    tasks.value.filter(task => task.status === 'failed')
  )

  const totalTasks = computed(() => tasks.value.length)

  // 方法
  const fetchTasks = async (params?: { skip?: number; limit?: number; status?: string }) => {
    try {
      loading.value = true
      const data = await taskApi.getTasks(params)
      tasks.value = data
    } catch (error) {
      console.error('获取任务列表失败:', error)
      ElMessage.error('获取任务列表失败')
    } finally {
      loading.value = false
    }
  }

  const fetchTask = async (taskId: string) => {
    try {
      const data = await taskApi.getTask(taskId)
      currentTask.value = data
      
      // 更新任务列表中的对应项
      const index = tasks.value.findIndex(task => task.task_id === taskId)
      if (index !== -1) {
        tasks.value[index] = data
      }
      
      return data
    } catch (error) {
      console.error('获取任务详情失败:', error)
      ElMessage.error('获取任务详情失败')
      return null
    }
  }

  const createMarketTask = async (params: any) => {
    try {
      const task = await taskApi.createMarketTask(params)
      tasks.value.unshift(task)
      
      // 建立WebSocket连接
      connectWebSocket(task.task_id)
      
      ElMessage.success('任务创建成功')
      return task
    } catch (error) {
      console.error('创建Market任务失败:', error)
      return null
    }
  }

  const createGithubTask = async (params: any) => {
    try {
      const task = await taskApi.createGithubTask(params)
      tasks.value.unshift(task)
      
      // 建立WebSocket连接
      connectWebSocket(task.task_id)
      
      ElMessage.success('任务创建成功')
      return task
    } catch (error) {
      console.error('创建Github任务失败:', error)
      return null
    }
  }

  const uploadFile = async (file: File, platform?: string, suffix?: string) => {
    try {
      const response = await taskApi.uploadFile(file, platform, suffix)
      
      // 建立WebSocket连接
      connectWebSocket(response.task_id)
      
      // 刷新任务列表
      await fetchTasks()
      
      ElMessage.success('文件上传成功')
      return response
    } catch (error) {
      console.error('文件上传失败:', error)
      return null
    }
  }

  const cancelTask = async (taskId: string) => {
    try {
      await taskApi.cancelTask(taskId)
      
      // 更新本地状态
      const task = tasks.value.find(t => t.task_id === taskId)
      if (task) {
        task.status = 'cancelled'
      }
      
      // 断开WebSocket连接
      disconnectWebSocket(taskId)
      
      ElMessage.success('任务已取消')
    } catch (error) {
      console.error('取消任务失败:', error)
    }
  }

  const connectWebSocket = (taskId: string) => {
    // 如果已经有连接，先断开
    if (wsClients.value.has(taskId)) {
      disconnectWebSocket(taskId)
    }

    const wsClient = new WebSocketClient(
      taskId,
      (message: WebSocketMessage) => {
        handleWebSocketMessage(taskId, message)
      },
      (error) => {
        console.error(`WebSocket错误 (${taskId}):`, error)
      },
      (event) => {
        console.log(`WebSocket关闭 (${taskId}):`, event)
        wsClients.value.delete(taskId)
      }
    )

    wsClient.connect()
    wsClients.value.set(taskId, wsClient)
  }

  const disconnectWebSocket = (taskId: string) => {
    const wsClient = wsClients.value.get(taskId)
    if (wsClient) {
      wsClient.disconnect()
      wsClients.value.delete(taskId)
    }
  }

  const handleWebSocketMessage = (_taskId: string, message: WebSocketMessage) => {
    if (message.type === 'progress') {
      const progress: TaskProgress = message.data
      updateTaskProgress(progress)
    } else if (message.type === 'system') {
      ElMessage.info(message.data.message)
    }
  }

  const updateTaskProgress = (progress: TaskProgress) => {
    // 更新任务列表中的任务
    const taskIndex = tasks.value.findIndex(task => task.task_id === progress.task_id)
    if (taskIndex !== -1) {
      const task = tasks.value[taskIndex]
      task.status = progress.status
      task.progress = progress.progress
      task.current_step = progress.current_step
    }

    // 更新当前任务
    if (currentTask.value && currentTask.value.task_id === progress.task_id) {
      currentTask.value.status = progress.status
      currentTask.value.progress = progress.progress
      currentTask.value.current_step = progress.current_step
    }

    // 如果任务完成或失败，重新获取完整信息
    if (['completed', 'failed', 'cancelled'].includes(progress.status)) {
      setTimeout(() => {
        fetchTask(progress.task_id)
        disconnectWebSocket(progress.task_id)
      }, 1000)
    }
  }

  const clearTasks = () => {
    tasks.value = []
  }

  const removeTask = (taskId: string) => {
    const index = tasks.value.findIndex(task => task.task_id === taskId)
    if (index !== -1) {
      tasks.value.splice(index, 1)
    }
    disconnectWebSocket(taskId)
  }

  // 断开所有WebSocket连接
  const disconnectAllWebSockets = () => {
    wsClients.value.forEach((client, _taskId) => {
      client.disconnect()
    })
    wsClients.value.clear()
  }

  return {
    // 状态
    tasks,
    currentTask,
    loading,
    
    // 计算属性
    activeTasks,
    completedTasks,
    failedTasks,
    totalTasks,
    
    // 方法
    fetchTasks,
    fetchTask,
    createMarketTask,
    createGithubTask,
    uploadFile,
    cancelTask,
    connectWebSocket,
    disconnectWebSocket,
    updateTaskProgress,
    clearTasks,
    removeTask,
    disconnectAllWebSockets
  }
})