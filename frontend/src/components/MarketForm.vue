<template>
  <div class="market-form">
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      @submit.prevent="handleSubmit"
    >
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="插件作者" prop="author">
            <el-input
              v-model="form.author"
              placeholder="请输入插件作者名称"
              clearable
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="插件名称" prop="name">
            <el-input
              v-model="form.name"
              placeholder="请输入插件名称"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="插件版本" prop="version">
            <el-input
              v-model="form.version"
              placeholder="例如: 1.0.0"
              clearable
            />
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
          <p><strong>作者:</strong> langgenius</p>
          <p><strong>名称:</strong> agent</p>
          <p><strong>版本:</strong> 0.0.9</p>
          <p><strong>说明:</strong> 将从 Dify Marketplace 下载 langgenius/agent v0.0.9 插件并重新打包</p>
        </div>
      </template>
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { isValidVersion } from '@/utils'

const emit = defineEmits<{
  submit: [params: any]
}>()

const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  author: '',
  name: '',
  version: '',
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
  author: [
    { required: true, message: '请输入插件作者', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入插件名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  version: [
    { required: true, message: '请输入插件版本', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请输入版本号'))
        } else if (!isValidVersion(value)) {
          callback(new Error('请输入正确的版本号格式，如: 1.0.0'))
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
      author: form.author,
      name: form.name,
      version: form.version,
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

// 填充示例数据
const fillExample = () => {
  form.author = 'langgenius'
  form.name = 'agent'
  form.version = '0.0.9'
}
</script>

<style scoped>
.market-form {
  max-width: 800px;
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