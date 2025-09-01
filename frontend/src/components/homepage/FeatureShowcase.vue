<template>
  <section class="features-section">
    <div class="features-container">
      <div class="features-header">
        <h2 class="features-title">核心功能特性</h2>
        <p class="features-subtitle">为您提供全面的插件打包解决方案</p>
      </div>
      
      <div class="features-grid">
        <div
          v-for="feature in features"
          :key="feature.id"
          class="feature-card"
          :class="{ 'feature-highlight': feature.highlight }"
        >
          <div class="feature-icon">
            <el-icon>
              <component :is="feature.icon" />
            </el-icon>
          </div>
          
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-description">{{ feature.description }}</p>
          
          <div v-if="feature.highlight" class="feature-badge">
            推荐
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
interface Feature {
  id: string
  title: string
  description: string
  icon: string
  highlight?: boolean
}

const features: Feature[] = [
  {
    id: 'local',
    title: 'Local模式',
    description: '支持本地文件上传，快速处理您的插件文件。拖拽上传，实时进度显示，操作简单便捷。',
    icon: 'Upload',
    highlight: true
  },
  {
    id: 'realtime',
    title: '实时监控',
    description: '提供实时的任务进度监控和系统状态展示，让您随时掌握处理进度和系统运行情况。',
    icon: 'Monitor'
  },
  {
    id: 'management',
    title: '任务管理',
    description: '完善的任务管理系统，支持任务查看、取消、重试等操作，让您轻松管理所有处理任务。',
    icon: 'List'
  }
]
</script>

<style scoped>
.features-section {
  padding: 80px 0;
  background-color: #fafafa;
}

.features-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.features-header {
  text-align: center;
  margin-bottom: 60px;
}

.features-title {
  font-size: 36px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 16px 0;
}

.features-subtitle {
  font-size: 18px;
  color: #8c8c8c;
  margin: 0;
  line-height: 1.6;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 32px;
}

.feature-card {
  background: white;
  padding: 40px 32px;
  border-radius: 16px;
  text-align: center;
  position: relative;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
  border-color: #1890ff;
}

.feature-highlight {
  border-color: #1890ff;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
}

.feature-highlight:hover {
  background: linear-gradient(135deg, #e6f7ff 0%, #d1f2ff 100%);
}

.feature-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  background: linear-gradient(135deg, #1890ff, #40a9ff);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  color: white;
  transition: all 0.3s ease;
}

.feature-highlight .feature-icon {
  background: linear-gradient(135deg, #52c41a, #73d13d);
}

.feature-card:hover .feature-icon {
  transform: scale(1.1);
}

.feature-title {
  font-size: 24px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 16px 0;
}

.feature-description {
  font-size: 16px;
  line-height: 1.6;
  color: #595959;
  margin: 0;
}

.feature-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  background: linear-gradient(135deg, #52c41a, #73d13d);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
  }
  
  .features-title {
    font-size: 32px;
  }
  
  .features-subtitle {
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .features-section {
    padding: 60px 0;
  }
  
  .features-container {
    padding: 0 16px;
  }
  
  .features-header {
    margin-bottom: 40px;
  }
  
  .features-title {
    font-size: 28px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .feature-card {
    padding: 32px 24px;
  }
  
  .feature-icon {
    width: 60px;
    height: 60px;
    font-size: 28px;
    margin-bottom: 20px;
  }
  
  .feature-title {
    font-size: 20px;
  }
  
  .feature-description {
    font-size: 14px;
  }
}
</style>