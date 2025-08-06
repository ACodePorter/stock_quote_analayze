import { apiService } from './api'
import type { LoginRequest, LoginResponse } from '@/types/auth.types'

export class AuthService {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    
    return apiService.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  }

  async logout(): Promise<void> {
    return apiService.post('/auth/logout')
  }

  async verifyToken(): Promise<{ valid: boolean }> {
    return apiService.get('/auth/verify')
  }
}

export const authService = new AuthService() 