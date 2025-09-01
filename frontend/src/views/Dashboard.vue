<template>
  <div class="dashboard">
    <!-- 创建任务区域 -->
    <el-row :gutter="24" class="create-task-section">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>创建新任务</span>
            </div>
          </template>
          
          <LocalForm @submit="handleLocalSubmit" />
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 统计信息 -->
    <el-row :gutter="24" class="stats-section">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ totalTasks }}</div>
            <div class="stat-label">总任务数</div>
          </div>
          <div class="stat-icon">
            <el-icon><Document /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value active">{{ activeTasks.length }}</div>
            <div class="stat-label">进行中</div>
          </div>
          <div class="stat-icon active">
            <el-icon><Loading /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value success">{{ completedTasks.length }}</div>
            <div class="stat-label">已完成</div>
          </div>
          <div class="stat-icon success">
            <el-icon><CircleCheck /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value error">{{ failedTasks.length }}</div>
            <div class="stat-label">失败</div>
          </div>
          <div class="stat-icon error">
            <el-icon><CircleClose /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 活跃任务和系统状态 -->
    <el-row :gutter="24" class="content-section">
      <el-col :span="16">
        <!-- 活跃任务 -->
        <el-card>
          <template #header>
            <div class="card-header">
              <span>活跃任务</span>
              <el-button 
                type="primary" 
                size="small"
                @click="$router.push('/tasks')"
              >
                查看全部
              </el-button>
            </div>
          </template>
          
          <div v-if="activeTasks.length === 0" class="empty-state">
            <el-empty description="暂无活跃任务" />
          </div>
          
          <div v-else class="task-list">
            <div 
              v-for="task in activeTasks.slice(0, 5)" 
              :key="task.task_id"
              class="task-item"
            >
              <div class="task-info">
                <div class="task-title">
                  {{ getTaskTitle(task) }}
                </div>
                <div class="task-status">
                  <el-tag :type="getStatusType(task.status)">
                    {{ getTaskStatusLabel(task.status) }}
                  </el-tag>
                  <span class="task-step">{{ task.current_step || '等待中...' }}</span>
                </div>
              </div>
              <div class="task-progress">
                <el-progress 
                  :percentage="Math.round(task.progress * 100)"
                  :status="getProgressStatus(task.status)"
                />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <!-- 系统状态 -->
        <el-card class="system-status-card">
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
              <el-button 
                size="small"
                @click="refreshSystemStatus"
                :loading="systemStore.loading"
              >
                刷新
              </el-button>
            </div>
          </template>
          
          <div v-if="systemStore.systemStatus" class="system-status">
            <div class="status-item">
              <span class="status-label">CPU使用率</span>
              <el-progress 
                :percentage="systemStore.systemStatus.cpu_percent"
                :color="getResourceColor(systemStore.systemStatus.cpu_percent)"
                :show-text="false"
                class="status-progress"
              />
              <span class="status-value">{{ formatPercent(systemStore.systemStatus.cpu_percent) }}</span>
            </div>
            
            <div class="status-item">
              <span class="status-label">内存使用率</span>
              <el-progress 
                :percentage="systemStore.systemStatus.memory_percent"
                :color="getResourceColor(systemStore.systemStatus.memory_percent)"
                :show-text="false"
                class="status-progress"
              />
              <span class="status-value">{{ formatPercent(systemStore.systemStatus.memory_percent) }}</span>
            </div>
            
            <div class="status-item">
              <span class="status-label">磁盘使用率</span>
              <el-progress 
                :percentage="systemStore.systemStatus.disk_percent"
                :color="getResourceColor(systemStore.systemStatus.disk_percent)"
                :show-text="false"
                class="status-progress"
              />
              <span class="status-value">{{ formatPercent(systemStore.systemStatus.disk_percent) }}</span>
            </div>
          </div>
        </el-card>
        
        <!-- 存储信息 -->
        <el-card class="storage-info-card">
          <template #header>
            <div class="card-header">
              <span>存储信息</span>
            </div>
          </template>
          
          <div v-if="systemStore.storageInfo" class="storage-info">
            <div class="storage-item">
              <span class="storage-label">已用空间</span>
              <span class="storage-value">
                {{ formatFileSize(systemStore.storageInfo.used_space) }}
              </span>
            </div>
            <div class="storage-item">
              <span class="storage-label">总空间</span>
              <span class="storage-value">
                {{ formatFileSize(systemStore.storageInfo.total_space) }}
              </span>
            </div>
            <div class="storage-item">
              <span class="storage-label">上传文件</span>
              <span class="storage-value">
                {{ systemStore.storageInfo.upload_count }} 个
              </span>
            </div>
            <div class="storage-item">
              <span class="storage-label">输出文件</span>
              <span class="storage-value">
                {{ systemStore.storageInfo.output_count }} 个
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTaskStore } from '@/stores/task'
import { useSystemStore } from '@/stores/system'
import { getTaskStatusLabel, formatFileSize, formatPercent } from '@/utils'
import MarketForm from '@/components/MarketForm.vue'
import GithubForm from '@/components/GithubForm.vue'
import LocalForm from '@/components/LocalForm.vue'

