<template>
  <div class="logs-view">
    <div class="logs-header">
      <h1 class="text-2xl font-bold text-gray-900">系统日志</h1>
      <div class="flex gap-2">
        <el-button @click="refreshLogs" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="exportLogs" type="primary">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 统计信息 -->
    <LogsStats :stats="stats" />

    <!-- 标签页 -->
    <el-tabs v-model="currentTab" @tab-change="handleTabChange">
      <el-tab-pane label="历史采集日志" name="historical_collect">
        <!-- 过滤器 -->
        <LogsFilter 
          :filters="filters"
          @update-filters="updateFilters"
        />

        <!-- 日志表格 -->
        <LogsTable 
          :logs="filteredLogs"
          :loading="loading"
          @refresh="loadLogs"
        />

        <!-- 分页 -->
        <LogsPagination 
          v-model:current="pagination.current"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          @change="handlePageChange"
        />
      </el-tab-pane>

      <el-tab-pane label="操作日志" name="operation">
        <!-- 过滤器 -->
        <LogsFilter 
          :filters="filters"
          @update-filters="updateFilters"
        />

        <!-- 日志表格 -->
        <LogsTable 
          :logs="filteredLogs"
          :loading="loading"
          @refresh="loadLogs"
        />

        <!-- 分页 -->
        <LogsPagination 
          v-model:current="pagination.current"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          @change="handlePageChange"
        />
      </el-tab-pane>
    </el-tabs>

    <!-- 错误提示 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      closable
      @close="clearError"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { Refresh, Download } from '@element-plus/icons-vue'
import { useLogsStore } from '@/stores/logs'
import LogsStats from '@/components/logs/LogsStats.vue'
import LogsFilter from '@/components/logs/LogsFilter.vue'
import LogsTable from '@/components/logs/LogsTable.vue'
import LogsPagination from '@/components/logs/LogsPagination.vue'

const logsStore = useLogsStore()

// 从store获取状态
const { 
  loading, 
  error, 
  filters, 
  pagination, 
  stats, 
  filteredLogs,
  currentTab 
} = storeToRefs(logsStore)

// 从store获取方法
const { 
  fetchStats, 
  updateFilters, 
  updatePagination, 
  switchTab, 
  loadLogs,
  refresh,
  exportLogs,
  clearError 
} = logsStore

// 方法
const refreshLogs = () => {
  refresh()
}

const handleTabChange = (tab: string) => {
  switchTab(tab as 'historical_collect' | 'operation')
}

const handlePageChange = (page: number, pageSize: number) => {
  updatePagination(page, pageSize)
}

// 生命周期
onMounted(() => {
  loadLogs()
  fetchStats()
})
</script>

<style scoped>
.logs-view {
  @apply space-y-6;
}

.logs-header {
  @apply flex justify-between items-center;
}
</style> 