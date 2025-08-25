import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LogsTable from './LogsTable.vue'
import type { AnyLogEntry, LogEntry, OperationLogEntry, HistoricalCollectLogEntry } from '@/types/logs.types'

describe('LogsTable', () => {
  const mockLogs: AnyLogEntry[] = [
    {
      id: 1,
      timestamp: '2024-01-01T10:00:00Z',
      level: 'INFO',
      message: 'Test log message',
      source: 'test-source',
      details: 'Test details',
      user_id: 123,
      ip_address: '192.168.1.1'
    } as LogEntry,
    {
      id: 2,
      operation_type: 'data_import',
      operation_desc: 'Import test data',
      affected_rows: 100,
      status: 'success',
      error_message: 'No errors',
      created_at: '2024-01-01T10:00:00Z'
    } as HistoricalCollectLogEntry,
    {
      id: 3,
      log_type: 'user_action',
      log_message: 'User performed action',
      affected_count: 1,
      log_status: 'completed',
      error_info: 'No errors',
      log_time: '2024-01-01T10:00:00Z'
    } as OperationLogEntry
  ]

  it('renders correctly with different log types', () => {
    const wrapper = mount(LogsTable, {
      props: {
        logs: mockLogs,
        loading: false,
        logType: 'historical_collect'
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.logs-table').exists()).toBe(true)
  })

  it('displays correct columns for historical_collect log type', () => {
    const wrapper = mount(LogsTable, {
      props: {
        logs: mockLogs,
        loading: false,
        logType: 'historical_collect'
      }
    })

    // 检查是否显示了正确的列
    expect(wrapper.text()).toContain('操作类型')
    expect(wrapper.text()).toContain('操作描述')
    expect(wrapper.text()).toContain('影响行数')
    expect(wrapper.text()).toContain('状态')
    expect(wrapper.text()).toContain('创建时间')
  })

  it('displays correct columns for operation log type', () => {
    const wrapper = mount(LogsTable, {
      props: {
        logs: mockLogs,
        loading: false,
        logType: 'operation'
      }
    })

    // 检查是否显示了正确的列
    expect(wrapper.text()).toContain('日志类型')
    expect(wrapper.text()).toContain('日志消息')
    expect(wrapper.text()).toContain('影响数量')
    expect(wrapper.text()).toContain('状态')
    expect(wrapper.text()).toContain('日志时间')
  })

  it('displays correct columns for default log type', () => {
    const wrapper = mount(LogsTable, {
      props: {
        logs: mockLogs,
        loading: false,
        logType: 'default'
      }
    })

    // 检查是否显示了正确的列
    expect(wrapper.text()).toContain('时间')
    expect(wrapper.text()).toContain('级别')
    expect(wrapper.text()).toContain('来源')
    expect(wrapper.text()).toContain('消息')
    expect(wrapper.text()).toContain('用户ID')
    expect(wrapper.text()).toContain('IP地址')
  })

  it('shows loading state correctly', () => {
    const wrapper = mount(LogsTable, {
      props: {
        logs: mockLogs,
        loading: true,
        logType: 'historical_collect'
      }
    })

    expect(wrapper.find('.el-table').attributes('loading')).toBe('true')
  })

  it('handles empty logs array', () => {
    const wrapper = mount(LogsTable, {
      props: {
        logs: [],
        loading: false,
        logType: 'historical_collect'
      }
    })

    expect(wrapper.exists()).toBe(true)
    // 表格应该存在但没有数据行
    expect(wrapper.find('.el-table').exists()).toBe(true)
  })
})