const router = useRouter()
const taskStore = useTaskStore()
const systemStore = useSystemStore()

const activeTab = ref('market')

// 计算属性
const totalTasks = computed(() => taskStore.totalTasks)
const activeTasks = computed(() => taskStore.activeTasks)
const completedTasks = computed(() => taskStore.completedTasks)
const failedTasks = computed(() => taskStore.failedTasks)

// 方法
const handleTabChange = (tab: string) => {
  console.log('切换到:', tab)
}

const handleMarketSubmit = async (params: any) => {
  const task = await taskStore.createMarketTask(params)
  if (task) {
    router.push(`/tasks/${task.task_id}`)
  }
}

const handleGithubSubmit = async (params: any) => {
  const task = await taskStore.createGithubTask(params)
  if (task) {
    router.push(`/tasks/${task.task_id}`)
  }
}

const handleLocalSubmit = async (data: any) => {
  const response = await taskStore.uploadFile(data.file, data.platform, data.suffix)
  if (response) {
    router.push(`/tasks/${response.task_id}`)
  }
}

const getTaskTitle = (task: any) => {
  const params = task.parameters || {}
  
  if (task.mode === 'market') {
    return `${params.author}/${params.name} v${params.version}`
  } else if (task.mode === 'github') {
    return `${params.repo} ${params.release}`
  } else if (task.mode === 'local') {
    return params.file_name || '本地文件'
  }
  
  return '未知任务'
}

const getStatusType = (status: string) => {
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

const getProgressStatus = (status: string) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return undefined
}

const getResourceColor = (percentage: number) => {
  if (percentage < 60) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const refreshSystemStatus = async () => {
  await Promise.all([
    systemStore.fetchSystemStatus(),
    systemStore.fetchStorageInfo()
  ])
}

onMounted(async () => {
  await Promise.all([
    taskStore.fetchTasks({ limit: 10 }),
    refreshSystemStatus()
  ])
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.create-task-section {
  margin-bottom: 24px;
}

.stats-section {
  margin-bottom: 24px;
}

.content-section {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-card {
  text-align: center;
  position: relative;
  overflow: hidden;
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-content {
  text-align: left;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #262626;
  margin-bottom: 8px;
}

.stat-value.active {
  color: #1890ff;
}

.stat-value.success {
  color: #52c41a;
}

.stat-value.error {
  color: #ff4d4f;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
}

.stat-icon {
  font-size: 40px;
  color: #d9d9d9;
  opacity: 0.8;
}

.stat-icon.active {
  color: #1890ff;
}

.stat-icon.success {
  color: #52c41a;
}

.stat-icon.error {
  color: #ff4d4f;
}

.empty-state {
  padding: 40px 0;
}

.task-list {
  space-y: 16px;
}

.task-item {
  padding: 16px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  margin-bottom: 16px;
}

.task-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.task-title {
  font-weight: 500;
  color: #262626;
  margin-bottom: 4px;
}

.task-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-step {
  font-size: 12px;
  color: #8c8c8c;
}

.task-progress {
  margin-top: 8px;
}

.system-status-card {
  margin-bottom: 16px;
}

.system-status {
  space-y: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.status-label {
  width: 80px;
  font-size: 14px;
  color: #595959;
}

.status-progress {
  flex: 1;
  margin: 0 12px;
}

.status-value {
  width: 50px;
  text-align: right;
  font-size: 14px;
  font-weight: 500;
}

.storage-info-card {
  height: fit-content;
}

.storage-info {
  space-y: 12px;
}

.storage-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.storage-label {
  font-size: 14px;
  color: #595959;
}

.storage-value {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}

:deep(.el-progress-bar__outer) {
  height: 8px !important;
}
</style>