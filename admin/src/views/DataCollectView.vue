<template>
  <div class="datacollect-view">
    <!-- 当前任务状态 -->
    <div v-if="currentTask" class="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <div class="flex items-center">
        <el-icon class="text-yellow-600 mr-3"><Warning /></el-icon>
        <div>
          <h3 class="text-sm font-medium text-yellow-800">当前有任务正在运行</h3>
          <p class="text-sm text-yellow-700 mt-1">
            任务ID: {{ currentTask.task_id }} | 
            开始时间: {{ formatTime(currentTask.start_time) }}
          </p>
        </div>
      </div>
    </div>

    <!-- 数据采集功能 -->
    <el-card class="mb-8">
      <div class="text-center mb-8">
        <el-icon class="text-6xl text-gray-400 mb-4"><DataAnalysis /></el-icon>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">历史数据采集</h2>
        <p class="text-gray-600">使用akshare采集A股历史行情数据（单任务执行，防重复采集）</p>
      </div>

      <!-- 采集配置表单 -->
      <div class="max-w-2xl mx-auto">
        <el-form @submit.prevent="startCollection" :model="form" label-width="120px">
          <!-- 日期范围 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="开始日期" required>
                <el-date-picker
                  v-model="form.start_date"
                  type="date"
                  placeholder="选择开始日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="结束日期" required>
                <el-date-picker
                  v-model="form.end_date"
                  type="date"
                  placeholder="选择结束日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 股票选择 -->
          <el-form-item label="股票选择">
            <el-radio-group v-model="form.collection_type">
              <el-radio value="single">单个股票采集</el-radio>
              <el-radio value="multiple">多个股票采集</el-radio>
              <el-radio value="all">全量股票采集</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 单个股票代码输入 -->
          <el-form-item v-if="form.collection_type === 'single'" label="股票代码" required>
            <el-input
              v-model="form.single_stock_code"
              placeholder="请输入股票代码，例如：000001"
              clearable
            />
            <div class="text-sm text-gray-500 mt-1">支持输入单个股票代码进行采集</div>
          </el-form-item>

          <!-- 多个股票代码输入 -->
          <el-form-item v-if="form.collection_type === 'multiple'" label="股票代码" required>
            <el-input
              v-model="form.stock_codes_text"
              type="textarea"
              :rows="5"
              placeholder="请输入股票代码，每行一个，例如：&#10;000001&#10;000002&#10;000858"
            />
            <div class="text-sm text-gray-500 mt-1">支持输入多个股票代码，每行一个</div>
          </el-form-item>

          <!-- 全量采集说明 -->
          <el-alert
            v-if="form.collection_type === 'all'"
            title="全量采集说明"
            type="info"
            :closable="false"
            show-icon
          >
            <p>将采集数据库中所有股票的历史数据。由于akshare限流要求，系统采用单任务执行模式，
            已采集过的股票数据将被跳过，避免重复采集。</p>
          </el-alert>

          <!-- 测试模式 -->
          <el-form-item>
            <el-checkbox v-model="form.test_mode">测试模式（只采集前5只股票）</el-checkbox>
          </el-form-item>

          <!-- 操作按钮 -->
          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              :disabled="!!currentTask"
              @click="startCollection"
            >
              <el-icon v-if="loading" class="mr-2"><Loading /></el-icon>
              {{ loading ? '启动中...' : (currentTask ? '等待当前任务完成' : '开始采集') }}
            </el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <!-- 任务列表 -->
    <el-card>
      <template #header>
        <div class="flex justify-between items-center">
          <span>采集任务</span>
          <el-button type="text" @click="loadTasks" :icon="Refresh">
            刷新
          </el-button>
        </div>
      </template>

      <div v-if="tasks.length === 0" class="text-center text-gray-500 py-8">
        暂无采集任务
      </div>
      <div v-else class="space-y-4">
        <el-card
          v-for="task in tasks"
          :key="task.task_id"
          shadow="hover"
          class="mb-4"
        >
          <div class="flex justify-between items-start mb-3">
            <div>
              <h4 class="font-medium text-gray-900">任务 {{ task.task_id }}</h4>
              <p class="text-sm text-gray-500">
                {{ formatTime(task.start_time) }} - {{ task.end_time ? formatTime(task.end_time) : '进行中' }}
              </p>
            </div>
            <div class="flex items-center space-x-2">
              <el-tag
                :type="getStatusType(task.status)"
                size="small"
              >
                {{ getStatusText(task.status) }}
              </el-tag>
              <el-button
                v-if="task.status === 'running'"
                type="danger"
                size="small"
                @click="cancelTask(task.task_id)"
              >
                取消
              </el-button>
            </div>
          </div>
          
          <!-- 进度条 -->
          <div v-if="task.status === 'running'" class="mb-3">
            <div class="flex justify-between text-sm text-gray-600 mb-1">
              <span>进度</span>
              <span>{{ task.progress }}%</span>
            </div>
            <el-progress :percentage="task.progress" />
          </div>

          <!-- 统计信息 -->
          <el-row :gutter="20" class="text-sm">
            <el-col :span="6">
              <span class="text-gray-500">总股票数:</span>
              <span class="font-medium">{{ task.total_stocks }}</span>
            </el-col>
            <el-col :span="6">
              <span class="text-gray-500">成功:</span>
              <span class="font-medium text-green-600">{{ task.success_count }}</span>
            </el-col>
            <el-col :span="6">
              <span class="text-gray-500">失败:</span>
              <span class="font-medium text-red-600">{{ task.failed_count }}</span>
            </el-col>
            <el-col :span="6">
              <span class="text-gray-500">新增数据:</span>
              <span class="font-medium text-blue-600">{{ task.collected_count }}</span>
            </el-col>
          </el-row>

          <!-- 错误信息 -->
          <el-alert
            v-if="task.error_message"
            :title="task.error_message"
            type="error"
            :closable="false"
            show-icon
            class="mt-3"
          />
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataAnalysis, Warning, Loading, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'

