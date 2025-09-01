<template>
  <div class="local-form">
    <el-form
      ref="formRef"
      :model="form"
      label-width="120px"
      @submit.prevent="handleSubmit"
    >
      <el-row :gutter="24">
        <el-col :span="24">
          <el-form-item label="上传文件" required>
            <el-upload
              ref="uploadRef"
              class="upload-dragger"
              drag
              :auto-upload="false"
              :show-file-list="true"
              :limit="1"
              accept=".difypkg"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :before-upload="beforeUpload"
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                将 .difypkg 文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  只能上传 .difypkg 文件，且不超过 500MB
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="目标平台">
            <el-select
              v-model="form.platform"
              placeholder="选择目标平台（可选）"
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="option in platformOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="包后缀">
            <el-input
              v-model="form.suffix"
              placeholder="默认: offline"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item>
        <el-button 
          type="primary" 
          @click="handleSubmit"
          :loading="uploading"
          :disabled="!selectedFile"
          size="large"
        >
          <el-icon><Upload /></el-icon>
          上传并重新打包
        </el-button>
        <el-button @click="resetForm" size="large">
          重置
        </el-button>
      </el-form-item>
    </el-form>
    
    <!-- 文件信息显示 -->
    <div v-if="selectedFile" class="file-info">
      <el-card>
        <template #header>
          <span>文件信息</span>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件名">
            {{ selectedFile.name }}
          </el-descriptions-item>
          <el-descriptions-item label="文件大小">
            {{ formatFileSize(selectedFile.size) }}
          </el-descriptions-item>
          <el-descriptions-item label="文件类型">
            {{ selectedFile.type || 'application/octet-stream' }}
          </el-descriptions-item>
          <el-descriptions-item label="最后修改">
            {{ formatTime(selectedFile.lastModified) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
    
    <!-- 说明 -->
    <el-alert
      title="说明"
      type="info"
      :closable="false"
      class="info-alert"
    >
      <template #default>
        <div class="info-content">
          <p>• 支持上传 .difypkg 格式的Dify插件文件</p>
          <p>• 文件大小限制为 500MB</p>
          <p>• 上传成功后将自动开始重新打包过程</p>
          <p>• 可选择目标平台进行跨平台打包</p>
        </div>
      </template>
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { FormInstance, UploadInstance, UploadProps, UploadFile } from 'element-plus'
import { formatFileSize, formatTime } from '@/utils'

const emit = defineEmits<{
  submit: [data: { file: File; platform?: string; suffix?: string }]
}>()

const formRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()
const uploading = ref(false)
const selectedFile = ref<File | null>(null)

const form = reactive({
  platform: '',
  suffix: 'offline'
})

const platformOptions = [
  { label: 'Linux x86_64', value: 'manylinux2014_x86_64' },
  { label: 'Linux aarch64', value: 'manylinux2014_aarch64' },
  { label: 'Windows x86_64', value: 'win_amd64' },
  { label: 'macOS x86_64', value: 'macosx_10_9_x86_64' },
  { label: 'macOS arm64', value: 'macosx_11_0_arm64' }
]

const handleFileChange: UploadProps['onChange'] = (file) => {
  if (file.raw) {
    selectedFile.value = file.raw
  }
}

const handleFileRemove = () => {
  selectedFile.value = null
}

const beforeUpload = (file: File) => {
  // 验证文件类型
  if (!file.name.endsWith('.difypkg')) {
    ElMessage.error('只能上传 .difypkg 文件')
    return false
  }
  
  // 验证文件大小 (500MB)
  const maxSize = 500 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 500MB')
    return false
  }
  
  selectedFile.value = file
  return false // 阻止自动上传
}

const handleSubmit = async () => {
  if (!selectedFile.value) {
    ElMessage.error('请先选择要上传的文件')
    return
  }
  
  uploading.value = true
  
  try {
    const data = {
      file: selectedFile.value,
      platform: form.platform || undefined,
      suffix: form.suffix || 'offline'
    }
    
    emit('submit', data)
    
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    uploading.value = false
  }
}

const resetForm = () => {
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  selectedFile.value = null
  form.platform = ''
  form.suffix = 'offline'
}
</script>

<style scoped>
.local-form {
  max-width: 800px;
}

.upload-dragger {
  width: 100%;
}

.upload-dragger :deep(.el-upload-dragger) {
  width: 100%;
  height: 180px;
}

.file-info {
  margin: 24px 0;
}

.info-alert {
  margin-top: 24px;
}

.info-content {
  line-height: 1.6;
}

.info-content p {
  margin: 4px 0;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-button) {
  margin-right: 12px;
}

:deep(.el-upload__tip) {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
}
</style>