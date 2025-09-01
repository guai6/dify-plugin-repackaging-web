<template>
  <div class="task-detail">
    <!-- 头部信息 -->
    <el-card class="header-card">
      <div class="header-content">
        <div class="header-left">
          <el-button
            @click="$router.go(-1)"
            circle
            size="small"
          >
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <div class="header-info">
            <h3>{{ taskTitle }}</h3>
            <div class="header-meta">
              <el-tag :type="getStatusType(task?.status)">
                {{ getTaskStatusLabel(task?.status) }}
              </el-tag>
              <span class="task-id">ID: {{ taskId }}</span>
            </div>
          </div>
        </div>
        <div class="header-right">
          <el-space>
            <el-button
              v-if="canCancel"
              type="warning"
              @click="handleCancel"
            >
              取消任务
            </el-button>
            
            <el-button
              v-if="canDownload"
              type="success"
              @click="handleDownload"
            >
              下载结果
            </el-button>
            
            <el-button
              :icon="refreshing ? 'Loading' : 'Refresh'"
              :loading="refreshing"
              @click="refreshTask"
            >
              刷新
            </el-button>
          </el-space>
        </div>
      </div>
    </el-card>
    
    <!-- 主要内容 -->
    <el-row :gutter="24">
      <!-- 左侧：任务信息和进度 -->
      <el-col :span="16">
        <!-- 进度信息 -->
        <el-card class="progress-card">
          <template #header>
            <span>任务进度</span>
          </template>
          
          <div v-if="task" class="progress-content">
            <div class="progress-bar">
              <el-progress
                :percentage="Math.round(task.progress * 100)"
                :status="getProgressStatus(task.status)"
                stroke-width="12"
              />
            </div>
            
            <div class="progress-info">
              <div class="current-step">
                <span class="label">当前步骤:</span>
                <span class="value">{{ task.current_step || '等待中...' }}</span>
              </div>
              <div class="progress-stats">
                <span>{{ Math.round(task.progress * 100) }}% 完成</span>
                <span>{{ task.total_steps }} 步骤</span>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 实时日志 -->
        <el-card class="log-card">
          <template #header>
            <div class="log-header">
              <span>实时日志</span>
              <el-space>
                <el-button
                  size="small"
                  @click="toggleAutoScroll"
                >
                  {{ autoScroll ? '暂停滚动' : '自动滚动' }}
                </el-button>
                <el-button
                  size="small"
                  @click="clearLogs"
                >
                  清空日志
                </el-button>
                <el-button
                  size="small"
                  @click="downloadLogs"
                >
                  导出日志
                </el-button>
              </el-space>
            </div>
          </template>
          
          <div class="log-content" ref="logContainer">
            <div v-if="logs.length === 0" class="empty-logs">
              <el-empty description="暂无日志信息" />
            </div>
            <div v-else class="log-list">
              <div
                v-for="(log, index) in logs"
                :key="index"
                :class="['log-item', `log-${log.level}`]"
              >
                <span class="log-time">{{ formatTime(log.timestamp) }}</span>
                <span class="log-level">{{ log.level.toUpperCase() }}</span>
                <span class="log-message">{{ log.message }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：任务详情 -->
      <el-col :span="8">
        <!-- 基本信息 -->
        <el-card class="info-card">
          <template #header>
            <span>基本信息</span>
          </template>
          
          <div v-if="task" class="task-info">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="任务ID">
                <div class="copyable-text" @click="copyText(task.task_id)">
                  {{ task.task_id }}
                  <el-icon class="copy-icon"><CopyDocument /></el-icon>
                </div>
              </el-descriptions-item>
              
              <el-descriptions-item label="处理模式">
                <el-tag>{{ getModeLabel(task.mode) }}</el-tag>
              </el-descriptions-item>
              
              <el-descriptions-item label="创建时间">
                {{ formatTime(task.created_at) }}
              </el-descriptions-item>
              
              <el-descriptions-item label="开始时间">
                {{ formatTime(task.started_at) }}
              </el-descriptions-item>
              
              <el-descriptions-item label="完成时间">
                {{ formatTime(task.completed_at) }}
              </el-descriptions-item>
              
              <el-descriptions-item
                v-if="task.file_size"
                label="文件大小"
              >
                {{ formatFileSize(task.file_size) }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
        
        <!-- 任务参数 -->
        <el-card class="params-card">
          <template #header>
            <span>任务参数</span>
          </template>
          
          <div v-if="task?.parameters" class="task-params">
            <el-descriptions :column="1" border>
              <el-descriptions-item
                v-for="(value, key) in task.parameters"
                :key="key"
                :label="getParamLabel(key)"
              >
                {{ value }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
          
          <div v-else class="empty-params">
            <el-empty description="无参数信息" />
          </div>
        </el-card>
        
        <!-- 错误信息 -->
        <el-card v-if="task?.error_message" class="error-card">
          <template #header>
            <span>错误信息</span>
          </template>
          
          <el-alert
            :title="task.error_message"
            type="error"
            :closable="false"
            show-icon
          />
        </el-card>
        
        <!-- 连接状态 -->
        <el-card class="status-card">
          <template #header>
            <span>连接状态</span>
          </template>
          
          <div class="connection-status">
            <div class="status-item">
              <span class="status-label">WebSocket:</span>
              <el-tag :type="wsConnected ? 'success' : 'danger'">
                {{ wsConnected ? '已连接' : '未连接' }}
              </el-tag>
            </div>
            
            <div class="status-actions">
              <el-button
                v-if="!wsConnected"
                size="small"
                type="primary"
                @click="connectWebSocket"
              >
                连接实时日志
              </el-button>
              
              <el-button
                v-else
                size="small"
                type="warning"
                @click="disconnectWebSocket"
              >
                断开连接
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTaskStore } from '@/stores/task'
import { 
  getTaskStatusLabel, 
  formatTime, 
  formatFileSize,
  copyToClipboard,
  downloadFile
} from '@/utils'
import { taskApi, WebSocketClient } from '@/api'

interface LogItem {
  timestamp: string
  level: string
  message: string
}

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()

// 响应式数据
const refreshing = ref(false)
const wsConnected = ref(false)
const autoScroll = ref(true)
const logs = ref<LogItem[]>([])
const logContainer = ref<HTMLElement>()
let wsClient: WebSocketClient | null = null

// 任务ID
const taskId = computed(() => route.params.id as string)

// 任务信息
const task = computed(() => taskStore.currentTask)

// 任务标题
const taskTitle = computed(() => {
  if (!task.value) return '加载中...'
  
  const params = task.value.parameters || {}
  
  if (task.value.mode === 'market') {
    return `${params.author}/${params.name} v${params.version}`
  } else if (task.value.mode === 'github') {
    return `${params.repo} ${params.release}`
  } else if (task.value.mode === 'local') {
    return params.file_name || '本地文件'
  }
  
  return '未知任务'
})

// 计算属性
const canCancel = computed(() => {
  return task.value && ['pending', 'downloading', 'extracting', 'packaging'].includes(task.value.status)
})

const canDownload = computed(() => {
  return task.value && task.value.status === 'completed'
})

// 方法
const refreshTask = async () => {
  refreshing.value = true
  try {
    await taskStore.fetchTask(taskId.value)
  } finally {
    refreshing.value = false
  }
}

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm('确定要取消这个任务吗？', '确认取消', {
      type: 'warning'
    })
    
    await taskStore.cancelTask(taskId.value)
    await refreshTask()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消任务失败:', error)
    }
  }
}

