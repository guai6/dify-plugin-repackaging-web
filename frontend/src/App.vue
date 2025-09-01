<template>
  <div id="app">
    <el-container class="layout">
      <!-- 顶部导航栏 -->
      <el-header class="top-header">
        <div class="header-content">
          <!-- Logo区域 -->
          <div class="logo-section" @click="$router.push('/')">
            <h2>Dify插件打包工具</h2>
          </div>
          
          <!-- 导航菜单 -->
          <div class="nav-section">
            <el-menu
              :default-active="$route.path"
              mode="horizontal"
              router
              class="top-menu"
              background-color="transparent"
              text-color="#262626"
              active-text-color="#1890ff"
            >
              <el-menu-item index="/">
                <el-icon><House /></el-icon>
                <span>首页</span>
              </el-menu-item>
              
              <el-menu-item index="/local">
                <el-icon><Upload /></el-icon>
                <span>Local模式</span>
              </el-menu-item>
              
              <el-menu-item index="/tasks">
                <el-icon><List /></el-icon>
                <span>任务管理</span>
              </el-menu-item>
              
              <el-menu-item index="/files">
                <el-icon><Folder /></el-icon>
                <span>文件管理</span>
              </el-menu-item>
            </el-menu>
          </div>
          
          <!-- 系统状态区域 -->
          <div class="status-section">
            <el-space>
              <!-- 系统状态指示器 -->
              <el-tooltip content="系统状态" placement="bottom">
                <el-badge
                  :value="activeTasks"
                  :hidden="activeTasks === 0"
                  class="status-badge"
                >
                  <el-button
                    :type="systemHealthy ? 'success' : 'danger'"
                    :icon="systemHealthy ? 'CircleCheck' : 'CircleClose'"
                    circle
                    size="small"
                    @click="checkSystemHealth"
                  />
                </el-badge>
              </el-tooltip>
              
              <!-- 刷新按钮 -->
              <el-tooltip content="刷新数据" placement="bottom">
                <el-button
                  :icon="refreshing ? 'Loading' : 'Refresh'"
                  :loading="refreshing"
                  circle
                  size="small"
                  @click="refreshData"
                />
              </el-tooltip>
            </el-space>
          </div>
          
          <!-- 移动端菜单按钮 -->
          <div class="mobile-menu-btn">
            <el-button
              :icon="mobileMenuOpen ? 'Close' : 'Menu'"
              circle
              size="small"
              @click="toggleMobileMenu"
            />
          </div>
        </div>
        
        <!-- 移动端菜单 -->
        <div v-show="mobileMenuOpen" class="mobile-menu">
          <el-menu
            :default-active="$route.path"
            router
            class="mobile-nav-menu"
            @select="closeMobileMenu"
          >
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </el-menu-item>
            
            <el-menu-item index="/local">
              <el-icon><Upload /></el-icon>
              <span>Local模式</span>
            </el-menu-item>
            
            <el-menu-item index="/tasks">
              <el-icon><List /></el-icon>
              <span>任务管理</span>
            </el-menu-item>
            
            <el-menu-item index="/files">
              <el-icon><Folder /></el-icon>
              <span>文件管理</span>
            </el-menu-item>
          </el-menu>
        </div>
      </el-header>
      
      <!-- 页面内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTaskStore } from '@/stores/task'
import { useSystemStore } from '@/stores/system'

const route = useRoute()
const taskStore = useTaskStore()
const systemStore = useSystemStore()

const refreshing = ref(false)
const systemHealthy = ref(true)
const mobileMenuOpen = ref(false)

// 计算活跃任务数量
const activeTasks = computed(() => taskStore.activeTasks.length)

// 检查系统健康状态
const checkSystemHealth = async () => {
  try {
    const health = await systemStore.healthCheck()
    systemHealthy.value = health.status === 'healthy'
  } catch (error) {
    systemHealthy.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  refreshing.value = true
  try {
    await Promise.all([
      taskStore.fetchTasks(),
      systemStore.fetchSystemStatus(),
      systemStore.fetchStorageInfo()
    ])
  } catch (error) {
    console.error('刷新数据失败:', error)
  } finally {
    refreshing.value = false
  }
}

// 移动端菜单控制
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

// 定期检查系统状态
let healthCheckInterval: NodeJS.Timeout

onMounted(async () => {
  // 初始化数据
  await refreshData()
  
  // 定期检查系统健康状态
  healthCheckInterval = setInterval(checkSystemHealth, 30000) // 30秒检查一次
})

onUnmounted(() => {
  // 清理定时器
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval)
  }
  
  // 断开所有WebSocket连接
  taskStore.disconnectAllWebSockets()
})
</script>

<style scoped>
.layout {
  height: 100vh;
  background-color: #f0f2f5;
}

/* 顶部导航栏 */
.top-header {
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 64px;
  padding: 0;
  position: relative;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Logo区域 */
.logo-section {
  cursor: pointer;
  transition: opacity 0.3s ease;
}

.logo-section:hover {
  opacity: 0.8;
}

.logo-section h2 {
  color: #262626;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

/* 导航菜单 */
.nav-section {
  flex: 1;
  display: flex;
  justify-content: center;
  max-width: 600px;
}

.top-menu {
  border-bottom: none;
  background: transparent;
}

:deep(.top-menu .el-menu-item) {
  border-bottom: 2px solid transparent;
  margin: 0 8px;
  border-radius: 6px 6px 0 0;
  transition: all 0.3s ease;
}

:deep(.top-menu .el-menu-item:hover) {
  background-color: #f0f2f5;
  color: #1890ff;
}

:deep(.top-menu .el-menu-item.is-active) {
  border-bottom-color: #1890ff;
  background-color: #e6f7ff;
  color: #1890ff;
}

:deep(.top-menu .el-menu-item span) {
  margin-left: 8px;
}

/* 系统状态区域 */
.status-section {
  display: flex;
  align-items: center;
}

.status-badge {
  margin-right: 8px;
}

/* 移动端菜单按钮 */
.mobile-menu-btn {
  display: none;
}

/* 移动端菜单 */
.mobile-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.mobile-nav-menu {
  border-right: none;
}

:deep(.mobile-nav-menu .el-menu-item) {
  padding-left: 24px;
}

/* 主内容区域 */
.main-content {
  padding: 24px;
  background-color: #f0f2f5;
  overflow-y: auto;
  height: calc(100vh - 64px);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-content {
    padding: 0 16px;
  }
  
  .logo-section h2 {
    font-size: 16px;
  }
  
  :deep(.top-menu .el-menu-item span) {
    display: none;
  }
  
  :deep(.top-menu .el-menu-item) {
    margin: 0 4px;
    min-width: 48px;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .nav-section {
    display: none;
  }
  
  .mobile-menu-btn {
    display: block;
  }
  
  .status-section {
    margin-right: 8px;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .logo-section h2 {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 0 12px;
  }
  
  .main-content {
    padding: 12px;
  }
  
  .status-section :deep(.el-space) {
    gap: 4px !important;
  }
}

/* 全局样式 */
:deep(.el-card) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.el-table) {
  border-radius: 8px;
}

:deep(.el-button) {
  border-radius: 6px;
}

:deep(.el-input) {
  border-radius: 6px;
}

/* 平滑过渡动画 */
* {
  transition: all 0.3s ease;
}

/* 导航菜单动画 */
:deep(.el-menu-item) {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 移动端菜单动画 */
.mobile-menu {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>