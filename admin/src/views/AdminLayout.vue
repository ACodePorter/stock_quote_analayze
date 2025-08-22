<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="admin-sidebar">
      <div class="sidebar-header">
        <h2 class="text-xl font-bold text-gray-900">📊 管理后台</h2>
        <p class="text-sm text-gray-600">{{ user?.username || '管理员' }}</p>
      </div>
      
      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
        >
          <el-icon class="nav-icon">
            <component :is="item.icon" />
          </el-icon>
          <span class="nav-text">{{ item.name }}</span>
        </router-link>
      </nav>
      
      <div class="sidebar-footer">
        <el-button
          type="danger"
          size="small"
          class="w-full"
          @click="handleLogout"
        >
          退出登录
        </el-button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="admin-main">
      <!-- 头部 -->
      <header class="admin-header">
        <div class="header-left">
          <h1 class="text-2xl font-bold text-gray-900">{{ currentPageTitle }}</h1>
          <div class="breadcrumb">
            <span>管理后台</span>
            <span>/</span>
            <span>{{ currentPageTitle }}</span>
          </div>
        </div>
        
        <div class="header-right">
          <div class="user-menu">
            <span class="user-name">{{ user?.username || '管理员' }}</span>
            <el-avatar :size="32" class="user-avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <div class="admin-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import {
  DataBoard,
  Document,
  User,
  TrendCharts,
  Setting,
  DataAnalysis,
  Monitor,
  Cpu,
  DocumentCopy,
  Bell
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 菜单项配置
const menuItems = [
  { path: '/dashboard', name: '仪表板', icon: DataBoard },
  { path: '/users', name: '用户管理', icon: User },
  { path: '/quotes', name: '行情数据', icon: TrendCharts },
  { path: '/datasource', name: '数据源配置', icon: Setting },
  { path: '/datacollect', name: '数据采集', icon: DataAnalysis },
  { path: '/monitoring', name: '系统监控', icon: Monitor },
  { path: '/models', name: '预测模型', icon: Cpu },
  { path: '/logs', name: '系统日志', icon: Document },
  { path: '/content', name: '内容管理', icon: DocumentCopy },
  { path: '/announcements', name: '公告发布', icon: Bell }
]

// 计算属性
const user = computed(() => authStore.user)

const currentPageTitle = computed(() => {
  const currentItem = menuItems.find(item => item.path === route.path)
  return currentItem?.name || '页面'
})

// 方法
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await authStore.logout()
    router.push('/login')
  } catch (err) {
    // 用户取消
  }
}
</script>

<style scoped>
.admin-layout {
  @apply min-h-screen bg-gray-50;
}

.admin-sidebar {
  @apply fixed left-0 top-0 h-full w-64 bg-white shadow-lg z-50;
}

.sidebar-header {
  @apply p-6 border-b border-gray-200;
}

.sidebar-nav {
  @apply flex-1 p-4 space-y-2;
}

.nav-item {
  @apply flex items-center px-4 py-3 text-gray-700 rounded-lg transition-colors hover:bg-gray-100;
  text-decoration: none;
}

.nav-item.active {
  @apply bg-blue-50 text-blue-700;
  text-decoration: none;
}

.nav-icon {
  @apply mr-3 text-lg;
}

.nav-text {
  @apply font-medium;
  text-decoration: none;
}

/* 确保所有导航链接都没有下划线 */
.nav-item,
.nav-item:hover,
.nav-item:focus,
.nav-item:active,
.nav-item.router-link-active,
.nav-item.router-link-exact-active {
  text-decoration: none !important;
}

.sidebar-footer {
  @apply p-4 border-t border-gray-200;
}

.admin-main {
  @apply ml-64 min-h-screen;
}

.admin-header {
  @apply bg-white shadow-sm border-b border-gray-200 px-6 py-4 flex justify-between items-center;
}

.header-left {
  @apply flex flex-col;
}

.breadcrumb {
  @apply text-sm text-gray-500 mt-1;
}

.header-right {
  @apply flex items-center;
}

.user-menu {
  @apply flex items-center space-x-3;
}

.user-name {
  @apply text-sm font-medium text-gray-700;
}

.user-avatar {
  @apply bg-gray-300;
}
</style> 