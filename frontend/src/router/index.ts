import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Homepage',
      component: () => import('@/views/Homepage.vue'),
      meta: { title: '首页' }
    },
    {
      path: '/local',
      name: 'LocalMode',
      component: () => import('@/views/LocalMode.vue'),
      meta: { title: 'Local模式' }
    },
    {
      path: '/tasks',
      name: 'Tasks',
      component: () => import('@/views/Tasks.vue'),
      meta: { title: '任务管理' }
    },
    {
      path: '/tasks/:id',
      name: 'TaskDetail',
      component: () => import('@/views/TaskDetail.vue'),
      meta: { title: '任务详情' }
    },
    {
      path: '/files',
      name: 'Files',
      component: () => import('@/views/Files.vue'),
      meta: { title: '文件管理' }
    },
    // Keep existing routes but mark as hidden
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { title: '控制台', hidden: true }
    },
    {
      path: '/market',
      name: 'Market',
      component: () => import('@/views/Market.vue'),
      meta: { title: 'Market模式', hidden: true }
    },
    {
      path: '/github',
      name: 'Github',
      component: () => import('@/views/Github.vue'),
      meta: { title: 'Github模式', hidden: true }
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('@/views/Settings.vue'),
      meta: { title: '系统设置', hidden: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue'),
      meta: { title: '页面未找到' }
    }
  ]
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - Dify插件重新打包工具`
  }
  next()
})

export default router