const handleDownload = () => {
  const url = taskApi.downloadResult(taskId.value)
  downloadFile(url)
}

const getStatusType = (status?: string) => {
  if (!status) return ''
  
  const types = {
    pending: '',
    downloading: 'warning',
    extracting: 'warning',
    packaging: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return types[status as keyof typeof types] || ''
}

const getProgressStatus = (status?: string) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return undefined
}

const getModeLabel = (mode: string) => {
  const labels = {
    market: 'Marketplace',
    github: 'Github',
    local: '本地文件'
  }
  return labels[mode as keyof typeof labels] || mode
}

const getParamLabel = (key: string) => {
  const labels = {
    author: '作者',
    name: '名称',
    version: '版本',
    repo: '仓库',
    release: '发布版本',
    asset_name: '文件名',
    file_name: '文件名',
    platform: '平台',
    suffix: '后缀'
  }
  return labels[key as keyof typeof labels] || key
}

const copyText = (text: string) => {
  copyToClipboard(text)
}

const connectWebSocket = () => {
  if (wsClient) {
    wsClient.disconnect()
  }
  
  wsClient = new WebSocketClient(
    taskId.value,
    handleWebSocketMessage,
    (error) => {
      console.error('WebSocket错误:', error)
      wsConnected.value = false
    },
    (event) => {
      console.log('WebSocket关闭:', event)
      wsConnected.value = false
    }
  )
  
  wsClient.connect()
  wsConnected.value = true
}

