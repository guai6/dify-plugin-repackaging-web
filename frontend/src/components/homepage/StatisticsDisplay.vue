<template>
  <section class="statistics-section">
    <div class="statistics-container">
      <div class="statistics-header">
        <h2 class="statistics-title">系统状态</h2>
        <p class="statistics-subtitle">实时监控系统运行状态和资源使用情况</p>
      </div>
      
      <div class="stats-grid">
        <!-- 任务统计 -->
        <div class="stat-group">
          <h3 class="stat-group-title">任务统计</h3>
          <div class="stat-cards">
            <div class="stat-card">
              <div class="stat-icon total">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ totalTasks }}</div>
                <div class="stat-label">总任务数</div>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon active">
                <el-icon><Loading /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ activeTasks.length }}</div>
                <div class="stat-label">进行中</div>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon success">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ completedTasks.length }}</div>
                <div class="stat-label">已完成</div>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon error">
                <el-icon><CircleClose /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ failedTasks.length }}</div>
                <div class="stat-label">失败</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 系统资源 -->
        <div class="stat-group">
          <h3 class="stat-group-title">系统资源</h3>
          <div class="resource-stats">
            <div class="resource-item">
              <div class="resource-header">
                <span class="resource-label">CPU使用率</span>
                <span class="resource-value">{{ formatPercent(systemStatus?.cpu_percent || 0) }}</span>
              </div>
              <div class="resource-progress">
                <el-progress
                  :percentage="systemStatus?.cpu_percent || 0"
                  :color="getResourceColor(systemStatus?.cpu_percent || 0)"
                  :show-text="false"
                />
              </div>
            </div>
            
            <div class="resource-item">
              <div class="resource-header">
                <span class="resource-label">内存使用率</span>
                <span class="resource-value">{{ formatPercent(systemStatus?.memory_percent || 0) }}</span>
              </div>
              <div class="resource-progress">
                <el-progress
                  :percentage="systemStatus?.memory_percent || 0"
                  :color="getResourceColor(systemStatus?.memory_percent || 0)"
                  :show-text="false"
                />
              </div>
            </div>
            
            <div class="resource-item">
              <div class="resource-header">
                <span class="resource-label">磁盘使用率</span>
                <span class="resource-value">{{ formatPercent(systemStatus?.disk_percent || 0) }}</span>
              </div>
              <div class="resource-progress">
                <el-progress
                  :percentage="systemStatus?.disk_percent || 0"
                  :color="getResourceColor(systemStatus?.disk_percent || 0)"
                  :show-text="false"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- 存储信息 -->
        <div class="stat-group">
          <h3 class="stat-group-title">存储信息</h3>
          <div class="storage-stats">
            <div class="storage-overview">
              <div class="storage-circle">
                <el-progress
                  type="circle"
                  :percentage="storageUsagePercent"
                  :color="getResourceColor(storageUsagePercent)"
                  :width="120"
                />
              </div>
              <div class="storage-details">
                <div class="storage-item">
                  <span class="storage-label">已用空间</span>
                  <span class="storage-value">{{ formatFileSize(storageInfo?.used_space || 0) }}</span>
                </div>
                <div class="storage-item">
                  <span class="storage-label">总空间</span>
                  <span class="storage-value">{{ formatFileSize(storageInfo?.total_space || 0) }}</span>
                </div>
                <div class="storage-item">
                  <span class="storage-label">上传文件</span>
                  <span class="storage-value">{{ storageInfo?.upload_count || 0 }} 个</span>
                </div>
                <div class="storage-item">
                  <span class="storage-label">输出文件</span>
                  <span class="storage-value">{{ storageInfo?.output_count || 0 }} 个</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="stats-actions">
        <el-button @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
        <el-button type="primary" @click="$router.push('/tasks')">
          查看任务管理
        </el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useTaskStore } from '@/stores/task'
import { useSystemStore } from '@/stores/system'
import { formatFileSize, formatPercent } from '@/utils'

const taskStore = useTaskStore()
const systemStore = useSystemStore()

// 计算属性
const totalTasks = computed(() => taskStore.totalTasks)
const activeTasks = computed(() => taskStore.activeTasks)
const completedTasks = computed(() => taskStore.completedTasks)
const failedTasks = computed(() => taskStore.failedTasks)
const systemStatus = computed(() => systemStore.systemStatus)
const storageInfo = computed(() => systemStore.storageInfo)
const loading = computed(() => systemStore.loading)

const storageUsagePercent = computed(() => {
  if (!storageInfo.value) return 0
  return Math.round((storageInfo.value.used_space / storageInfo.value.total_space) * 100)
})

// 方法
const getResourceColor = (percentage: number) => {
  if (percentage < 60) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const refreshData = async () => {
  await Promise.all([
    taskStore.fetchTasks({ limit: 100 }),
    systemStore.fetchSystemStatus(),
    systemStore.fetchStorageInfo()
  ])
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.statistics-section {
  padding: 80px 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.statistics-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.statistics-header {
  text-align: center;
  margin-bottom: 60px;
}

.statistics-title {
  font-size: 36px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 16px 0;
}

.statistics-subtitle {
  font-size: 18px;
  color: #8c8c8c;
  margin: 0;
  line-height: 1.6;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 32px;
  margin-bottom: 60px;
}

.stat-group {
  background: white;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.stat-group:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.stat-group-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 24px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: #f0f0f0;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #1890ff, #40a9ff);
}

.stat-icon.active {
  background: linear-gradient(135deg, #faad14, #ffc53d);
}

.stat-icon.success {
  background: linear-gradient(135deg, #52c41a, #73d13d);
}

.stat-icon.error {
  background: linear-gradient(135deg, #ff4d4f, #ff7875);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #262626;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
}

.resource-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.resource-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resource-label {
  font-size: 14px;
  color: #595959;
}

.resource-value {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.resource-progress {
  width: 100%;
}

.storage-stats {
  display: flex;
  flex-direction: column;
}

.storage-overview {
  display: flex;
  align-items: center;
  gap: 24px;
}

.storage-circle {
  flex-shrink: 0;
}

.storage-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.storage-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.storage-label {
  font-size: 14px;
  color: #595959;
}

.storage-value {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.stats-actions {
  text-align: center;
  display: flex;
  justify-content: center;
  gap: 16px;
}

.stats-actions .el-button {
  height: 40px;
  padding: 0 24px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .storage-overview {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .statistics-section {
    padding: 60px 0;
  }
  
  .statistics-container {
    padding: 0 16px;
  }
  
  .statistics-header {
    margin-bottom: 40px;
  }
  
  .statistics-title {
    font-size: 28px;
  }
  
  .statistics-subtitle {
    font-size: 16px;
  }
  
  .stats-grid {
    margin-bottom: 40px;
  }
  
  .stat-group {
    padding: 24px;
  }
  
  .stat-cards {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .stat-card {
    padding: 12px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .stats-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .stats-actions .el-button {
    width: 200px;
  }
}
</style>