import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { usersService } from '@/services/users.service'
import type { User, CreateUserRequest, UpdateUserRequest } from '@/types/users.types'

export const useUsersStore = defineStore('users', () => {
  // State
  const users = ref<User[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const searchKeyword = ref('')

  // Getters
  const filteredUsers = computed(() => {
    if (!searchKeyword.value) return users.value
    
    const keyword = searchKeyword.value.toLowerCase()
    return users.value.filter(user =>
      user.username.toLowerCase().includes(keyword) ||
      user.email.toLowerCase().includes(keyword)
    )
  })

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  const userStats = computed(() => {
    const stats = {
      total: users.value.length,
      active: 0,
      inactive: 0,
      suspended: 0
    }
    
    users.value.forEach(user => {
      if (user.status === 'active') stats.active++
      else if (user.status === 'inactive') stats.inactive++
      else if (user.status === 'suspended') stats.suspended++
    })
    
    return stats
  })

  // Actions
  const fetchUsers = async () => {
    loading.value = true
    error.value = null
    
    try {
      console.log('🔄 开始获取用户列表...', { 
        page: currentPage.value, 
        pageSize: pageSize.value, 
        search: searchKeyword.value 
      })
      
      const response = await usersService.getUsers(
        currentPage.value,
        pageSize.value,
        searchKeyword.value
      )
      
      console.log('✅ 用户API响应成功:', response)
      console.log('📊 响应数据结构:', {
        hasData: !!response.data,
        dataLength: response.data?.length || 0,
        total: response.total,
        page: response.page,
        pageSize: response.pageSize
      })
      
      if (response.data && Array.isArray(response.data)) {
        users.value = response.data
        total.value = response.total
        console.log(`✅ 用户数据更新成功: ${users.value.length} 个用户`)
      } else {
        console.warn('⚠️ 响应数据格式异常:', response)
        users.value = []
        total.value = 0
      }
      
    } catch (err: any) {
      console.error('❌ 获取用户列表失败:', err)
      console.error('错误详情:', {
        message: err.message,
        status: err.status,
        response: err.response,
        stack: err.stack
      })
      
      error.value = err.message || '获取用户列表失败'
      ElMessage.error(error.value || '获取用户列表失败')
      
      // 清空数据，避免显示旧数据
      users.value = []
      total.value = 0
    } finally {
      loading.value = false
      console.log('🔄 用户列表获取完成，loading状态:', loading.value)
    }
  }

  const createUser = async (userData: CreateUserRequest) => {
    loading.value = true
    error.value = null
    
    try {
      const newUser = await usersService.createUser(userData)
      // 重新获取用户列表以确保数据一致性
      await fetchUsers()
      ElMessage.success('用户创建成功')
      return newUser
    } catch (err: any) {
      error.value = err.message || '创建用户失败'
      ElMessage.error(error.value || '创建用户失败')
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateUser = async (userId: number, userData: UpdateUserRequest) => {
    loading.value = true
    error.value = null
    
    try {
      const updatedUser = await usersService.updateUser(userId, userData)
      // 重新获取用户列表以确保数据一致性
      await fetchUsers()
      ElMessage.success('用户信息更新成功')
      return updatedUser
    } catch (err: any) {
      error.value = err.message || '更新用户失败'
      ElMessage.error(error.value || '更新用户失败')
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateUserStatus = async (userId: number, status: string) => {
    try {
      await usersService.updateUserStatus(userId, status)
      // 重新获取用户列表以确保数据一致性
      await fetchUsers()
      ElMessage.success('用户状态更新成功')
    } catch (err: any) {
      error.value = err.message || '更新用户状态失败'
      ElMessage.error(error.value || '更新用户状态失败')
      throw err
    }
  }

  const deleteUser = async (userId: number) => {
    try {
      await usersService.deleteUser(userId)
      // 重新获取用户列表以确保数据一致性
      await fetchUsers()
      ElMessage.success('用户删除成功')
    } catch (err: any) {
      error.value = err.message || '删除用户失败'
      ElMessage.error(error.value || '删除用户失败')
      throw err
    }
  }

  const setPage = (page: number) => {
    currentPage.value = page
    fetchUsers()
  }

  const setPageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    fetchUsers()
  }

  const setSearchKeyword = (keyword: string) => {
    console.log('🔍 设置搜索关键词:', keyword)
    searchKeyword.value = keyword
    currentPage.value = 1
    // 搜索是前端过滤，不需要重新请求API
    // fetchUsers()
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    users,
    loading,
    error,
    total,
    currentPage,
    pageSize,
    searchKeyword,
    
    // Getters
    filteredUsers,
    totalPages,
    userStats,
    
    // Actions
    fetchUsers,
    createUser,
    updateUser,
    updateUserStatus,
    deleteUser,
    setPage,
    setPageSize,
    setSearchKeyword,
    clearError
  }
})
