export interface LogEntry {
  id: number
  timestamp: string
  level: 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG'
  message: string
  source: string
  details?: string
  user_id?: number
  ip_address?: string
}

export interface LogFilter {
  type: 'all' | 'historical_collect' | 'operation'
  level: 'all' | 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG'
  startDate: string | null
  endDate: string | null
  keyword: string
}

export interface LogStats {
  total: number
  success: number
  error: number
  successRate: number
  todayCount: number
  weekCount: number
}

export interface LogTable {
  id: string
  name: string
  description: string
  record_count: number
  last_updated: string
}

export interface LogsResponse {
  data: LogEntry[]
  total: number
  page: number
  pageSize: number
  stats: LogStats
} 