import { apiService } from './api'
import type { LogsResponse, LogFilter, LogStats, LogTable } from '@/types/logs.types'

export class LogsService {
  async getLogs(params: LogFilter & { page: number; pageSize: number }): Promise<LogsResponse> {
    const queryParams = new URLSearchParams()
    
    if (params.type !== 'all') {
      queryParams.append('type', params.type)
    }
    if (params.level !== 'all') {
      queryParams.append('level', params.level)
    }
    if (params.startDate) {
      queryParams.append('start_date', params.startDate)
    }
    if (params.endDate) {
      queryParams.append('end_date', params.endDate)
    }
    if (params.keyword) {
      queryParams.append('keyword', params.keyword)
    }
    queryParams.append('page', params.page.toString())
    queryParams.append('page_size', params.pageSize.toString())
    
    return apiService.get<LogsResponse>(`/logs/query/historical_collect?${queryParams}`)
  }

  async getRealtimeLogs(params: LogFilter & { page: number; pageSize: number }): Promise<LogsResponse> {
    const queryParams = new URLSearchParams()
    
    if (params.level !== 'all') {
      queryParams.append('level', params.level)
    }
    if (params.startDate) {
      queryParams.append('start_date', params.startDate)
    }
    if (params.endDate) {
      queryParams.append('end_date', params.endDate)
    }
    if (params.keyword) {
      queryParams.append('keyword', params.keyword)
    }
    queryParams.append('page', params.page.toString())
    queryParams.append('page_size', params.pageSize.toString())
    
    return apiService.get<LogsResponse>(`/logs/query/realtime_collect?${queryParams}`)
  }

  async getOperationLogs(params: LogFilter & { page: number; pageSize: number }): Promise<LogsResponse> {
    const queryParams = new URLSearchParams()
    
    if (params.level !== 'all') {
      queryParams.append('level', params.level)
    }
    if (params.startDate) {
      queryParams.append('start_date', params.startDate)
    }
    if (params.endDate) {
      queryParams.append('end_date', params.endDate)
    }
    if (params.keyword) {
      queryParams.append('keyword', params.keyword)
    }
    queryParams.append('page', params.page.toString())
    queryParams.append('page_size', params.pageSize.toString())
    
    return apiService.get<LogsResponse>(`/operation-logs/query?${queryParams}`)
  }

  async getLogStats(): Promise<LogStats> {
    return apiService.get<LogStats>('/logs/stats')
  }

  async getLogTables(): Promise<LogTable[]> {
    return apiService.get<LogTable[]>('/logs/tables')
  }

  async exportLogs(params: LogFilter): Promise<Blob> {
    const queryParams = new URLSearchParams()
    
    if (params.type !== 'all') {
      queryParams.append('type', params.type)
    }
    if (params.level !== 'all') {
      queryParams.append('level', params.level)
    }
    if (params.startDate) {
      queryParams.append('start_date', params.startDate)
    }
    if (params.endDate) {
      queryParams.append('end_date', params.endDate)
    }
    if (params.keyword) {
      queryParams.append('keyword', params.keyword)
    }
    
    const response = await apiService.get(`/logs/export?${queryParams}`, {
      responseType: 'blob'
    })
    return response as Blob
  }
}

export const logsService = new LogsService() 