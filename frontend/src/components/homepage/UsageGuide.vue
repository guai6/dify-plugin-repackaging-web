<template>
  <section class="usage-section">
    <div class="usage-container">
      <div class="usage-header">
        <h2 class="usage-title">使用指南</h2>
        <p class="usage-subtitle">简单三步，快速完成插件重新打包</p>
      </div>
      
      <div class="steps-container">
        <div
          v-for="(step, index) in steps"
          :key="step.id"
          class="step-item"
        >
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-content">
            <h3 class="step-title">{{ step.title }}</h3>
            <p class="step-description">{{ step.description }}</p>
          </div>
          
          <!-- 连接线 -->
          <div v-if="index < steps.length - 1" class="step-connector"></div>
        </div>
      </div>
      
      <div class="examples-section">
        <h3 class="examples-title">使用示例</h3>
        <div class="examples-grid">
          <div
            v-for="example in examples"
            :key="example.title"
            class="example-card"
          >
            <h4 class="example-title">{{ example.title }}</h4>
            <p class="example-description">{{ example.description }}</p>
            
            <div v-if="example.code" class="example-code">
              <pre><code>{{ example.code }}</code></pre>
            </div>
          </div>
        </div>
      </div>
      
      <div class="guide-actions">
        <el-button type="primary" size="large" @click="startUsing">
          立即开始使用
        </el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

interface GuideStep {
  id: number
  title: string
  description: string
}

interface Example {
  title: string
  description: string
  code?: string
}

const router = useRouter()

const steps: GuideStep[] = [
  {
    id: 1,
    title: '上传插件文件',
    description: '选择您需要重新打包的插件文件，支持拖拽上传或点击选择文件。系统会自动检测文件格式并进行验证。'
  },
  {
    id: 2,
    title: '配置打包参数',
    description: '根据需要选择目标平台和文件后缀。系统提供智能推荐，您也可以根据具体需求进行自定义配置。'
  },
  {
    id: 3,
    title: '下载处理结果',
    description: '系统会实时显示处理进度，完成后您可以直接下载重新打包的插件文件，并查看详细的处理日志。'
  }
]

const examples: Example[] = [
  {
    title: 'Local模式使用',
    description: '本地文件上传和处理的完整流程示例',
    code: `1. 选择本地插件文件 (.zip, .tar.gz)
2. 选择目标平台 (可选)
3. 设置文件后缀 (可选)
4. 点击上传并开始处理
5. 实时查看处理进度
6. 下载处理完成的文件`
  },
  {
    title: '任务管理',
    description: '如何有效管理您的处理任务',
    code: `• 在任务管理页面查看所有任务状态
• 支持任务取消、重试等操作
• 实时WebSocket连接显示进度
• 查看详细的任务日志和错误信息`
  },
  {
    title: '文件管理',
    description: '管理上传和输出文件的最佳实践',
    code: `• 查看所有上传的原始文件
• 管理处理完成的输出文件
• 支持文件下载和删除操作
• 监控存储空间使用情况`
  }
]

const startUsing = () => {
  router.push('/local')
}
</script>

<style scoped>
.usage-section {
  padding: 80px 0;
  background-color: #ffffff;
}

.usage-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.usage-header {
  text-align: center;
  margin-bottom: 60px;
}

.usage-title {
  font-size: 36px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 16px 0;
}

.usage-subtitle {
  font-size: 18px;
  color: #8c8c8c;
  margin: 0;
  line-height: 1.6;
}

.steps-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 80px;
  position: relative;
}

.step-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
  max-width: 300px;
}

.step-number {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #1890ff, #40a9ff);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
  position: relative;
  z-index: 2;
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 12px 0;
}

.step-description {
  font-size: 14px;
  line-height: 1.6;
  color: #595959;
  margin: 0;
}

.step-connector {
  position: absolute;
  top: 30px;
  left: calc(50% + 30px);
  right: calc(-50% + 30px);
  height: 2px;
  background: linear-gradient(90deg, #1890ff, #40a9ff);
  z-index: 1;
}

.examples-section {
  margin-bottom: 60px;
}

.examples-title {
  font-size: 28px;
  font-weight: 600;
  color: #262626;
  text-align: center;
  margin: 0 0 40px 0;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.example-card {
  background: #fafafa;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
}

.example-card:hover {
  background: #f5f5f5;
  border-color: #d9d9d9;
}

.example-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 12px 0;
}

.example-description {
  font-size: 14px;
  color: #595959;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.example-code {
  background: #262626;
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
}

.example-code pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
}

.example-code code {
  color: #f8f8f2;
  white-space: pre;
}

.guide-actions {
  text-align: center;
}

.guide-actions .el-button {
  height: 48px;
  padding: 0 32px;
  font-size: 16px;
  border-radius: 24px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .steps-container {
    flex-direction: column;
    align-items: center;
    gap: 40px;
  }
  
  .step-item {
    max-width: 500px;
  }
  
  .step-connector {
    display: none;
  }
  
  .examples-grid {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .usage-section {
    padding: 60px 0;
  }
  
  .usage-container {
    padding: 0 16px;
  }
  
  .usage-header {
    margin-bottom: 40px;
  }
  
  .usage-title {
    font-size: 28px;
  }
  
  .usage-subtitle {
    font-size: 16px;
  }
  
  .steps-container {
    margin-bottom: 60px;
    gap: 32px;
  }
  
  .step-number {
    width: 50px;
    height: 50px;
    font-size: 20px;
    margin-bottom: 20px;
  }
  
  .step-title {
    font-size: 18px;
  }
  
  .step-description {
    font-size: 13px;
  }
  
  .examples-title {
    font-size: 24px;
    margin-bottom: 32px;
  }
  
  .examples-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .example-card {
    padding: 20px;
  }
  
  .example-title {
    font-size: 16px;
  }
  
  .example-description {
    font-size: 13px;
  }
  
  .example-code {
    padding: 12px;
  }
  
  .example-code pre {
    font-size: 11px;
  }
}
</style>