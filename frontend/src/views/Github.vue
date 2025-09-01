<template>
  <div class="github-mode-page">
    <div class="page-header">
      <h1>Github模式</h1>
      <p>从Github仓库下载插件进行重新打包处理</p>
    </div>
    
    <div class="github-form-container">
      <GithubForm @submit="handleSubmit" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useTaskStore } from '@/stores/task'
import GithubForm from '@/components/GithubForm.vue'

const router = useRouter()
const taskStore = useTaskStore()

const handleSubmit = async (params: any) => {
  try {
    const task = await taskStore.createGithubTask(params)
    if (task) {
      router.push(`/tasks/${task.task_id}`)
    }
  } catch (error) {
    console.error('Github任务创建失败:', error)
  }
}
</script>

<style scoped>
.github-mode-page {
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

.github-form-container {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>