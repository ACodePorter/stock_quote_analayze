<template>
  <div class="logs-stats">
    <el-row :gutter="16">
      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats?.total || 0 }}</div>
              <div class="stat-label">总日志数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon success">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats?.success || 0 }}</div>
              <div class="stat-label">成功日志</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon error">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats?.error || 0 }}</div>
              <div class="stat-label">错误日志</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon rate">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ formatSuccessRate(stats?.successRate) }}%</div>
              <div class="stat-label">成功率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { Document, CircleCheck, CircleClose, TrendCharts } from '@element-plus/icons-vue'
import type { LogStats } from '@/types/logs.types'

interface Props {
  stats: LogStats | null
}

defineProps<Props>()

// 格式化成功率
const formatSuccessRate = (rate: number | undefined) => {
  if (rate === undefined || rate === null) return 0
  return Math.round(rate * 100)
}
</script>

<style scoped>
.logs-stats {
  @apply mb-6;
}

.stat-card {
  @apply h-24;
}

.stat-content {
  @apply flex items-center h-full;
}

.stat-icon {
  @apply w-12 h-12 rounded-lg flex items-center justify-center mr-4;
}

.stat-icon.total {
  @apply bg-blue-100 text-blue-600;
}

.stat-icon.success {
  @apply bg-green-100 text-green-600;
}

.stat-icon.error {
  @apply bg-red-100 text-red-600;
}

.stat-icon.rate {
  @apply bg-purple-100 text-purple-600;
}

.stat-info {
  @apply flex-1;
}

.stat-value {
  @apply text-2xl font-bold text-gray-900;
}

.stat-label {
  @apply text-sm text-gray-500 mt-1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .logs-stats {
    @apply mb-4;
  }
  
  .stat-card {
    @apply h-20 mb-4;
  }
  
  .stat-icon {
    @apply w-10 h-10 mr-3;
  }
  
  .stat-value {
    @apply text-xl;
  }
  
  .stat-label {
    @apply text-xs;
  }
}

@media (max-width: 480px) {
  .stat-card {
    @apply h-16;
  }
  
  .stat-icon {
    @apply w-8 h-8 mr-2;
  }
  
  .stat-value {
    @apply text-lg;
  }
  
  .stat-label {
    @apply text-xs;
  }
}
</style> 