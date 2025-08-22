import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { logsService } from '@/services/logs.service'
import type { AnyLogEntry, LogFilter, LogStats, LogTable } from '@/types/logs.types'

export const useLogsStore = defineStore('logs', () => {
  // 状态 - 为每个标签页单独管理数据
  const historicalLogs = ref<AnyLogEntry[]>([])
  const realtimeLogs = ref<AnyLogEntry[]>([])
  const operationLogs = ref<AnyLogEntry[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const filters = ref<LogFilter>({
    type: 'all',
    level: 'all',
    startDate: null,
    endDate: null,
    keyword: ''
  })
  const pagination = ref({
    current: 1,
    pageSize: 20,
    total: 0
  })
  const stats = ref<LogStats | null>(null)
  const logTables = ref<LogTable[]>([])
  const currentTab = ref<'historical_collect' | 'realtime_collect' | 'operation'>('historical_collect')

  // 计算属性 - 根据当前标签页返回对应数据
  const filteredLogs = computed(() => {
    if (currentTab.value === 'historical_collect') {
      return historicalLogs.value
    } else if (currentTab.value === 'realtime_collect') {
      return realtimeLogs.value
    } else {
      return operationLogs.value
    }
  })

  // 动作
  const fetchLogs = async () => {
    loading.value = true
    error.value = null
    
    try {
      console.log('🔍 开始获取历史采集日志，分页参数:', {
        page: pagination.value.current,
        pageSize: pagination.value.pageSize
      })
      
      const response = await logsService.getLogs({
        ...filters.value,
        page: pagination.value.current,
        pageSize: pagination.value.pageSize
      })
      
      console.log('📊 历史采集日志API响应:', response)
      
      historicalLogs.value = response.data
      pagination.value.total = response.total
      
      console.log('✅ 历史采集日志获取成功:', {
        logsCount: historicalLogs.value.length,
        total: pagination.value.total,
        currentPage: pagination.value.current,
        pageSize: pagination.value.pageSize
      })
    } catch (err) {
      console.error('❌ 历史采集日志获取失败:', err)
      error.value = err instanceof Error ? err.message : '获取日志失败'
    } finally {
      loading.value = false
    }
  }

  const fetchRealtimeLogs = async () => {
    loading.value = true
    error.value = null
    
    try {
      console.log('🔍 开始获取实时行情采集日志，分页参数:', {
        page: pagination.value.current,
        pageSize: pagination.value.pageSize
      })
      
      const response = await logsService.getRealtimeLogs({
        ...filters.value,
        page: pagination.value.current,
        pageSize: pagination.value.pageSize
      })
      
      console.log('📊 实时行情采集日志API响应:', response)
      
      realtimeLogs.value = response.data
      pagination.value.total = response.total
      
      console.log('✅ 实时行情采集日志获取成功:', {
        logsCount: realtimeLogs.value.length,
        total: pagination.value.total,
        currentPage: pagination.value.current,
        pageSize: pagination.value.pageSize
      })
    } catch (err) {
      console.error('❌ 实时行情采集日志获取失败:', err)
      error.value = err instanceof Error ? err.message : '获取实时行情采集日志失败'
    } finally {
      loading.value = false
    }
  }

  const fetchOperationLogs = async () => {
    loading.value = true
    error.value = null
    
    try {
      console.log('🔍 开始获取操作日志，分页参数:', {
        page: pagination.value.current,
        pageSize: pagination.value.pageSize
      })
      
      const response = await logsService.getOperationLogs({
        ...filters.value,
        page: pagination.value.current,
        pageSize: pagination.value.pageSize
      })
      
      console.log('📊 操作日志API响应:', response)
      
      operationLogs.value = response.data
      pagination.value.total = response.total
      
      console.log('✅ 操作日志获取成功:', {
        logsCount: operationLogs.value.length,
        total: pagination.value.total,
        currentPage: pagination.value.current,
        pageSize: pagination.value.pageSize
      })
    } catch (err) {
      console.error('❌ 操作日志获取失败:', err)
      error.value = err instanceof Error ? err.message : '获取操作日志失败'
    } finally {
      loading.value = false
    }
  }

  const fetchStats = async () => {
    try {
      stats.value = await logsService.getLogStats()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取统计失败'
    }
  }

  const fetchLogTables = async () => {
    try {
      logTables.value = await logsService.getLogTables()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取日志表失败'
    }
  }

  const updateFilters = (newFilters: Partial<LogFilter>) => {
    filters.value = { ...filters.value, ...newFilters }
    pagination.value.current = 1 // 重置到第一页
    loadLogs()
  }

  const updatePagination = (page: number, pageSize: number) => {
    pagination.value.current = page
    pagination.value.pageSize = pageSize
    loadLogs()
  }

  const switchTab = (tab: 'historical_collect' | 'realtime_collect' | 'operation') => {
    currentTab.value = tab
    pagination.value.current = 1
    loadLogs()
  }

  const loadLogs = () => {
    if (currentTab.value === 'historical_collect') {
      fetchLogs()
    } else if (currentTab.value === 'realtime_collect') {
      fetchRealtimeLogs()
    } else {
      fetchOperationLogs()
    }
  }

  const refresh = () => {
    loadLogs()
    fetchStats()
  }

  const exportLogs = async () => {
    try {
      const blob = await logsService.exportLogs(filters.value)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `logs_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '导出失败'
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // 状态
    historicalLogs,
    realtimeLogs,
    operationLogs,
    loading,
    error,
    filters,
    pagination,
    stats,
    logTables,
    currentTab,
    // 计算属性
    filteredLogs,
    // 动作
    fetchLogs,
    fetchRealtimeLogs,
    fetchOperationLogs,
    fetchStats,
    fetchLogTables,
    updateFilters,
    updatePagination,
    switchTab,
    loadLogs,
    refresh,
    exportLogs,
    clearError
  }
}) 