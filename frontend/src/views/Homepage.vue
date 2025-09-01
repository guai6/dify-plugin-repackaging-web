<template>
  <div class="homepage">
    <!-- Hero区域 -->
    <HeroSection />
    
    <!-- 产品特性展示 -->
    <FeatureShowcase />
    
    <!-- 使用指南 -->
    <UsageGuide />
    
    <!-- 统计展示 -->
    <StatisticsDisplay />
  </div>
</template>

<script setup lang="ts">
import HeroSection from '@/components/homepage/HeroSection.vue'
import FeatureShowcase from '@/components/homepage/FeatureShowcase.vue'
import UsageGuide from '@/components/homepage/UsageGuide.vue'
import StatisticsDisplay from '@/components/homepage/StatisticsDisplay.vue'

// Import homepage styles
import '@/styles/homepage.scss'
</script>

<style scoped>
.homepage {
  min-height: 100vh;
  background-color: #ffffff;
}

/* 全局样式优化 */
:deep(.el-button) {
  transition: all 0.3s ease;
}

:deep(.el-button:hover) {
  transform: translateY(-1px);
}

:deep(.el-progress-bar__outer) {
  border-radius: 10px;
}

:deep(.el-progress-bar__inner) {
  border-radius: 10px;
}

:deep(.el-card) {
  transition: all 0.3s ease;
}

/* 滚动行为优化 */
html {
  scroll-behavior: smooth;
}

/* 响应式字体大小 */
@media (max-width: 768px) {
  .homepage {
    font-size: 14px;
  }
}
</style>