// 表单数据
const form = ref({
  start_date: '',
  end_date: '',
  collection_type: 'single',
  single_stock_code: '',
  stock_codes_text: '',
  test_mode: false
})

// 状态数据
const tasks = ref([])
const currentTask = ref(null)
const loading = ref(false)
const pollingInterval = ref(null)

// API基础URL
const API_BASE = '/api'

// 方法
const startCollection = async () => {
  try {
    loading.value = true
    
    // 验证表单
    if (!form.value.start_date || !form.value.end_date) {
      ElMessage.error('请选择开始日期和结束日期')
      return
    }
    
    // 检查当前任务状态
    if (currentTask.value) {
      ElMessage.error('已有采集任务正在运行，请等待完成后再启动新任务')
      return
    }
    
    // 准备请求数据
    const requestData = {
      start_date: form.value.start_date,
      end_date: form.value.end_date,
      test_mode: form.value.test_mode
    }

    // 根据采集类型设置股票代码
    if (form.value.collection_type === 'single') {
      if (!form.value.single_stock_code.trim()) {
        ElMessage.error('请输入股票代码')
        return
      }
      requestData.stock_codes = [form.value.single_stock_code.trim()]
    } else if (form.value.collection_type === 'multiple') {
      const stockCodes = form.value.stock_codes_text
        .split('\n')
        .map(code => code.trim())
        .filter(code => code.length > 0)
      
      if (stockCodes.length === 0) {
        ElMessage.error('请输入至少一个股票代码')
        return
      }
      
      requestData.stock_codes = stockCodes
    }

    console.log('发送请求:', requestData)
    const response = await axios.post(`${API_BASE}/data-collection/historical`, requestData)
    
    if (response.data.status === 'started') {
      ElMessage.success('采集任务已启动')
      loadTasks()
      loadCurrentTask()
    }
    
  } catch (error) {
    console.error('启动采集任务失败:', error)
    let errorMsg = '启动采集任务失败'
    
    if (error.response) {
      // 服务器响应了错误状态码
      errorMsg = error.response.data?.detail || `服务器错误 (${error.response.status})`
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMsg = '无法连接到服务器，请检查网络连接'
    } else {
      // 其他错误
      errorMsg = error.message || '未知错误'
    }
    
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

const loadTasks = async () => {
  try {
    const response = await axios.get(`${API_BASE}/data-collection/tasks`)
    tasks.value = response.data
  } catch (error) {
    console.error('加载任务列表失败:', error)
  }
}

const loadCurrentTask = async () => {
  try {
    const response = await axios.get(`${API_BASE}/data-collection/current-task`)
    currentTask.value = response.data.current_task
  } catch (error) {
    console.error('加载当前任务信息失败:', error)
  }
}

const cancelTask = async (taskId: string) => {
  try {
    await ElMessageBox.confirm('确定要取消这个任务吗？', '确认取消', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`${API_BASE}/data-collection/tasks/${taskId}`)
    ElMessage.success('任务已取消')
    loadTasks()
    loadCurrentTask()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消任务失败:', error)
      ElMessage.error(error.response?.data?.detail || '取消任务失败')
    }
  }
}

const resetForm = () => {
  form.value = {
    start_date: '',
    end_date: '',
    collection_type: 'single',
    single_stock_code: '',
    stock_codes_text: '',
    test_mode: false
  }
}

const getStatusText = (status: string) => {
  const statusMap = {
    'running': '运行中',
    'completed': '已完成',
    'failed': '失败',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

const getStatusType = (status: string) => {
  const typeMap = {
    'running': 'primary',
    'completed': 'success',
    'failed': 'danger',
    'cancelled': 'warning'
  }
  return typeMap[status] || 'info'
}

const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

const startPolling = () => {
  pollingInterval.value = setInterval(() => {
    loadTasks()
    loadCurrentTask()
  }, 5000) // 每5秒刷新一次
}

const stopPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
  }
}

// 生命周期
onMounted(() => {
  loadTasks()
  loadCurrentTask()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.datacollect-view {
  padding: 20px;
}
</style> 