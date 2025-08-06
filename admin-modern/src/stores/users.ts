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
      const response = await usersService.getUsers(
        currentPage.value,
        pageSize.value,
        searchKeyword.value
      )
      users.value = response.data
      total.value = response.total
    } catch (err: any) {
      error.value = err.message || '获取用户列表失败'
      ElMessage.error(error.value)
    } finally {
      loading.value = false
    }
  }

  const createUser = async (userData: CreateUserRequest) => {
    loading.value = true
    error.value = null
    
    try {
      const newUser = await usersService.createUser(userData)
      users.value.unshift(newUser)
      total.value++
      ElMessage.success('用户创建成功')
      return newUser
    } catch (err: any) {
      error.value = err.message || '创建用户失败'
      ElMessage.error(error.value)
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
      const index = users.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        users.value[index] = updatedUser
      }
      ElMessage.success('用户信息更新成功')
      return updatedUser
    } catch (err: any) {
      error.value = err.message || '更新用户失败'
      ElMessage.error(error.value)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateUserStatus = async (userId: number, status: string) => {
    try {
      await usersService.updateUserStatus(userId, status)
      const user = users.value.find(u => u.id === userId)
      if (user) {
        user.status = status as 'active' | 'inactive' | 'suspended'
      }
      ElMessage.success('用户状态更新成功')
    } catch (err: any) {
      error.value = err.message || '更新用户状态失败'
      ElMessage.error(error.value)
      throw err
    }
  }

  const deleteUser = async (userId: number) => {
    try {
      await usersService.deleteUser(userId)
      const index = users.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        users.value.splice(index, 1)
        total.value--
      }
      ElMessage.success('用户删除成功')
    } catch (err: any) {
      error.value = err.message || '删除用户失败'
      ElMessage.error(error.value)
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
    searchKeyword.value = keyword
    currentPage.value = 1
    fetchUsers()
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
