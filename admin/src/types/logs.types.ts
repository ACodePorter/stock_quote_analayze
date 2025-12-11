export interface LogEntry {
  id: number
  timestamp: string
  level: 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG'
  message: string
  source: string
  collect_source: string
  details?: string
  user_id?: number
  ip_address?: string
}

// 历史采集日志条目
export interface HistoricalCollectLogEntry {
  id: number
  operation_type: string
  collect_source: string
  operation_desc: string
  affected_rows: number
  status: string
  error_message?: string
  created_at: string
}

// 实时行情采集日志条目
export interface RealtimeCollectLogEntry {
  id: number
  operation_type: string
  collect_source: string
  operation_desc: string
  affected_rows: number
  status: string
  error_message?: string
  created_at: string
}

// 操作日志条目
export interface OperationLogEntry {
  id: number
  log_type: string
  log_message: string
  affected_count: number
  log_status: string
  error_info?: string
  log_time: string
}

// 通用日志条目类型
export type AnyLogEntry = LogEntry | HistoricalCollectLogEntry | RealtimeCollectLogEntry | OperationLogEntry

export interface LogFilter {
  type: 'all' | 'historical_collect' | 'realtime_collect' | 'operation' | 'collect_source'
  level: 'all' | 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG'
  startDate: string | null
  endDate: string | null
  collect_source: string | null
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
  data: AnyLogEntry[]
  total: number
  page: number
  pageSize: number
} 