const disconnectWebSocket = () => {
  if (wsClient) {
    wsClient.disconnect()
    wsClient = null
  }
  wsConnected.value = false
}

const handleWebSocketMessage = (message: any) => {
  if (message.type === 'progress') {
    const progress = message.data
    
    // 添加日志
    addLog('info', progress.message || progress.current_step)
    
    // 更新任务状态
    taskStore.updateTaskProgress(progress)
  } else if (message.type === 'system') {
    addLog('system', message.data.message)
  }
}

const addLog = (level: string, message: string) => {
  logs.value.push({
    timestamp: new Date().toISOString(),
    level,
    message
  })
  
  // 自动滚动到底部
  if (autoScroll.value) {
    nextTick(() => {
      if (logContainer.value) {
        logContainer.value.scrollTop = logContainer.value.scrollHeight
      }
    })
  }
  
  // 限制日志数量
  if (logs.value.length > 1000) {
    logs.value = logs.value.slice(-500)
  }
}

const toggleAutoScroll = () => {
  autoScroll.value = !autoScroll.value
}

const clearLogs = () => {
  logs.value = []
}

const downloadLogs = () => {
  const logText = logs.value
    .map(log => `[${formatTime(log.timestamp)}] ${log.level.toUpperCase()}: ${log.message}`)
    .join('\n')
  
  const blob = new Blob([logText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `task-${taskId.value}-logs.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  await refreshTask()
  
  // 如果任务正在进行中，自动连接WebSocket
  if (task.value && ['pending', 'downloading', 'extracting', 'packaging'].includes(task.value.status)) {
    connectWebSocket()
  }
})

onUnmounted(() => {
  disconnectWebSocket()
})
</script>

<style scoped>
.task-detail {
  max-width: 1400px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-info h3 {
  margin: 0;
  color: #262626;
  font-size: 20px;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.task-id {
  font-size: 12px;
  color: #8c8c8c;
}

.progress-card {
  margin-bottom: 24px;
}

.progress-content {
  padding: 16px 0;
}

.progress-bar {
  margin-bottom: 16px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.current-step .label {
  color: #8c8c8c;
  margin-right: 8px;
}

.current-step .value {
  color: #262626;
  font-weight: 500;
}

.progress-stats {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #8c8c8c;
}

.log-card {
  margin-bottom: 24px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-content {
  height: 400px;
  overflow-y: auto;
  background-color: #1e1e1e;
  border-radius: 4px;
  padding: 12px;
}

.empty-logs {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.log-list {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
}

.log-item {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  padding: 2px 0;
}

.log-time {
  color: #888;
  min-width: 120px;
}

.log-level {
  min-width: 60px;
  font-weight: bold;
}

.log-message {
  flex: 1;
  word-break: break-all;
}

.log-info {
  color: #4CAF50;
}

.log-info .log-level {
  color: #4CAF50;
}

.log-info .log-message {
  color: #E8E8E8;
}

.log-warn {
  color: #FF9800;
}

.log-warn .log-level {
  color: #FF9800;
}

.log-warn .log-message {
  color: #E8E8E8;
}

.log-error {
  color: #F44336;
}

.log-error .log-level {
  color: #F44336;
}

.log-error .log-message {
  color: #E8E8E8;
}

.log-system {
  color: #2196F3;
}

.log-system .log-level {
  color: #2196F3;
}

.log-system .log-message {
  color: #E8E8E8;
}

.info-card {
  margin-bottom: 16px;
}

.copyable-text {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: color 0.2s;
}

.copyable-text:hover {
  color: #1890ff;
}

.copy-icon {
  margin-left: 8px;
  font-size: 14px;
}

.params-card {
  margin-bottom: 16px;
}

.empty-params {
  padding: 20px 0;
}

.error-card {
  margin-bottom: 16px;
}

.status-card {
  margin-bottom: 16px;
}

.connection-status {
  padding: 8px 0;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.status-label {
  color: #8c8c8c;
}

.status-actions {
  text-align: center;
}

:deep(.el-progress-bar__outer) {
  height: 12px !important;
  background-color: #f0f0f0;
}

:deep(.el-progress-bar__inner) {
  border-radius: 6px;
}
</style>