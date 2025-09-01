<template>
  <section class="hero-section">
    <div class="hero-container">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">{{ title }}</h1>
          <h2 class="hero-subtitle">{{ subtitle }}</h2>
          <p class="hero-description">{{ description }}</p>
          
          <div class="hero-actions">
            <el-button
              v-for="button in ctaButtons"
              :key="button.text"
              :type="button.type"
              size="large"
              @click="button.action"
              class="hero-button"
            >
              {{ button.text }}
            </el-button>
          </div>
        </div>
        
        <div class="hero-visual">
          <div class="hero-image">
            <el-icon class="hero-icon"><Box /></el-icon>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

interface CTAButton {
  text: string
  type: 'primary' | 'default'
  action: () => void
}

interface Props {
  title?: string
  subtitle?: string
  description?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Dify插件重新打包工具',
  subtitle: '简单、快速、可靠的插件打包解决方案',
  description: '支持多种来源的插件文件处理，提供便捷的本地文件上传功能，一键完成插件重新打包，让您的开发工作更加高效。'
})

const router = useRouter()

const ctaButtons: CTAButton[] = [
  {
    text: '开始使用',
    type: 'primary',
    action: () => router.push('/local')
  },
  {
    text: '了解更多',
    type: 'default',
    action: () => {
      // 滚动到产品特性区域
      const featuresSection = document.querySelector('.features-section')
      if (featuresSection) {
        featuresSection.scrollIntoView({ behavior: 'smooth' })
      }
    }
  }
]
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 600px;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.hero-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  position: relative;
  z-index: 1;
}

.hero-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

.hero-text {
  color: white;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 16px 0;
  background: linear-gradient(45deg, #ffffff, #e3f2fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 24px;
  font-weight: 500;
  line-height: 1.4;
  margin: 0 0 24px 0;
  color: rgba(255, 255, 255, 0.9);
}

.hero-description {
  font-size: 18px;
  line-height: 1.6;
  margin: 0 0 40px 0;
  color: rgba(255, 255, 255, 0.8);
}

.hero-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.hero-button {
  height: 48px;
  padding: 0 32px;
  font-size: 16px;
  border-radius: 24px;
  transition: all 0.3s ease;
}

.hero-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-image {
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: float 6s ease-in-out infinite;
}

.hero-icon {
  font-size: 120px;
  color: rgba(255, 255, 255, 0.8);
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .hero-content {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
  }
  
  .hero-title {
    font-size: 40px;
  }
  
  .hero-subtitle {
    font-size: 20px;
  }
  
  .hero-description {
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .hero-section {
    min-height: 500px;
  }
  
  .hero-container {
    padding: 0 16px;
  }
  
  .hero-title {
    font-size: 32px;
  }
  
  .hero-subtitle {
    font-size: 18px;
  }
  
  .hero-description {
    font-size: 14px;
  }
  
  .hero-actions {
    justify-content: center;
  }
  
  .hero-button {
    height: 44px;
    padding: 0 24px;
    font-size: 14px;
  }
  
  .hero-image {
    width: 200px;
    height: 200px;
  }
  
  .hero-icon {
    font-size: 80px;
  }
}
</style>