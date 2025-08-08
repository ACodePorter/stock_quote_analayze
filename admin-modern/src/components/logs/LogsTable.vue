<template>
  <div class="logs-table">
    <el-card>
      <el-table
        :data="logs"
        :loading="loading"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.timestamp) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="source" label="来源" width="150" />
        
        <el-table-column prop="message" label="消息" min-width="300">
          <template #default="{ row }">
            <div class="message-cell">
              <span class="message-text">{{ row.message }}</span>
              <el-button
                v-if="row.details"
                type="text"
                size="small"
                @click="showDetails(row)"
              >
                详情
              </el-button>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="user_id" label="用户ID" width="100" />
        
        <el-table-column prop="ip_address" label="IP地址" width="120" />
      </el-table>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailsVisible"
      title="日志详情"
      width="600px"
    >
      <div v-if="selectedLog" class="log-details">
        <div class="detail-item">
          <span class="detail-label">ID:</span>
          <span class="detail-value">{{ selectedLog.id }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">时间:</span>
          <span class="detail-value">{{ formatDateTime(selectedLog.timestamp) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">级别:</span>
          <span class="detail-value">
            <el-tag :type="getLevelType(selectedLog.level)" size="small">
              {{ selectedLog.level }}
            </el-tag>
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">来源:</span>
          <span class="detail-value">{{ selectedLog.source }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">消息:</span>
          <span class="detail-value">{{ selectedLog.message }}</span>
        </div>
        <div v-if="selectedLog.details" class="detail-item">
          <span class="detail-label">详情:</span>
          <div class="detail-value details-content">
            <pre>{{ selectedLog.details }}</pre>
          </div>
        </div>
        <div v-if="selectedLog.user_id" class="detail-item">
          <span class="detail-label">用户ID:</span>
          <span class="detail-value">{{ selectedLog.user_id }}</span>
        </div>
        <div v-if="selectedLog.ip_address" class="detail-item">
          <span class="detail-label">IP地址:</span>
          <span class="detail-value">{{ selectedLog.ip_address }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import dayjs from 'dayjs'
import type { LogEntry } from '@/types/logs.types'

interface Props {
  logs: LogEntry[]
  loading: boolean
}

defineProps<Props>()

// 详情对话框
const detailsVisible = ref(false)
const selectedLog = ref<LogEntry | null>(null)

// 格式化日期时间
const formatDateTime = (timestamp: string) => {
  return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss')
}

// 获取日志级别对应的标签类型（限定为 Element Plus 允许的取值）
const getLevelType = (level: string): 'primary' | 'success' | 'warning' | 'info' | 'danger' => {
  if (level === 'WARNING') return 'warning'
  if (level === 'ERROR') return 'danger'
  // INFO、DEBUG 或未知都使用 'info'
  return 'info'
}

// 显示详情
const showDetails = (log: LogEntry) => {
  selectedLog.value = log
  detailsVisible.value = true
}
</script>

<style scoped>
.logs-table {
  @apply mb-6;
}

.message-cell {
  @apply flex items-center justify-between;
}

.message-text {
  @apply flex-1 truncate;
}

.log-details {
  @apply space-y-4;
}

.detail-item {
  @apply flex items-start;
}

.detail-label {
  @apply w-20 text-sm font-medium text-gray-700 mr-4;
}

.detail-value {
  @apply flex-1 text-sm text-gray-900;
}

.details-content {
  @apply bg-gray-50 p-3 rounded border;
}

.details-content pre {
  @apply text-xs text-gray-700 whitespace-pre-wrap;
}
</style> 