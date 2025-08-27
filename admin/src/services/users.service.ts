import { apiService } from './api'
import type { User, CreateUserRequest, UpdateUserRequest, UsersResponse } from '@/types/users.types'

export class UsersService {
  async getUsers(page = 1, pageSize = 20, search?: string): Promise<UsersResponse> {
    const params = new URLSearchParams({
      skip: ((page - 1) * pageSize).toString(),
      limit: pageSize.toString()
    })
    
    if (search) {
      params.append('search', search)
    }
    
    const url = `/users?${params}`
    console.log('🌐 调用用户API:', url)
    console.log('📋 请求参数:', { page, pageSize, search, skip: (page - 1) * pageSize, limit: pageSize })
    
    try {
      const response = await apiService.get<UsersResponse>(url)
      console.log('✅ 用户API调用成功:', response)
      return response
    } catch (error) {
      console.error('❌ 用户API调用失败:', error)
      throw error
    }
  }

  async createUser(userData: CreateUserRequest): Promise<User> {
    return apiService.post<User>('/users', userData)
  }

  async updateUser(userId: number, userData: UpdateUserRequest): Promise<User> {
    return apiService.put<User>(`/users/${userId}`, userData)
  }

  async updateUserStatus(userId: number, status: string): Promise<{ message: string }> {
    return apiService.put<{ message: string }>(`/users/${userId}/status`, { status })
  }

  async deleteUser(userId: number): Promise<{ message: string }> {
    return apiService.delete<{ message: string }>(`/users/${userId}`)
  }

  async getUserStats(): Promise<{
    total: number
    active: number
    disabled: number
    suspended: number
  }> {
    return apiService.get('/users/stats')
  }
}

export const usersService = new UsersService()
