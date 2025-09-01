<template>
  <div class="local-mode-page">
    <div class="page-header">
      <h1>Local模式</h1>
      <p>上传本地插件文件进行重新打包处理</p>
    </div>
    
    <div class="local-form-container">
      <LocalForm @submit="handleSubmit" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useTaskStore } from '@/stores/task'
import LocalForm from '@/components/LocalForm.vue'

const router = useRouter()
const taskStore = useTaskStore()

const handleSubmit = async (data: { file: File; platform?: string; suffix?: string }) => {
  try {
    const response = await taskStore.uploadFile(data.file, data.platform, data.suffix)
    if (response) {
      router.push(`/tasks/${response.task_id}`)
    }
  } catch (error) {
    console.error('文件上传失败:', error)
  }
}
</script>

<style scoped>
.local-mode-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  color: #262626;
  margin-bottom: 8px;
}

.page-header p {
  font-size: 16px;
  color: #8c8c8c;
  margin: 0;
}

.local-form-container {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>