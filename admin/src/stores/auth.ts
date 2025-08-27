import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth.service'
import type { LoginRequest, UserInfo } from '@/types/auth.types'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string | null>(null)
  const user = ref<UserInfo | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isInitialized = ref(false) // 新增：标记是否已初始化

  // 计算属性
  const isAuthenticated = computed(() => {
    // 只有在初始化完成后才检查认证状态
    if (!isInitialized.value) return false
    return !!token.value
  })

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

  const initAuth = async () => {
    console.log('🔄 开始初始化认证状态...')
    
    // 检查本地存储中的认证信息
    const savedToken = localStorage.getItem('admin_token')
    const savedUser = localStorage.getItem('admin_user')
    
    if (savedToken && savedUser) {
      try {
        // 验证token是否仍然有效
        console.log('🔍 发现本地存储的认证信息，正在验证...')
        const response = await authService.verifyToken()
        const isValid = response.valid
        
        if (isValid) {
          token.value = savedToken
          user.value = JSON.parse(savedUser)
          console.log('✅ 本地认证信息验证成功')
        } else {
          console.log('❌ 本地认证信息已过期，清除...')
          localStorage.removeItem('admin_token')
          localStorage.removeItem('admin_user')
        }
      } catch (err) {
        console.error('❌ 验证本地认证信息失败:', err)
        // 清除无效的认证信息
        localStorage.removeItem('admin_token')
        localStorage.removeItem('admin_user')
      }
    } else {
      console.log('ℹ️ 本地存储中无认证信息')
    }
    
    // 标记初始化完成
    isInitialized.value = true
    console.log('✅ 认证状态初始化完成，认证状态:', isAuthenticated.value)
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
    isInitialized,
    // 计算属性
    isAuthenticated,
    // 动作
    login,
    logout,
    initAuth,
    clearError
  }
}) 