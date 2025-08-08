import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth'

class ApiService {
  private api: AxiosInstance
  private isLoggingOut = false

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/admin',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 请求拦截器
    this.api.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore()
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // 响应拦截器
    this.api.interceptors.response.use(
      (response) => response.data,
      (error) => {
        // 避免在登出请求时触发无限循环
        if (error.response?.status === 401 && !this.isLoggingOut) {
          const authStore = useAuthStore()
          authStore.logout()
        }
        return Promise.reject(error)
      }
    )
  }

  get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.api.get(url, config)
  }

  post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.api.post(url, data, config)
  }

  put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.api.put(url, data, config)
  }

  delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.api.delete(url, config)
  }
}

export const apiService = new ApiService() 