export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'user' | 'guest'
  status: 'active' | 'inactive' | 'suspended'
  created_at: string
  updated_at: string
  last_login?: string
}

export interface CreateUserRequest {
  username: string
  email: string
  password: string
  role: 'admin' | 'user' | 'guest'
}

export interface UpdateUserRequest {
  email?: string
  role?: 'admin' | 'user' | 'guest'
  status?: 'active' | 'inactive' | 'suspended'
}

export interface UsersResponse {
  data: User[]
  total: number
  page: number
  pageSize: number
} 