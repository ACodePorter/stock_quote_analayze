import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth.service'
import type { LoginRequest, UserInfo } from '@/types/auth.types'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('admin_token'))
  const user = ref<UserInfo | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)

  // 动作
  const login = async (credentials: LoginRequest) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await authService.login(credentials)
      token.value = response.access_token
      user.value = response.user
      
      // 保存到本地存储
      localStorage.setItem('admin_token', response.access_token)
      localStorage.setItem('admin_user', JSON.stringify(response.user))
      
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : '登录失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      await authService.logout()
    } catch (err) {
      console.error('Logout error:', err)
      // 即使后端请求失败，也要清除本地状态
    } finally {
      // 清除状态
      token.value = null
      user.value = null
      error.value = null
      
      // 清除本地存储
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
    }
  }

  const initAuth = () => {
    const savedToken = localStorage.getItem('admin_token')
    const savedUser = localStorage.getItem('admin_user')
    
    if (savedToken && savedUser) {
      try {
        token.value = savedToken
        user.value = JSON.parse(savedUser)
      } catch (err) {
        console.error('Failed to restore auth state:', err)
        logout()
      }
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // 状态
    token,
    user,
    loading,
    error,
    // 计算属性
    isAuthenticated,
    // 动作
    login,
    logout,
    initAuth,
    clearError
  }
}) 