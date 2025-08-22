<template>
  <div class="quotes-view">
    <div class="page-header">
      <h1>行情数据</h1>
      <div class="header-actions">
        <el-button @click="refreshAllData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 标签页 -->
    <el-card class="tabs-section">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 股票实时行情 -->
        <el-tab-pane label="股票实时行情" name="stocks">
          <div class="tab-content">
            <el-table
              :data="stockData"
              :loading="stockLoading"
              stripe
              style="width: 100%"
            >
              <el-table-column prop="code" label="代码" width="80" />
              <el-table-column prop="name" label="名称" width="120" />
              <el-table-column prop="current_price" label="现价" width="80">
                <template #default="scope">
                  <span :class="getPriceClass(scope.row.current_price, scope.row.pre_close)">
                    {{ formatPrice(scope.row.current_price) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="change_percent" label="涨跌幅" width="80">
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.change_percent)">
                    {{ formatPercent(scope.row.change_percent) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="open" label="开盘" width="80">
                <template #default="scope">
                  {{ formatPrice(scope.row.open) }}
                </template>
              </el-table-column>
              <el-table-column prop="pre_close" label="昨收" width="80">
                <template #default="scope">
                  {{ formatPrice(scope.row.pre_close) }}
                </template>
              </el-table-column>
              <el-table-column prop="high" label="最高" width="80">
                <template #default="scope">
                  {{ formatPrice(scope.row.high) }}
                </template>
              </el-table-column>
              <el-table-column prop="low" label="最低" width="80">
                <template #default="scope">
                  {{ formatPrice(scope.row.low) }}
                </template>
              </el-table-column>
              <el-table-column prop="volume" label="成交量" width="100">
                <template #default="scope">
                  {{ formatVolume(scope.row.volume) }}
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="成交额" width="100">
                <template #default="scope">
                  {{ formatAmount(scope.row.amount) }}
                </template>
              </el-table-column>
              <el-table-column prop="turnover_rate" label="换手率" width="80">
                <template #default="scope">
                  {{ formatPercent(scope.row.turnover_rate) }}
                </template>
              </el-table-column>
              <el-table-column prop="pe_dynamic" label="PE" width="60">
                <template #default="scope">
                  {{ formatPE(scope.row.pe_dynamic) }}
                </template>
              </el-table-column>
              <el-table-column prop="pb_ratio" label="PB" width="60">
                <template #default="scope">
                  {{ formatPB(scope.row.pb_ratio) }}
                </template>
              </el-table-column>
              <el-table-column prop="update_time" label="更新时间" width="140" />
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 指数实时行情 -->
        <el-tab-pane label="指数实时行情" name="indices">
          <div class="tab-content">
            <el-table
              :data="indexData"
              :loading="indexLoading"
              stripe
              style="width: 100%"
            >
              <el-table-column prop="code" label="代码" width="80" />
              <el-table-column prop="name" label="名称" width="120" />
              <el-table-column prop="price" label="点位" width="100">
                <template #default="scope">
                  <span :class="getPriceClass(scope.row.price, scope.row.pre_close)">
                    {{ formatPrice(scope.row.price) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="change" label="涨跌" width="80">
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.change)">
                    {{ formatPrice(scope.row.change) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="pct_chg" label="涨跌幅" width="80">
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.pct_chg)">
                    {{ formatPercent(scope.row.pct_chg) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="open" label="开盘" width="80">
                <template #default="scope">
                  {{ formatPrice(scope.row.open) }}
                </template>
              </el-table-column>
              <el-table-column prop="pre_close" label="昨收" width="80">
                <template #default="scope">
                  {{ formatPrice(scope.row.pre_close) }}
                </template>
              </el-table-column>
              <el-table-column prop="high" label="最高" width="80">
                <template #default="scope">
                  {{ formatPrice(scope.row.high) }}
                </template>
              </el-table-column>
              <el-table-column prop="low" label="最低" width="80">
                <template #default="scope">
                  {{ formatPrice(scope.row.low) }}
                </template>
              </el-table-column>
              <el-table-column prop="volume" label="成交量" width="100">
                <template #default="scope">
                  {{ formatVolume(scope.row.volume) }}
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="成交额" width="100">
                <template #default="scope">
                  {{ formatAmount(scope.row.amount) }}
                </template>
              </el-table-column>
              <el-table-column prop="amplitude" label="振幅" width="80">
                <template #default="scope">
                  {{ formatPercent(scope.row.amplitude) }}
                </template>
              </el-table-column>
              <el-table-column prop="turnover" label="换手率" width="80">
                <template #default="scope">
                  {{ formatPercent(scope.row.turnover) }}
                </template>
              </el-table-column>
              <el-table-column prop="pe" label="PE" width="60">
                <template #default="scope">
                  {{ formatPE(scope.row.pe) }}
                </template>
              </el-table-column>
              <el-table-column prop="volume_ratio" label="量比" width="80">
                <template #default="scope">
                  {{ formatVolume(scope.row.volume_ratio) }}
                </template>
              </el-table-column>
              <el-table-column prop="update_time" label="更新时间" width="140" />
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 行业板块实时行情 -->
        <el-tab-pane label="行业板块实时行情" name="industries">
          <div class="tab-content">
            <el-table
              :data="industryData"
              :loading="industryLoading"
              stripe
              style="width: 100%"
            >
              <el-table-column prop="name" label="行业名称" width="150" />
              <el-table-column prop="price" label="点位" width="80">
                <template #default="scope">
                  {{ formatPrice(scope.row.price) }}
                </template>
              </el-table-column>
              <el-table-column prop="change_percent" label="涨跌幅" width="80">
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.change_percent)">
                    {{ formatPercent(scope.row.change_percent) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="change_amount" label="涨跌额" width="80">
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.change_amount)">
                    {{ formatPrice(scope.row.change_amount) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="total_market_value" label="总市值" width="100">
                <template #default="scope">
                  {{ formatAmount(scope.row.total_market_value) }}
                </template>
              </el-table-column>
              <el-table-column prop="volume" label="成交量" width="100">
                <template #default="scope">
                  {{ formatVolume(scope.row.volume) }}
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="成交额" width="100">
                <template #default="scope">
                  {{ formatAmount(scope.row.amount) }}
                </template>
              </el-table-column>
              <el-table-column prop="turnover_rate" label="换手率" width="80">
                <template #default="scope">
                  {{ formatPercent(scope.row.turnover_rate) }}
                </template>
              </el-table-column>
              <el-table-column prop="leading_stock" label="领涨股" width="100" />
              <el-table-column prop="leading_stock_change" label="领涨股涨幅" width="100">
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.leading_stock_change)">
                    {{ formatPercent(scope.row.leading_stock_change) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="update_time" label="更新时间" width="140" />
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { quotesService } from '@/services/quotes.service'

// 响应式数据
const activeTab = ref('stocks')
const loading = ref(false)
const stockData = ref<any[]>([])
const stockLoading = ref(false)
const indexData = ref<any[]>([])
const indexLoading = ref(false)
const industryData = ref<any[]>([])
const industryLoading = ref(false)

// 方法
const refreshAllData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchStockData(),
      fetchIndexData(),
      fetchIndustryData(),
      fetchStats()
    ])
    ElMessage.success('数据刷新成功')
  } catch (error) {
    console.error('刷新数据失败:', error)
    ElMessage.error('数据刷新失败')
  } finally {
    loading.value = false
  }
}

const fetchStockData = async () => {
  stockLoading.value = true
  try {
    const response = await quotesService.getStockQuotes({
      page: 1,
      pageSize: 20
    })
    
    if (response.success) {
      stockData.value = response.data
    }
  } catch (error) {
    console.error('获取股票数据失败:', error)
    ElMessage.error('获取股票数据失败')
  } finally {
    stockLoading.value = false
  }
}

const fetchIndexData = async () => {
  indexLoading.value = true
  try {
    const response = await quotesService.getIndexQuotes({
      page: 1,
      pageSize: 20
    })
    
    if (response.success) {
      indexData.value = response.data
    }
  } catch (error) {
    console.error('获取指数数据失败:', error)
    ElMessage.error('获取指数数据失败')
  } finally {
    indexLoading.value = false
  }
}

const fetchIndustryData = async () => {
  industryLoading.value = true
  try {
    const response = await quotesService.getIndustryQuotes({
      page: 1,
      pageSize: 20
    })
    
    if (response.success) {
      industryData.value = response.data
    }
  } catch (error) {
    console.error('获取行业板块数据失败:', error)
    ElMessage.error('获取行业板块数据失败')
  } finally {
    industryLoading.value = false
  }
}

const fetchStats = async () => {
  try {
    const response = await quotesService.getQuotesStats()
    if (response.success) {
      // TODO: 更新统计数据
      console.log('统计数据:', response.data)
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const handleTabChange = (tab: string | number) => {
  console.log('切换到标签页:', tab)
}

// 数据格式化函数
const formatPrice = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '-'
  return value.toFixed(2)
}

const formatPercent = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '-'
  return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
}

const formatVolume = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '-'
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`
  } else if (value >= 10000) {
    return `${(value / 10000).toFixed(2)}万`
  }
  return value.toLocaleString()
}

const formatAmount = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '-'
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`
  } else if (value >= 10000) {
    return `${(value / 10000).toFixed(2)}万`
  }
  return value.toLocaleString()
}

const formatPE = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '-'
  return value.toFixed(2)
}

const formatPB = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '-'
  return value.toFixed(2)
}

const getPriceClass = (current: number | null | undefined, preClose: number | null | undefined): string => {
  if (current === null || current === undefined || preClose === null || preClose === undefined) return ''
  if (current > preClose) return 'text-red-500 font-medium'
  if (current < preClose) return 'text-green-500 font-medium'
  return ''
}

const getChangeClass = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return ''
  if (value > 0) return 'text-red-500 font-medium'
  if (value < 0) return 'text-green-500 font-medium'
  return ''
}

// 生命周期
onMounted(async () => {
  console.log('行情数据页面已加载')
  await fetchStockData()
})
</script>

<style scoped>
.quotes-view {
  padding: 24px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.tabs-section {
  margin-bottom: 24px;
}

.tab-content {
  padding: 20px 0;
}

/* 数据格式化样式 */
.text-red-500 {
  color: #ef4444;
}

.text-green-500 {
  color: #10b981;
}

.font-medium {
  font-weight: 500;
}

/* 表格样式优化 */
.el-table {
  font-size: 14px;
}

.el-table th {
  background-color: #f8fafc;
  color: #374151;
  font-weight: 600;
}

.el-table td {
  padding: 8px 0;
}

/* 数字列右对齐 */
.el-table .cell {
  text-align: right;
}

.el-table .cell:first-child {
  text-align: left;
}

/* 涨跌颜色 */
.positive-change {
  color: #ef4444;
}

.negative-change {
  color: #10b981;
}

.neutral-change {
  color: #6b7280;
}
</style> 