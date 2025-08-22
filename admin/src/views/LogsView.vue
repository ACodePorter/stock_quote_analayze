<template>
  <div class="logs-view">
    <!-- 页面标题区域 - 已隐藏 -->
    <!-- <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; padding: 16px; background-color: #f8f9fa; border-radius: 8px;">
      <div style="flex: 1;">
        <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">管理后台 / 系统日志</div>
        <h1 style="font-size: 24px; font-weight: bold; color: #111827; margin: 0;">系统日志</h1>
      </div>
      <div style="display: flex; gap: 8px;">
        <el-button @click="refreshLogs" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="exportLogs" type="primary">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div> -->

    <!-- 统计信息 -->
    <LogsStats :stats="stats" />

    <!-- 标签页 -->
<el-tabs v-model="currentTab" @tab-change="onTabChange">
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
          :log-type="currentTab"
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

      <el-tab-pane label="实时行情采集日志" name="realtime_collect">
        <!-- 过滤器 -->
        <LogsFilter 
          :filters="filters"
          @update-filters="updateFilters"
        />

        <!-- 日志表格 -->
        <LogsTable 
          :logs="filteredLogs"
          :loading="loading"
          :log-type="currentTab"
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
          :log-type="currentTab"
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

type TabName = 'historical_collect' | 'realtime_collect' | 'operation'
const onTabChange = (name: string | number) => {
  switchTab(String(name) as TabName)
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
  margin-top: 24px;
}

/* 移除可能有问题的Tailwind样式 */
</style> 