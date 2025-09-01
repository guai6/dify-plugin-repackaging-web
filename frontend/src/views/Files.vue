<template>
  <div class="files-page">
    <!-- 头部操作栏 -->
    <el-card class="header-card">
      <div class="header-content">
        <div class="header-left">
          <h3>文件管理</h3>
          <el-tag type="info">
            {{ files.length }} 个文件
          </el-tag>
        </div>
        <div class="header-right">
          <el-space>
            <el-input
              v-model="searchText"
              placeholder="搜索文件名"
              style="width: 200px"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            
            <el-select
              v-model="fileTypeFilter"
              placeholder="文件类型"
              style="width: 150px"
              @change="handleFilterChange"
            >
              <el-option label="全部文件" value="all" />
              <el-option label="输入文件" value="input" />
              <el-option label="输出文件" value="output" />
            </el-select>
            
            <el-select
              v-model="sortBy"
              placeholder="排序方式"
              style="width: 150px"
              @change="handleSortChange"
            >
              <el-option label="创建时间" value="created_at" />
              <el-option label="文件名" value="name" />
              <el-option label="文件大小" value="size" />
            </el-select>
            
            <el-button
              :icon="sortOrder === 'asc' ? 'Sort' : 'SortDown'"
              @click="toggleSortOrder"
            >
              {{ sortOrder === 'asc' ? '升序' : '降序' }}
            </el-button>
            
            <el-button
              :icon="refreshing ? 'Loading' : 'Refresh'"
              :loading="refreshing"
              @click="refreshFiles"
            >
              刷新
            </el-button>
            
            <el-button
              type="warning"
              @click="handleCleanup"
            >
              清理临时文件
            </el-button>
          </el-space>
        </div>
      </div>
    </el-card>
    
    <!-- 存储信息 -->
    <el-row :gutter="24" class="storage-section">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">
              {{ formatFileSize(storageInfo?.used_space || 0) }}
            </div>
            <div class="stat-label">已用空间</div>
          </div>
          <div class="stat-icon">
            <el-icon><HardDisk /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">
              {{ formatFileSize(storageInfo?.total_space || 0) }}
            </div>
            <div class="stat-label">总空间</div>
          </div>
          <div class="stat-icon">
            <el-icon><HardDisk /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ storageInfo?.upload_count || 0 }}</div>
            <div class="stat-label">上传文件</div>
          </div>
          <div class="stat-icon">
            <el-icon><Upload /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ storageInfo?.output_count || 0 }}</div>
            <div class="stat-label">输出文件</div>
          </div>
          <div class="stat-icon">
            <el-icon><Download /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 文件列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="table-header">
          <span>文件列表</span>
          <div class="table-actions">
            <el-space v-if="selectedFiles.length > 0">
              <el-button
                type="primary"
                size="small"
                @click="handleBatchDownload"
              >
                批量下载 ({{ selectedFiles.length }})
              </el-button>
              
              <el-button
                type="danger"
                size="small"
                @click="handleBatchDelete"
              >
                批量删除 ({{ selectedFiles.length }})
              </el-button>
            </el-space>
          </div>
        </div>
      </template>
      
      <el-table
        v-loading="fileStore.loading"
        :data="filteredFiles"
        stripe
        @selection-change="handleSelectionChange"
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column label="文件名" min-width="300">
          <template #default="{ row }">
            <div class="file-name">
              <el-icon class="file-icon">
                <component :is="getFileIcon(row.name)" />
              </el-icon>
              <span class="name">{{ row.name }}</span>
              <el-tag
                v-if="row.type"
                :type="getFileTypeTag(row.type)"
                size="small"
                class="file-type-tag"
              >
                {{ getFileTypeLabel(row.type) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
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
        
        <el-table-column label="关联任务" width="150">
          <template #default="{ row }">
            <el-link
              v-if="row.task_id"
              type="primary"
              @click="goToTask(row.task_id)"
            >
              查看任务
            </el-link>
            <span v-else class="no-task">--</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button
                size="small"
                type="primary"
                @click="handleDownload(row)"
              >
                下载
              </el-button>
              
              <el-button
                size="small"
                @click="handlePreview(row)"
              >
                预览
              </el-button>
              
              <el-button
                size="small"
                type="danger"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 文件预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      :title="`文件预览 - ${previewFile?.name}`"
      width="80%"
      :before-close="handlePreviewClose"
    >
      <div v-if="previewFile" class="file-preview">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件名">
            {{ previewFile.name }}
          </el-descriptions-item>
          <el-descriptions-item label="文件大小">
            {{ formatFileSize(previewFile.size) }}
          </el-descriptions-item>
          <el-descriptions-item label="文件类型">
            {{ getFileTypeLabel(previewFile.type) }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatTime(previewFile.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="文件路径" :span="2">
            <div class="file-path">
              {{ previewFile.path }}
              <el-button
                size="small"
                @click="copyPath(previewFile.path)"
              >
                复制路径
              </el-button>
            </div>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 文件内容预览 -->
        <div v-if="isTextFile(previewFile.name)" class="file-content-preview">
          <el-divider>文件内容</el-divider>
          <div v-loading="loadingContent" class="content-container">
            <el-input
              v-if="fileContent"
              v-model="fileContent"
              type="textarea"
              :rows="15"
              readonly
              class="content-textarea"
            />
            <div v-else-if="!loadingContent" class="no-content">
              无法预览该文件类型或文件为空
            </div>
          </div>
        </div>
        
        <div v-else class="unsupported-preview">
          <el-divider>文件内容</el-divider>
          <el-alert
            title="不支持预览"
            type="info"
            description="该文件类型不支持在线预览，请下载后查看。"
            show-icon
            :closable="false"
          />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button
          type="primary"
          @click="handleDownload(previewFile)"
        >
          下载文件
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFileStore } from '@/stores/file'
import { useSystemStore } from '@/stores/system'
import { 
  formatFileSize, 
  formatTime, 
  formatRelativeTime,
  getFileTypeIcon,
  copyToClipboard
} from '@/utils'
import type { FileInfo } from '@/types'

const router = useRouter()
const fileStore = useFileStore()
const systemStore = useSystemStore()

// 响应式数据
const refreshing = ref(false)
const fileTypeFilter = ref('all')
const searchText = ref('')
const sortBy = ref('created_at')
const sortOrder = ref<'asc' | 'desc'>('desc')
const selectedFiles = ref<FileInfo[]>([])
const previewVisible = ref(false)
const previewFile = ref<FileInfo | null>(null)
const fileContent = ref('')
const loadingContent = ref(false)

// 计算属性
const files = computed(() => fileStore.files)
const storageInfo = computed(() => systemStore.storageInfo)

const filteredFiles = computed(() => {
  let result = files.value
  
  // 文件类型过滤
  if (fileTypeFilter.value !== 'all') {
    result = result.filter(file => file.type === fileTypeFilter.value)
  }
  
  // 搜索过滤
  if (searchText.value.trim()) {
    const searchLower = searchText.value.toLowerCase().trim()
    result = result.filter(file => 
      file.name.toLowerCase().includes(searchLower)
    )
  }
  
  // 排序
  result = result.sort((a, b) => {
    let aValue: any
    let bValue: any
    
    switch (sortBy.value) {
      case 'name':
        aValue = a.name.toLowerCase()
        bValue = b.name.toLowerCase()
        break
      case 'size':
        aValue = a.size
        bValue = b.size
        break
      case 'created_at':
      default:
        aValue = new Date(a.created_at).getTime()
        bValue = new Date(b.created_at).getTime()
        break
    }
    
    if (sortOrder.value === 'asc') {
      return aValue > bValue ? 1 : -1
    } else {
      return aValue < bValue ? 1 : -1
    }
  })
  
  return result
})

// 方法
const refreshFiles = async () => {
  refreshing.value = true
  try {
    await Promise.all([
      fileStore.fetchFiles(fileTypeFilter.value),
      systemStore.fetchStorageInfo()
    ])
  } finally {
    refreshing.value = false
  }
}

const handleFilterChange = () => {
  // 文件类型过滤变化时重新获取数据
  refreshFiles()
}

const handleSearch = () => {
  // 搜索时不需要重新获取数据，由计算属性自动过滤
}

const handleSortChange = () => {
  // 排序方式变化时不需要重新获取数据
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

const handleSelectionChange = (selection: FileInfo[]) => {
  selectedFiles.value = selection
}

const handleDownload = (file: FileInfo) => {
  fileStore.downloadFile(file.type, file.name)
}

const handlePreview = async (file: FileInfo) => {
  previewFile.value = file
  previewVisible.value = true
  fileContent.value = ''
  
  // 如果是文本文件，加载文件内容
  if (isTextFile(file.name)) {
    await loadFileContent(file)
  }
}

const handlePreviewClose = () => {
  previewVisible.value = false
  previewFile.value = null
  fileContent.value = ''
  loadingContent.value = false
}

const isTextFile = (filename: string) => {
  const textExtensions = [
    '.txt', '.md', '.json', '.xml', '.html', '.css', '.js', '.ts', 
    '.vue', '.py', '.java', '.cpp', '.c', '.h', '.log', '.yml', '.yaml',
    '.ini', '.conf', '.config', '.sh', '.bat', '.dockerfile', '.gitignore'
  ]
  const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'))
  return textExtensions.includes(ext)
}

const loadFileContent = async (file: FileInfo) => {
  try {
    loadingContent.value = true
    
    // 检查文件大小，太大的文件不加载内容
    if (file.size > 1024 * 1024) { // 1MB
      fileContent.value = '文件过大（超过1MB），不支持在线预览，请下载后查看。'
      return
    }
    
    const response = await fetch(
      fileApi.getFileContentUrl(file.type, file.name),
      { method: 'GET' }
    )
    
    if (response.ok) {
      const content = await response.text()
      fileContent.value = content
    } else {
      fileContent.value = '无法加载文件内容'
    }
  } catch (error) {
    console.error('加载文件内容失败:', error)
    fileContent.value = '加载文件内容失败'
  } finally {
    loadingContent.value = false
  }
}

const handleDelete = async (file: FileInfo) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 "${file.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await fileStore.deleteFile(file.type, file.name)
    await refreshFiles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文件失败:', error)
    }
  }
}

const handleBatchDownload = async () => {
  try {
    if (selectedFiles.value.length === 0) {
      ElMessage.warning('请选择要下载的文件')
      return
    }
    
    ElMessage.info(`开始下载 ${selectedFiles.value.length} 个文件...`)
    
    // 逐个下载文件，避免浏览器阻止多个下载
    for (const file of selectedFiles.value) {
      await new Promise(resolve => {
        fileStore.downloadFile(file.type, file.name)
        // 稍微延时避免浏览器下载限制
        setTimeout(resolve, 500)
      })
    }
    
    ElMessage.success('批量下载完成')
    selectedFiles.value = []
  } catch (error) {
    console.error('批量下载失败:', error)
    ElMessage.error('批量下载失败')
  }
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedFiles.value.length} 个文件吗？`,
      '确认批量删除',
      { type: 'warning' }
    )
    
    const deletePromises = selectedFiles.value.map(file =>
      fileStore.deleteFile(file.type, file.name)
    )
    
    await Promise.all(deletePromises)
    selectedFiles.value = []
    await refreshFiles()
    
    ElMessage.success('批量删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
    }
  }
}

const handleCleanup = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清理临时文件吗？这将删除超过24小时的临时文件。',
      '确认清理',
      { type: 'warning' }
    )
    
    await fileStore.cleanupTempFiles()
    await refreshFiles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清理失败:', error)
    }
  }
}

const goToTask = (taskId: string) => {
  router.push(`/tasks/${taskId}`)
}

const getFileIcon = (filename: string) => {
  return getFileTypeIcon(filename)
}

const getFileTypeTag = (type: string) => {
  const tags = {
    input: '',
    output: 'success',
    temp: 'warning'
  }
  return tags[type as keyof typeof tags] || ''
}

const getFileTypeLabel = (type: string) => {
  const labels = {
    input: '输入文件',
    output: '输出文件',
    temp: '临时文件'
  }
  return labels[type as keyof typeof labels] || type
}

const copyPath = (path: string) => {
  copyToClipboard(path)
}

onMounted(() => {
  refreshFiles()
})
</script>

<style scoped>
.files-page {
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

.storage-section {
  margin-bottom: 24px;
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
  font-size: 20px;
  font-weight: bold;
  color: #262626;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
}

.stat-icon {
  font-size: 32px;
  color: #d9d9d9;
  opacity: 0.8;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  color: #8c8c8c;
}

.name {
  flex: 1;
  word-break: break-all;
}

.file-type-tag {
  margin-left: 8px;
}

.time-cell {
  line-height: 1.4;
}

.relative-time {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.no-task {
  color: #c0c4cc;
}

.file-preview {
  margin-bottom: 16px;
}

.file-path {
  display: flex;
  align-items: center;
  gap: 8px;
  word-break: break-all;
}

.file-content-preview {
  margin-top: 20px;
}

.content-container {
  min-height: 200px;
}

.content-textarea {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.content-textarea :deep(.el-textarea__inner) {
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
  background-color: #fafafa;
  border: 1px solid #e6e6e6;
}

.no-content {
  text-align: center;
  color: #999;
  padding: 40px;
  background-color: #fafafa;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
}

.unsupported-preview {
  margin-top: 20px;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

:deep(.el-descriptions__label) {
  width: 100px;
}
</style>