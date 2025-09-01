<template>
  <div class="github-form">
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      @submit.prevent="handleSubmit"
    >
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="Github仓库" prop="repo">
            <el-input
              v-model="form.repo"
              placeholder="例如: junjiem/dify-plugin-tools-dbquery"
              clearable
            />
            <div class="input-help">
              支持完整URL或仓库路径格式
            </div>
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="Release标签" prop="release">
            <el-input
              v-model="form.release"
              placeholder="例如: v0.0.2"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="Assets文件名" prop="asset_name">
            <el-input
              v-model="form.asset_name"
              placeholder="例如: db_query.difypkg"
              clearable
            />
            <div class="input-help">
              必须包含.difypkg后缀
            </div>
          </el-form-item>
        </el-col>
        
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
      </el-row>
      
      <el-row :gutter="24">
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
          :loading="submitting"
          size="large"
        >
          <el-icon><Download /></el-icon>
          开始下载并重新打包
        </el-button>
        <el-button @click="resetForm" size="large">
          重置
        </el-button>
      </el-form-item>
    </el-form>
    
    <!-- 示例说明 -->
    <el-alert
      title="示例"
      type="info"
      :closable="false"
      class="example-alert"
    >
      <template #default>
        <div class="example-content">
          <p><strong>仓库:</strong> junjiem/dify-plugin-tools-dbquery</p>
          <p><strong>Release:</strong> v0.0.2</p>
          <p><strong>文件名:</strong> db_query.difypkg</p>
          <p><strong>说明:</strong> 将从 Github Release 下载指定的插件文件并重新打包</p>
        </div>
      </template>
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { isValidUrl } from '@/utils'

const emit = defineEmits<{
  submit: [params: any]
}>()

const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  repo: '',
  release: '',
  asset_name: '',
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

const rules: FormRules = {
  repo: [
    { required: true, message: '请输入Github仓库', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请输入Github仓库'))
        } else {
          // 验证是否为有效的Github仓库格式
          const githubRepoPattern = /^([a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+)$|^https:\/\/github\.com\/[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+$/
          const isUrl = value.startsWith('http')
          
          if (isUrl && !isValidUrl(value)) {
            callback(new Error('请输入有效的Github URL'))
          } else if (!isUrl && !githubRepoPattern.test(value)) {
            callback(new Error('请输入正确的仓库格式，如: owner/repo'))
          } else {
            callback()
          }
        }
      },
      trigger: 'blur'
    }
  ],
  release: [
    { required: true, message: '请输入Release标签', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  asset_name: [
    { required: true, message: '请输入Assets文件名', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请输入Assets文件名'))
        } else if (!value.endsWith('.difypkg')) {
          callback(new Error('文件名必须以.difypkg结尾'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    const params = {
      repo: form.repo,
      release: form.release,
      asset_name: form.asset_name,
      platform: form.platform || undefined,
      suffix: form.suffix || 'offline'
    }
    
    emit('submit', params)
    
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  if (!formRef.value) return
  formRef.value.resetFields()
}
</script>

<style scoped>
.github-form {
  max-width: 800px;
}

.input-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.example-alert {
  margin-top: 24px;
}

.example-content {
  line-height: 1.6;
}

.example-content p {
  margin: 4px 0;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-button) {
  margin-right: 12px;
}
</style>