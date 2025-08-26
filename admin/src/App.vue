<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 在应用启动时初始化认证状态
onMounted(() => {
  console.log('🚀 应用启动，初始化认证状态...')
  authStore.initAuth()
  console.log('✅ 认证状态初始化完成，认证状态:', authStore.isAuthenticated)
})
</script>

<style scoped>
/* Main app styles */
</style>