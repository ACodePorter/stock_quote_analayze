import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/views/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue')
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('@/views/LogsView.vue')
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/UsersView.vue')
      },
      {
        path: 'quotes',
        name: 'Quotes',
        component: () => import('@/views/QuotesView.vue')
      },
      {
        path: 'datasource',
        name: 'DataSource',
        component: () => import('@/views/DataSourceView.vue')
      },
      {
        path: 'datacollect',
        name: 'DataCollect',
        component: () => import('@/views/DataCollectView.vue')
      },
      {
        path: 'monitoring',
        name: 'Monitoring',
        component: () => import('@/views/MonitoringView.vue')
      },
      {
        path: 'models',
        name: 'Models',
        component: () => import('@/views/ModelsView.vue')
      },
      {
        path: 'content',
        name: 'Content',
        component: () => import('@/views/ContentView.vue')
      },
      {
        path: 'announcements',
        name: 'Announcements',
        component: () => import('@/views/AnnouncementsView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router 