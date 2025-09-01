<template>
  <div class="settings-page">
    <!-- 头部 -->
    <el-card class="header-card">
      <div class="header-content">
        <h3>系统设置</h3>
        <el-button
          :icon="refreshing ? 'Loading' : 'Refresh'"
          :loading="refreshing"
          @click="refreshData"
        >
          刷新数据
        </el-button>
      </div>
    </el-card>
    
    <el-row :gutter="24">
      <!-- 左侧：配置设置 -->
      <el-col :span="16">
        <!-- API配置 -->
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>API配置</span>
              <el-button
                type="primary"
                size="small"
                @click="handleSaveConfig"
                :loading="saving"
              >
                保存配置
              </el-button>
            </div>
          </template>
          
          <el-form
            ref="configFormRef"
            :model="configForm"
            :rules="configRules"
            label-width="160px"
          >
            <el-form-item label="Github API URL" prop="github_api_url">
              <el-input
                v-model="configForm.github_api_url"
                placeholder="https://github.com"
              />
              <div class="form-help">
                用于从Github下载插件的API地址
              </div>
            </el-form-item>
            
            <el-form-item label="Marketplace API URL" prop="marketplace_api_url">
              <el-input
                v-model="configForm.marketplace_api_url"
                placeholder="https://marketplace.dify.ai"
              />
              <div class="form-help">
                用于从Dify Marketplace下载插件的API地址
              </div>
            </el-form-item>
            
            <el-form-item label="Pip镜像URL" prop="pip_mirror_url">
              <el-input
                v-model="configForm.pip_mirror_url"
                placeholder="https://mirrors.aliyun.com/pypi/simple"
              />
              <div class="form-help">
                用于下载Python包的镜像地址
              </div>
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- 系统信息 -->
        <el-card class="info-card">
          <template #header>
            <span>系统信息</span>
          </template>
          
          <div v-if="systemStatus" class="system-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="应用名称">
                {{ systemStatus.app_info?.name || '--' }}
              </el-descriptions-item>
              <el-descriptions-item label="应用版本">
                {{ systemStatus.app_info?.version || '--' }}
              </el-descriptions-item>
              <el-descriptions-item label="操作系统">
                {{ systemStatus.system_info?.platform || '--' }}
              </el-descriptions-item>
              <el-descriptions-item label="系统版本">
                {{ systemStatus.system_info?.platform_release || '--' }}
              </el-descriptions-item>
              <el-descriptions-item label="系统架构">
                {{ systemStatus.system_info?.architecture || '--' }}
              </el-descriptions-item>
              <el-descriptions-item label="Python版本">
                {{ systemStatus.system_info?.python_version || '--' }}
              </el-descriptions-item>
              <el-descriptions-item label="上传目录">
                {{ systemStatus.app_info?.upload_dir || '--' }}
              </el-descriptions-item>
              <el-descriptions-item label="输出目录">
                {{ systemStatus.app_info?.output_dir || '--' }}
              </el-descriptions-item>
              <el-descriptions-item label="最大文件大小" :span="2">
                {{ systemStatus.app_info?.max_file_size || '--' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
        
        <!-- 版本信息 -->
        <el-card class="version-card">
          <template #header>
            <div class="card-header">
              <span>版本信息</span>
              <el-button
                size="small"
                @click="fetchVersionInfo"
                :loading="loadingVersion"
              >
                获取版本信息
              </el-button>
            </div>
          </template>
          
          <div v-if="versionInfo" class="version-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="应用名称">
                {{ versionInfo.app_name || '--' }}
              </el-descriptions-item>
              <el-descriptions-item label="版本号">
                {{ versionInfo.version || '--' }}
              </el-descriptions-item>
              <el-descriptions-item label="构建时间">
                {{ formatTime(versionInfo.build_time) }}
              </el-descriptions-item>
              <el-descriptions-item label="Git分支">
                {{ versionInfo.git?.branch || '--' }}
              </el-descriptions-item>
              <el-descriptions-item label="Git提交">
                {{ versionInfo.git?.commit || '--' }}
              </el-descriptions-item>
              <el-descriptions-item label="Python版本">
                {{ versionInfo.python_version || '--' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：系统状态 -->
      <el-col :span="8">
        <!-- 系统资源状态 -->
        <el-card class="status-card">
          <template #header>
            <span>系统资源</span>
          </template>
          
          <div v-if="systemStatus" class="resource-status">
            <div class="resource-item">
              <div class="resource-header">
                <span class="resource-label">CPU使用率</span>
                <span class="resource-value">
                  {{ formatPercent(systemStatus.cpu_percent) }}
                </span>
              </div>
              <el-progress
                :percentage="systemStatus.cpu_percent"
                :color="getResourceColor(systemStatus.cpu_percent)"
                :show-text="false"
              />
            </div>
            
            <div class="resource-item">
              <div class="resource-header">
                <span class="resource-label">内存使用率</span>
                <span class="resource-value">
                  {{ formatPercent(systemStatus.memory_percent) }}
                </span>
              </div>
              <el-progress
                :percentage="systemStatus.memory_percent"
                :color="getResourceColor(systemStatus.memory_percent)"
                :show-text="false"
              />
            </div>
            
            <div class="resource-item">
              <div class="resource-header">
                <span class="resource-label">磁盘使用率</span>
                <span class="resource-value">
                  {{ formatPercent(systemStatus.disk_percent) }}
                </span>
              </div>
              <el-progress
                :percentage="systemStatus.disk_percent"
                :color="getResourceColor(systemStatus.disk_percent)"
                :show-text="false"
              />
            </div>
          </div>
        </el-card>
        
        <!-- 健康检查 -->
        <el-card class="health-card">
          <template #header>
            <div class="card-header">
              <span>健康检查</span>
              <el-button
                size="small"
                @click="performHealthCheck"
                :loading="loadingHealth"
              >
                检查健康状态
              </el-button>
            </div>
          </template>
          
          <div v-if="healthStatus" class="health-status">
            <div class="health-overview">
              <el-tag
                :type="getHealthType(healthStatus.status)"
                size="large"
                class="health-tag"
              >
                {{ getHealthLabel(healthStatus.status) }}
              </el-tag>
              <span class="health-time">
                {{ formatTime(healthStatus.timestamp) }}
              </span>
            </div>
            
            <div v-if="healthStatus.checks" class="health-checks">
              <h4>检查项目</h4>
              <div
                v-for="(status, key) in healthStatus.checks"
                :key="key"
                class="check-item"
              >
                <span class="check-label">{{ getCheckLabel(key) }}</span>
                <el-tag
                  :type="status ? 'success' : 'danger'"
                  size="small"
                >
                  {{ status ? '正常' : '异常' }}
                </el-tag>
              </div>
            </div>
            
            <div v-if="healthStatus.issues && healthStatus.issues.length > 0" class="health-issues">
              <h4>问题列表</h4>
              <ul>
                <li
                  v-for="issue in healthStatus.issues"
                  :key="issue"
                  class="issue-item"
                >
                  {{ issue }}
                </li>
              </ul>
            </div>
          </div>
        </el-card>
        
        <!-- 存储状态 -->
        <el-card class="storage-card">
          <template #header>
            <span>存储状态</span>
          </template>
          
          <div v-if="storageInfo" class="storage-status">
            <div class="storage-item">
              <span class="storage-label">已用空间</span>
              <span class="storage-value">
                {{ formatFileSize(storageInfo.used_space) }}
              </span>
            </div>
            <div class="storage-item">
              <span class="storage-label">总空间</span>
              <span class="storage-value">
                {{ formatFileSize(storageInfo.total_space) }}
              </span>
            </div>
            <div class="storage-item">
              <span class="storage-label">剩余空间</span>
              <span class="storage-value">
                {{ formatFileSize(storageInfo.free_space) }}
              </span>
            </div>
            
            <div class="storage-usage">
              <span class="usage-label">使用率</span>
              <el-progress
                :percentage="getStoragePercent(storageInfo)"
                :color="getResourceColor(getStoragePercent(storageInfo))"
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useSystemStore } from '@/stores/system'
import { formatTime, formatPercent, formatFileSize, isValidUrl } from '@/utils'

const systemStore = useSystemStore()

// 响应式数据
const refreshing = ref(false)
const saving = ref(false)
const loadingVersion = ref(false)
const loadingHealth = ref(false)
const versionInfo = ref<any>(null)
const healthStatus = ref<any>(null)

// 表单相关
const configFormRef = ref<FormInstance>()
const configForm = reactive({
  github_api_url: '',
  marketplace_api_url: '',
  pip_mirror_url: ''
})

const configRules: FormRules = {
  github_api_url: [
    { required: true, message: '请输入Github API URL', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!isValidUrl(value)) {
          callback(new Error('请输入有效的URL'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  marketplace_api_url: [
    { required: true, message: '请输入Marketplace API URL', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!isValidUrl(value)) {
          callback(new Error('请输入有效的URL'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  pip_mirror_url: [
    { required: true, message: '请输入Pip镜像URL', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!isValidUrl(value)) {
          callback(new Error('请输入有效的URL'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 计算属性
const systemStatus = computed(() => systemStore.systemStatus)
const apiConfig = computed(() => systemStore.apiConfig)
const storageInfo = computed(() => systemStore.storageInfo)

// 方法
const refreshData = async () => {
  refreshing.value = true
  try {
    await Promise.all([
      systemStore.fetchSystemStatus(),
      systemStore.fetchApiConfig(),
      systemStore.fetchStorageInfo()
    ])
    
    // 更新表单数据
    if (apiConfig.value) {
      Object.assign(configForm, apiConfig.value)
    }
  } finally {
    refreshing.value = false
  }
}

const handleSaveConfig = async () => {
  if (!configFormRef.value) return
  
  try {
    await configFormRef.value.validate()
    
    saving.value = true
    await systemStore.updateApiConfig(configForm)
    
    ElMessage.success('配置保存成功')
  } catch (error) {
    console.error('保存配置失败:', error)
  } finally {
    saving.value = false
  }
}

const fetchVersionInfo = async () => {
  loadingVersion.value = true
  try {
    versionInfo.value = await systemStore.getVersion()
  } finally {
    loadingVersion.value = false
  }
}

const performHealthCheck = async () => {
  loadingHealth.value = true
  try {
    healthStatus.value = await systemStore.healthCheck()
  } finally {
    loadingHealth.value = false
  }
}

const getResourceColor = (percentage: number) => {
  if (percentage < 60) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const getHealthType = (status: string) => {
  const types = {
    healthy: 'success',
    warning: 'warning',
    error: 'danger'
  }
  return types[status as keyof typeof types] || 'info'
}

const getHealthLabel = (status: string) => {
  const labels = {
    healthy: '健康',
    warning: '警告',
    error: '错误'
  }
  return labels[status as keyof typeof labels] || '未知'
}

const getCheckLabel = (key: string) => {
  const labels = {
    upload_dir: '上传目录',
    output_dir: '输出目录',
    memory_ok: '内存状态',
    disk_ok: '磁盘状态'
  }
  return labels[key as keyof typeof labels] || key
}

const getStoragePercent = (storage: any) => {
  if (!storage.total_space) return 0
  return (storage.used_space / storage.total_space) * 100
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.settings-page {
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

.header-content h3 {
  margin: 0;
  color: #262626;
}

.config-card,
.info-card,
.version-card {
  margin-bottom: 24px;
}

.status-card,
.health-card,
.storage-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.resource-status {
  space-y: 20px;
}

.resource-item {
  margin-bottom: 20px;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.resource-label {
  font-size: 14px;
  color: #606266;
}

.resource-value {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.health-status {
  padding: 8px 0;
}

.health-overview {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.health-tag {
  font-size: 14px;
}

.health-time {
  font-size: 12px;
  color: #909399;
}

.health-checks h4,
.health-issues h4 {
  margin: 16px 0 8px 0;
  font-size: 14px;
  color: #262626;
}

.check-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.check-label {
  font-size: 14px;
  color: #606266;
}

.health-issues ul {
  margin: 0;
  padding-left: 16px;
}

.issue-item {
  color: #f56c6c;
  font-size: 14px;
  margin-bottom: 4px;
}

.storage-status {
  padding: 8px 0;
}

.storage-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.storage-label {
  font-size: 14px;
  color: #606266;
}

.storage-value {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.storage-usage {
  margin-top: 16px;
}

.usage-label {
  display: block;
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-progress-bar__outer) {
  height: 8px !important;
  background-color: #f0f0f0;
}

:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}

:deep(.el-descriptions__label) {
  width: 120px;
}
</style>