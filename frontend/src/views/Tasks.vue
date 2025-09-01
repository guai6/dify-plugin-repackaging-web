<template>
  <div class="tasks-page">
    <!-- 头部操作栏 -->
    <el-card class="header-card">
      <div class="header-content">
        <div class="header-left">
          <h3>任务管理</h3>
          <el-tag type="info">总计 {{ totalTasks }} 个任务</el-tag>
        </div>
        <div class="header-right">
          <el-space>
            <el-select
              v-model="statusFilter"
              placeholder="筛选状态"
              clearable
              style="width: 150px"
              @change="handleFilterChange"
            >
              <el-option label="全部" value="" />
              <el-option
                v-for="status in statusOptions"
                :key="status.value"
                :label="status.label"
                :value="status.value"
              />
            </el-select>
            
            <el-button
              :icon="refreshing ? 'Loading' : 'Refresh'"
              :loading="refreshing"
              @click="refreshTasks"
            >
              刷新
            </el-button>
            
            <el-button
              type="primary"
              @click="$router.push('/dashboard')"
            >
              创建任务
            </el-button>
          </el-space>
        </div>
      </div>
    </el-card>
    
    <!-- 任务列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="taskStore.loading"
        :data="filteredTasks"
        stripe
        @row-click="handleRowClick"
        style="width: 100%"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="task-expand">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="任务ID">
                  {{ row.task_id }}
                </el-descriptions-item>
                <el-descriptions-item label="处理模式">
                  <el-tag>{{ getModeLabel(row.mode) }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="创建时间">
                  {{ formatTime(row.created_at) }}
                </el-descriptions-item>
                <el-descriptions-item label="开始时间">
                  {{ formatTime(row.started_at) }}
                </el-descriptions-item>
                <el-descriptions-item label="完成时间">
                  {{ formatTime(row.completed_at) }}
                </el-descriptions-item>
                <el-descriptions-item label="文件大小">
                  {{ row.file_size ? formatFileSize(row.file_size) : '--' }}
                </el-descriptions-item>
              </el-descriptions>
              
              <div v-if="row.parameters" class="task-params">
                <h4>任务参数</h4>
                <pre>{{ formatJson(row.parameters) }}</pre>
              </div>
              
              <div v-if="row.error_message" class="task-error">
                <h4>错误信息</h4>
                <el-alert
                  :title="row.error_message"
                  type="error"
                  :closable="false"
                />
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="任务名称" min-width="200">
          <template #default="{ row }">
            <div class="task-name">
              <el-link
                type="primary"
                @click.stop="goToTaskDetail(row.task_id)"
              >
                {{ getTaskTitle(row) }}
              </el-link>
              <div class="task-mode">
                <el-tag size="small">{{ getModeLabel(row.mode) }}</el-tag>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getTaskStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="进度" width="200">
          <template #default="{ row }">
            <div class="progress-cell">
              <el-progress
                :percentage="Math.round(row.progress * 100)"
                :status="getProgressStatus(row.status)"
                :show-text="false"
              />
              <span class="progress-text">
                {{ Math.round(row.progress * 100) }}%
              </span>
            </div>
            <div v-if="row.current_step" class="progress-step">
              {{ row.current_step }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            <div class="time-cell">
              <div>{{ formatTime(row.created_at) }}</div>
              <div class="relative-time">
                {{ formatRelativeTime(row.created_at) }}
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button
                size="small"
                @click.stop="goToTaskDetail(row.task_id)"
              >
                详情
              </el-button>
              
              <el-button
                v-if="canCancel(row.status)"
                size="small"
                type="warning"
                @click.stop="handleCancel(row.task_id)"
              >
                取消
              </el-button>
              
              <el-button
                v-if="canDownload(row.status)"
                size="small"
                type="success"
                @click.stop="handleDownload(row.task_id)"
              >
                下载
              </el-button>
              
              <el-dropdown @click.stop trigger="click">
                <el-button size="small">
                  更多
                  <el-icon><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="copyTaskId(row.task_id)">
                      复制任务ID
                    </el-dropdown-item>
                    <el-dropdown-item
                      v-if="row.task_id"
                      @click="connectWebSocket(row.task_id)"
                    >
                      连接实时日志
                    </el-dropdown-item>
                    <el-dropdown-item
                      divided
                      @click="removeTask(row.task_id)"
                    >
                      删除任务
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalTasks"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTaskStore } from '@/stores/task'
import { 
  getTaskStatusLabel, 
  formatTime, 
  formatRelativeTime, 
  formatFileSize, 
  formatJson,
  copyToClipboard,
  downloadFile
} from '@/utils'
import { taskApi } from '@/api'

const router = useRouter()
const taskStore = useTaskStore()

// 响应式数据
const refreshing = ref(false)
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 状态选项
const statusOptions = [
  { label: '等待中', value: 'pending' },
  { label: '下载中', value: 'downloading' },
  { label: '解压中', value: 'extracting' },
  { label: '打包中', value: 'packaging' },
  { label: '已完成', value: 'completed' },
  { label: '失败', value: 'failed' },
  { label: '已取消', value: 'cancelled' }
]

// 计算属性
const totalTasks = computed(() => taskStore.totalTasks)

const filteredTasks = computed(() => {
  let tasks = taskStore.tasks
  
  if (statusFilter.value) {
    tasks = tasks.filter(task => task.status === statusFilter.value)
  }
  
  return tasks
})

// 方法
const refreshTasks = async () => {
  refreshing.value = true
  try {
    await taskStore.fetchTasks({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      status: statusFilter.value || undefined
    })
  } finally {
    refreshing.value = false
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  refreshTasks()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  refreshTasks()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  refreshTasks()
}

const handleRowClick = (row: any) => {
  goToTaskDetail(row.task_id)
}

const goToTaskDetail = (taskId: string) => {
  router.push(`/tasks/${taskId}`)
}

const getTaskTitle = (task: any) => {
  // 优先使用task_name字段
  if (task.task_name) {
    return task.task_name
  }
  
  // 后备方案：根据模式生成名称
  const params = task.parameters || {}
  
  if (task.mode === 'market') {
    return `${params.author}/${params.name} v${params.version}`
  } else if (task.mode === 'github') {
    return `${params.repo} ${params.release}`
  } else if (task.mode === 'local') {
    return params.original_filename || params.file_name || '本地文件'
  }
  
  return '未知任务'
}

const getModeLabel = (mode: string) => {
  const labels = {
    market: 'Marketplace',
    github: 'Github',
    local: '本地文件'
  }
  return labels[mode as keyof typeof labels] || mode
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

const canCancel = (status: string) => {
  return ['pending', 'downloading', 'extracting', 'packaging'].includes(status)
}

const canDownload = (status: string) => {
  return status === 'completed'
}

const handleCancel = async (taskId: string) => {
  try {
    await ElMessageBox.confirm('确定要取消这个任务吗？', '确认取消', {
      type: 'warning'
    })
    
    await taskStore.cancelTask(taskId)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消任务失败:', error)
    }
  }
}

const handleDownload = (taskId: string) => {
  const url = taskApi.downloadResult(taskId)
  downloadFile(url)
}

const copyTaskId = (taskId: string) => {
  copyToClipboard(taskId)
}

const connectWebSocket = (taskId: string) => {
  taskStore.connectWebSocket(taskId)
  ElMessage.success('已连接实时日志')
}

const removeTask = async (taskId: string) => {
  try {
    await ElMessageBox.confirm('确定要删除这个任务记录吗？', '确认删除', {
      type: 'warning'
    })
    
    taskStore.removeTask(taskId)
    ElMessage.success('任务已删除')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除任务失败:', error)
    }
  }
}

// 监听状态过滤器变化
watch(statusFilter, () => {
  handleFilterChange()
})

onMounted(() => {
  refreshTasks()
})
</script>

<style scoped>
.tasks-page {
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

.header-left h3 {
  margin: 0;
  color: #262626;
}

.task-name {
  line-height: 1.4;
}

.task-mode {
  margin-top: 4px;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: #666;
  min-width: 35px;
}

.progress-step {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.time-cell {
  line-height: 1.4;
}

.relative-time {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.task-expand {
  padding: 16px;
  background-color: #fafafa;
}

.task-params {
  margin-top: 16px;
}

.task-params h4 {
  margin: 0 0 8px 0;
  color: #262626;
  font-size: 14px;
}

.task-params pre {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
}

.task-error {
  margin-top: 16px;
}

.task-error h4 {
  margin: 0 0 8px 0;
  color: #ff4d4f;
  font-size: 14px;
}

.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

:deep(.el-progress-bar__outer) {
  height: 6px !important;
  background-color: #f0f0f0;
}

:deep(.el-progress-bar__inner) {
  border-radius: 3px;
}
</style>