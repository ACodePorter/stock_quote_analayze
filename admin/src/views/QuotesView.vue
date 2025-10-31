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
            <!-- 搜索和筛选 -->
            <div class="search-section">
              <el-row :gutter="16" align="middle">
                <el-col :xs="24" :sm="24" :md="6" :lg="6" :xl="6">
                  <el-input
                    v-model="stockSearchKeyword"
                    placeholder="搜索股票代码或名称"
                    clearable
                    @input="handleStockSearch"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                </el-col>
                <el-col :xs="12" :sm="12" :md="4" :lg="4" :xl="4">
                  <el-select
                    v-model="stockMarketFilter"
                    placeholder="市场类型"
                    clearable
                    @change="handleStockMarketFilter"
                    style="width: 100%"
                  >
                    <el-option label="全部" value="" />
                    <el-option label="上海" value="sh" />
                    <el-option label="深圳" value="sz" />
                    <el-option label="创业板" value="cy" />
                    <el-option label="北交所" value="bj" />
                  </el-select>
                </el-col>
                <el-col :xs="12" :sm="12" :md="4" :lg="4" :xl="4">
                  <el-select
                    v-model="stockSortBy"
                    placeholder="排序方式"
                    @change="handleStockSortChange"
                    style="width: 100%"
                  >
                    <el-option label="涨跌幅（高到低）" value="change_percent" />
                    <el-option label="现价（高到低）" value="current_price" />
                    <el-option label="最高价（高到低）" value="high" />
                    <el-option label="最低价（高到低）" value="low" />
                    <el-option label="开盘价（高到低）" value="open" />
                    <el-option label="昨收价（高到低）" value="pre_close" />
                    <el-option label="成交量（高到低）" value="volume" />
                    <el-option label="成交额（高到低）" value="amount" />
                    <el-option label="换手率（高到低）" value="turnover_rate" />
                    <el-option label="市盈率（高到低）" value="pe_dynamic" />
                    <el-option label="总市值（高到低）" value="total_market_value" />
                    <el-option label="市净率（高到低）" value="pb_ratio" />
                    <el-option label="流通市值（高到低）" value="circulating_market_value" />
                    <el-option label="更新时间（新到旧）" value="update_time" />
                  </el-select>
                </el-col>
                <el-col :xs="24" :sm="24" :md="4" :lg="4" :xl="4">
                  <el-button @click="refreshStockData" :loading="stockLoading" style="width: 100%">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </el-col>
              </el-row>
            </div>

            <el-table
              :data="stockData"
              :loading="stockLoading"
              stripe
              style="width: 100%"
              class="responsive-table"
            >
              <el-table-column prop="code" label="代码" width="80" min-width="60" show-overflow-tooltip />
              <el-table-column prop="name" label="名称" min-width="100" show-overflow-tooltip />
              <el-table-column prop="current_price" label="现价" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span :class="getPriceClass(scope.row.current_price, scope.row.pre_close)">
                    {{ formatPrice(scope.row.current_price) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="change_percent" label="涨跌幅" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.change_percent)">
                    {{ formatPercent(scope.row.change_percent) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="open" label="开盘" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatPrice(scope.row.open) }}
                </template>
              </el-table-column>
              <el-table-column prop="pre_close" label="昨收" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatPrice(scope.row.pre_close) }}
                </template>
              </el-table-column>
              <el-table-column prop="high" label="最高" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatPrice(scope.row.high) }}
                </template>
              </el-table-column>
              <el-table-column prop="low" label="最低" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatPrice(scope.row.low) }}
                </template>
              </el-table-column>
              <el-table-column prop="volume" label="成交量" min-width="90" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatVolume(scope.row.volume) }}
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="成交额" min-width="90" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatAmount(scope.row.amount) }}
                </template>
              </el-table-column>
              <el-table-column prop="turnover_rate" label="换手率" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatPercent(scope.row.turnover_rate) }}
                </template>
              </el-table-column>
              <el-table-column prop="pe_dynamic" label="PE" min-width="60" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatPE(scope.row.pe_dynamic) }}
                </template>
              </el-table-column>
              <el-table-column prop="pb_ratio" label="PB" min-width="60" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatPB(scope.row.pb_ratio) }}
                </template>
              </el-table-column>
              <el-table-column prop="update_time" label="更新时间" min-width="120" show-overflow-tooltip />
            </el-table>

            <!-- 分页组件 -->
            <div class="pagination-section">
              <el-pagination
                v-model:current-page="stockCurrentPage"
                v-model:page-size="stockPageSize"
                :total="stockTotal"
                :page-sizes="[20, 50, 100, 200]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleStockPageSizeChange"
                @current-change="handleStockPageChange"
              />
            </div>
          </div>
        </el-tab-pane>

        <!-- 指数实时行情 -->
        <el-tab-pane label="指数实时行情" name="indices">
          <div class="tab-content">
            <!-- 搜索和筛选 -->
            <div class="search-section">
              <el-row :gutter="16" align="middle">
                <el-col :xs="24" :sm="24" :md="6" :lg="6" :xl="6">
                  <el-input
                    v-model="indexSearchKeyword"
                    placeholder="搜索指数代码或名称"
                    clearable
                    @input="handleIndexSearch"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                </el-col>
                <el-col :xs="24" :sm="24" :md="4" :lg="4" :xl="4">
                  <el-select
                    v-model="indexSortBy"
                    placeholder="排序方式"
                    @change="handleIndexSortChange"
                    style="width: 100%"
                  >
                    <el-option label="涨跌幅（高到低）" value="pct_chg" />
                    <el-option label="点位（高到低）" value="price" />
                    <el-option label="涨跌（高到低）" value="change" />
                    <el-option label="最高价（高到低）" value="high" />
                    <el-option label="最低价（高到低）" value="low" />
                    <el-option label="开盘价（高到低）" value="open" />
                    <el-option label="昨收价（高到低）" value="pre_close" />
                    <el-option label="成交量（高到低）" value="volume" />
                    <el-option label="成交额（高到低）" value="amount" />
                    <el-option label="振幅（高到低）" value="amplitude" />
                    <el-option label="换手率（高到低）" value="turnover" />
                    <el-option label="市盈率（高到低）" value="pe" />
                    <el-option label="量比（高到低）" value="volume_ratio" />
                    <el-option label="更新时间（新到旧）" value="update_time" />
                  </el-select>
                </el-col>
                <el-col :xs="24" :sm="24" :md="4" :lg="4" :xl="4">
                  <el-button @click="refreshIndexData" :loading="indexLoading" style="width: 100%">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </el-col>
              </el-row>
            </div>

            <el-table
              :data="indexData"
              :loading="indexLoading"
              stripe
              style="width: 100%"
              class="responsive-table"
            >
              <el-table-column prop="code" label="代码" width="80" min-width="60" show-overflow-tooltip />
              <el-table-column prop="name" label="名称" min-width="100" show-overflow-tooltip />
              <el-table-column prop="price" label="点位" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span :class="getPriceClass(scope.row.price, scope.row.pre_close)">
                    {{ formatPrice(scope.row.price) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="change" label="涨跌" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.change)">
                    {{ formatPrice(scope.row.change) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="pct_chg" label="涨跌幅" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.pct_chg)">
                    {{ formatPercent(scope.row.pct_chg) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="open" label="开盘" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatPrice(scope.row.open) }}
                </template>
              </el-table-column>
              <el-table-column prop="pre_close" label="昨收" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatPrice(scope.row.pre_close) }}
                </template>
              </el-table-column>
              <el-table-column prop="high" label="最高" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatPrice(scope.row.high) }}
                </template>
              </el-table-column>
              <el-table-column prop="low" label="最低" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatPrice(scope.row.low) }}
                </template>
              </el-table-column>
              <el-table-column prop="volume" label="成交量" min-width="90" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatVolume(scope.row.volume) }}
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="成交额" width="100">
                <template #default="scope">
                  {{ formatAmount(scope.row.amount) }}
                </template>
              </el-table-column>
              <el-table-column prop="update_time" label="更新时间" width="140" />
            </el-table>

            <!-- 分页组件 -->
            <div class="pagination-section">
              <el-pagination
                v-model:current-page="indexCurrentPage"
                v-model:page-size="indexPageSize"
                :total="indexTotal"
                :page-sizes="[20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleIndexPageSizeChange"
                @current-change="handleIndexPageChange"
              />
            </div>
          </div>
        </el-tab-pane>

        <!-- 历史行情数据 -->
        <el-tab-pane label="历史行情数据" name="historical">
          <div class="tab-content">
            <!-- 搜索和筛选 -->
            <div class="search-section">
              <el-row :gutter="16" align="middle">
                <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
                  <el-select
                    v-model="historicalStockCode"
                    placeholder="选择股票"
                    filterable
                    clearable
                    @change="handleHistoricalStockChange"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="stock in stockList"
                      :key="stock.code"
                      :label="`${stock.code} - ${stock.name}`"
                      :value="stock.code"
                    />
                  </el-select>
                </el-col>
                <el-col :xs="12" :sm="6" :md="4" :lg="4" :xl="4">
                  <el-date-picker
                    v-model="historicalStartDate"
                    type="date"
                    placeholder="开始日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    @change="handleHistoricalDateChange"
                    style="width: 100%"
                  />
                </el-col>
                <el-col :xs="12" :sm="6" :md="4" :lg="4" :xl="4">
                  <el-date-picker
                    v-model="historicalEndDate"
                    type="date"
                    placeholder="结束日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    @change="handleHistoricalDateChange"
                    style="width: 100%"
                  />
                </el-col>
                <el-col :xs="24" :sm="12" :md="4" :lg="4" :xl="4">
                  <el-checkbox
                    v-model="historicalIncludeNotes"
                    @change="handleHistoricalIncludeNotesChange"
                  >
                    包含交易备注
                  </el-checkbox>
                </el-col>
                <el-col :xs="24" :sm="12" :md="4" :lg="4" :xl="4">
                  <el-button @click="refreshHistoricalData" :loading="historicalLoading" style="width: 100%">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </el-col>
              </el-row>
            </div>

            <el-table
              :data="historicalData"
              :loading="historicalLoading"
              stripe
              style="width: 100%"
              class="responsive-table"
            >
              <el-table-column prop="code" label="代码" width="80" show-overflow-tooltip fixed="left" />
              <el-table-column prop="name" label="名称" width="100" show-overflow-tooltip fixed="left" />
              <el-table-column prop="date" label="日期" width="100" show-overflow-tooltip />
              <el-table-column prop="open" label="开盘" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span v-if="scope.row.editing">
                    <el-input
                      v-model="scope.row.editData.open"
                      size="small"
                      type="number"
                      step="0.01"
                      @blur="validateEditData(scope.row)"
                    />
                  </span>
                  <span v-else>
                    {{ formatPrice(scope.row.open) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="close" label="收盘" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span v-if="scope.row.editing">
                    <el-input
                      v-model="scope.row.editData.close"
                      size="small"
                      type="number"
                      step="0.01"
                      @blur="validateEditData(scope.row)"
                    />
                  </span>
                  <span v-else>
                    {{ formatPrice(scope.row.close) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="high" label="最高" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span v-if="scope.row.editing">
                    <el-input
                      v-model="scope.row.editData.high"
                      size="small"
                      type="number"
                      step="0.01"
                      @blur="validateEditData(scope.row)"
                    />
                  </span>
                  <span v-else>
                    {{ formatPrice(scope.row.high) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="low" label="最低" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span v-if="scope.row.editing">
                    <el-input
                      v-model="scope.row.editData.low"
                      size="small"
                      type="number"
                      step="0.01"
                      @blur="validateEditData(scope.row)"
                    />
                  </span>
                  <span v-else>
                    {{ formatPrice(scope.row.low) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="volume" label="成交量" min-width="90" show-overflow-tooltip>
                <template #default="scope">
                  <span v-if="scope.row.editing">
                    <el-input
                      v-model="scope.row.editData.volume"
                      size="small"
                      type="number"
                      @blur="validateEditData(scope.row)"
                    />
                  </span>
                  <span v-else>
                    {{ formatVolume(scope.row.volume) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="成交额" min-width="90" show-overflow-tooltip>
                <template #default="scope">
                  <span v-if="scope.row.editing">
                    <el-input
                      v-model="scope.row.editData.amount"
                      size="small"
                      type="number"
                      step="0.01"
                      @blur="validateEditData(scope.row)"
                    />
                  </span>
                  <span v-else>
                    {{ formatAmount(scope.row.amount) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="change_percent" label="涨跌幅" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.change_percent)">
                    {{ formatPercent(scope.row.change_percent) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="change" label="涨跌额" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.change)">
                    {{ formatPrice(scope.row.change) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="turnover_rate" label="换手率" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span v-if="scope.row.editing">
                    <el-input
                      v-model="scope.row.editData.turnover_rate"
                      size="small"
                      type="number"
                      step="0.01"
                      @blur="validateEditData(scope.row)"
                    />
                  </span>
                  <span v-else>
                    {{ formatPercent(scope.row.turnover_rate) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="remarks" label="备注" min-width="120" show-overflow-tooltip>
                <template #default="scope">
                  <span v-if="scope.row.editing">
                    <el-input
                      v-model="scope.row.editData.remarks"
                      size="small"
                      type="textarea"
                      :rows="2"
                    />
                  </span>
                  <span v-else>
                    {{ scope.row.remarks || '-' }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="scope">
                  <div v-if="scope.row.editing">
                    <el-button
                      type="primary"
                      size="small"
                      @click="saveHistoricalEdit(scope.row)"
                      :loading="scope.row.saving"
                    >
                      保存
                    </el-button>
                    <el-button
                      size="small"
                      @click="cancelHistoricalEdit(scope.row)"
                    >
                      取消
                    </el-button>
                  </div>
                  <div v-else>
                    <el-button
                      type="primary"
                      size="small"
                      @click="startHistoricalEdit(scope.row)"
                    >
                      编辑
                    </el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页组件 -->
            <div class="pagination-section">
              <el-pagination
                v-model:current-page="historicalCurrentPage"
                v-model:page-size="historicalPageSize"
                :total="historicalTotal"
                :page-sizes="[20, 50, 100, 200]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleHistoricalPageSizeChange"
                @current-change="handleHistoricalPageChange"
              />
            </div>
          </div>
        </el-tab-pane>

        <!-- 行业板块实时行情 -->
        <el-tab-pane label="行业板块实时行情" name="industries">
          <div class="tab-content">
            <!-- 搜索和筛选 -->
            <div class="search-section">
              <el-row :gutter="16" align="middle">
                <el-col :xs="24" :sm="24" :md="6" :lg="6" :xl="6">
                  <el-input
                    v-model="industrySearchKeyword"
                    placeholder="搜索行业名称"
                    clearable
                    @input="handleIndustrySearch"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                </el-col>
                <el-col :xs="24" :sm="24" :md="4" :lg="4" :xl="4">
                  <el-select
                    v-model="industrySortBy"
                    placeholder="排序方式"
                    @change="handleIndustrySortChange"
                    style="width: 100%"
                  >
                    <el-option label="涨跌幅（高到低）" value="change_percent" />
                    <el-option label="成交量（高到低）" value="volume" />
                    <el-option label="成交额（高到低）" value="amount" />
                    <el-option label="更新时间（新到旧）" value="update_time" />
                  </el-select>
                </el-col>
                <el-col :xs="24" :sm="24" :md="4" :lg="4" :xl="4">
                  <el-button @click="refreshIndustryData" :loading="industryLoading" style="width: 100%">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </el-col>
              </el-row>
            </div>

            <el-table
              :data="industryData"
              :loading="industryLoading"
              stripe
              style="width: 100%"
              class="responsive-table"
            >
              <el-table-column prop="name" label="行业名称" min-width="120" show-overflow-tooltip />
              <el-table-column prop="price" label="点位" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatPrice(scope.row.price) }}
                </template>
              </el-table-column>
              <el-table-column prop="change_percent" label="涨跌幅" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.change_percent)">
                    {{ formatPercent(scope.row.change_percent) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="change_amount" label="涨跌额" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.change_amount)">
                    {{ formatPrice(scope.row.change_amount) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="total_market_value" label="总市值" min-width="90" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatAmount(scope.row.total_market_value) }}
                </template>
              </el-table-column>
              <el-table-column prop="volume" label="成交量" min-width="90" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatVolume(scope.row.volume) }}
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="成交额" min-width="90" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatAmount(scope.row.amount) }}
                </template>
              </el-table-column>
              <el-table-column prop="turnover_rate" label="换手率" min-width="80" show-overflow-tooltip>
                <template #default="scope">
                  {{ formatPercent(scope.row.turnover_rate) }}
                </template>
              </el-table-column>
              <el-table-column prop="leading_stock" label="领涨股" min-width="90" show-overflow-tooltip />
              <el-table-column prop="leading_stock_change" label="领涨股涨幅" min-width="90" show-overflow-tooltip>
                <template #default="scope">
                  <span :class="getChangeClass(scope.row.leading_stock_change)">
                    {{ formatPercent(scope.row.leading_stock_change) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="update_time" label="更新时间" min-width="120" show-overflow-tooltip />
            </el-table>

            <!-- 分页组件 -->
            <div class="pagination-section">
              <el-pagination
                v-model:current-page="industryCurrentPage"
                v-model:page-size="industryPageSize"
                :total="industryTotal"
                :page-sizes="[20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleIndustryPageSizeChange"
                @current-change="handleIndustryPageChange"
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import { quotesService } from '@/services/quotes.service'

// 响应式数据
const activeTab = ref('stocks')
const loading = ref(false)

// 股票数据相关
const stockData = ref<any[]>([])
const stockLoading = ref(false)
const stockCurrentPage = ref(1)
const stockPageSize = ref(20)
const stockTotal = ref(0)
const stockSearchKeyword = ref('')
const stockMarketFilter = ref('')
const stockSortBy = ref('change_percent')

// 指数数据相关
const indexData = ref<any[]>([])
const indexLoading = ref(false)
const indexCurrentPage = ref(1)
const indexPageSize = ref(20)
const indexTotal = ref(0)
const indexSearchKeyword = ref('')
const indexSortBy = ref('pct_chg')

// 历史行情数据相关
const historicalData = ref<any[]>([])
const historicalLoading = ref(false)
const historicalCurrentPage = ref(1)
const historicalPageSize = ref(20)
const historicalTotal = ref(0)
const historicalStockCode = ref('')
const historicalStartDate = ref('')
const historicalEndDate = ref('')
const historicalIncludeNotes = ref(true)
const stockList = ref<any[]>([])

// 行业板块数据相关
const industryData = ref<any[]>([])
const industryLoading = ref(false)
const industryCurrentPage = ref(1)
const industryPageSize = ref(20)
const industryTotal = ref(0)
const industrySearchKeyword = ref('')
const industrySortBy = ref('change_percent')

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
      page: stockCurrentPage.value,
      pageSize: stockPageSize.value,
      keyword: stockSearchKeyword.value,
      market: stockMarketFilter.value,
      sortBy: stockSortBy.value
    })
    
    if (response.success) {
      stockData.value = response.data
      stockTotal.value = response.total
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
      page: indexCurrentPage.value,
      pageSize: indexPageSize.value,
      keyword: indexSearchKeyword.value,
      sortBy: indexSortBy.value
    })
    
    if (response.success) {
      indexData.value = response.data
      indexTotal.value = response.total
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
      page: industryCurrentPage.value,
      pageSize: industryPageSize.value,
      keyword: industrySearchKeyword.value,
      sortBy: industrySortBy.value
    })
    
    if (response.success) {
      industryData.value = response.data
      industryTotal.value = response.total
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
      console.log('统计数据:', response.data)
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// const fetchStockList = async () => {
//   try {
//     const response = await quotesService.getStockList()
//     if (response.success) {
//       stockList.value = response.data
//     }
//   } catch (error) {
//     console.error('获取股票列表失败:', error)
//     ElMessage.error('获取股票列表失败')
//   }
// }

const fetchHistoricalData = async () => {
  historicalLoading.value = true
  try {
    const response = await quotesService.getHistoricalQuotes({
      code: historicalStockCode.value || '',  // 允许为空
      page: historicalCurrentPage.value,
      pageSize: historicalPageSize.value,
      startDate: historicalStartDate.value,
      endDate: historicalEndDate.value,
      includeNotes: historicalIncludeNotes.value
    })
    
    if (response.success) {
      historicalData.value = response.data.map(item => ({
        ...item,
        editing: false,
        saving: false,
        editData: {}
      }))
      historicalTotal.value = response.total
    }
  } catch (error) {
    console.error('获取历史行情数据失败:', error)
    ElMessage.error('获取历史行情数据失败')
  } finally {
    historicalLoading.value = false
  }
}

const handleTabChange = (tab: string | number) => {
  console.log('切换到标签页:', tab)
}

// 股票数据分页相关方法
const handleStockSearch = () => {
  stockCurrentPage.value = 1
  fetchStockData()
}

const handleStockMarketFilter = (_value: string) => {
  stockCurrentPage.value = 1
  fetchStockData()
}

const handleStockSortChange = (_value: string) => {
  stockCurrentPage.value = 1
  fetchStockData()
}

const refreshStockData = () => {
  stockCurrentPage.value = 1
  fetchStockData()
}

const handleStockPageSizeChange = (value: number) => {
  stockPageSize.value = value
  stockCurrentPage.value = 1
  fetchStockData()
}

const handleStockPageChange = (value: number) => {
  stockCurrentPage.value = value
  fetchStockData()
}

// 指数数据分页相关方法
const handleIndexSearch = () => {
  indexCurrentPage.value = 1
  fetchIndexData()
}

const handleIndexSortChange = (_value: string) => {
  indexCurrentPage.value = 1
  fetchIndexData()
}

const refreshIndexData = () => {
  indexCurrentPage.value = 1
  fetchIndexData()
}

const handleIndexPageSizeChange = (value: number) => {
  indexPageSize.value = value
  indexCurrentPage.value = 1
  fetchIndexData()
}

const handleIndexPageChange = (value: number) => {
  indexCurrentPage.value = value
  fetchIndexData()
}

// 行业板块数据分页相关方法
const handleIndustrySearch = () => {
  industryCurrentPage.value = 1
  fetchIndustryData()
}

const handleIndustrySortChange = (_value: string) => {
  industryCurrentPage.value = 1
  fetchIndustryData()
}

const refreshIndustryData = () => {
  industryCurrentPage.value = 1
  fetchIndustryData()
}

const handleIndustryPageSizeChange = (value: number) => {
  industryPageSize.value = value
  industryCurrentPage.value = 1
  fetchIndustryData()
}

const handleIndustryPageChange = (value: number) => {
  industryCurrentPage.value = value
  fetchIndustryData()
}

// 历史行情数据相关方法
const handleHistoricalStockChange = () => {
  historicalCurrentPage.value = 1
  fetchHistoricalData()
}

const handleHistoricalDateChange = () => {
  historicalCurrentPage.value = 1
  fetchHistoricalData()
}

const handleHistoricalIncludeNotesChange = () => {
  historicalCurrentPage.value = 1
  fetchHistoricalData()
}

const refreshHistoricalData = () => {
  historicalCurrentPage.value = 1
  fetchHistoricalData()
}

const handleHistoricalPageSizeChange = (value: number) => {
  historicalPageSize.value = value
  historicalCurrentPage.value = 1
  fetchHistoricalData()
}

const handleHistoricalPageChange = (value: number) => {
  historicalCurrentPage.value = value
  fetchHistoricalData()
}

// 历史行情数据编辑相关方法
const startHistoricalEdit = (row: any) => {
  row.editing = true
  row.editData = {
    open: row.open,
    close: row.close,
    high: row.high,
    low: row.low,
    volume: row.volume,
    amount: row.amount,
    turnover_rate: row.turnover_rate,
    remarks: row.remarks || ''
  }
}

const cancelHistoricalEdit = (row: any) => {
  row.editing = false
  row.editData = {}
}

const validateEditData = (row: any) => {
  // 基本验证逻辑
  const { editData } = row
  
  // 价格验证
  const priceFields = ['open', 'close', 'high', 'low']
  priceFields.forEach(field => {
    if (editData[field] !== undefined && editData[field] !== '') {
      const value = parseFloat(editData[field])
      if (isNaN(value) || value < 0) {
        ElMessage.warning(`${field}价格必须为正数`)
        editData[field] = row[field]
      }
    }
  })
  
  // 成交量、成交额验证
  const volumeFields = ['volume', 'amount']
  volumeFields.forEach(field => {
    if (editData[field] !== undefined && editData[field] !== '') {
      const value = parseFloat(editData[field])
      if (isNaN(value) || value < 0) {
        ElMessage.warning(`${field}必须为正数`)
        editData[field] = row[field]
      }
    }
  })
  
  // 换手率验证
  if (editData.turnover_rate !== undefined && editData.turnover_rate !== '') {
    const value = parseFloat(editData.turnover_rate)
    if (isNaN(value) || value < 0 || value > 100) {
      ElMessage.warning('换手率必须在0-100之间')
      editData.turnover_rate = row.turnover_rate
    }
  }
  
  // 验证价格数据逻辑关系
  if (editData.open && editData.close) {
    const openValue = parseFloat(editData.open)
    const closeValue = parseFloat(editData.close)
    
    if (editData.high && !isNaN(openValue) && !isNaN(closeValue)) {
      const highValue = parseFloat(editData.high)
      if (!isNaN(highValue) && (highValue < openValue || highValue < closeValue)) {
        ElMessage.warning('最高价不能低于开盘价或收盘价')
        return false
      }
    }
    
    if (editData.low && !isNaN(openValue) && !isNaN(closeValue)) {
      const lowValue = parseFloat(editData.low)
      if (!isNaN(lowValue) && (lowValue > openValue || lowValue > closeValue)) {
        ElMessage.warning('最低价不能高于开盘价或收盘价')
        return false
      }
    }
  }
  
  return true
}

const saveHistoricalEdit = async (row: any) => {
  if (!validateEditData(row)) {
    return
  }

  row.saving = true
  try {
    const updateParams = {
      code: row.code,
      date: row.date,
      ...row.editData
    }

    const response = await quotesService.updateHistoricalQuote(updateParams)
    
    if (response.success) {
      // 更新本地数据
      Object.assign(row, row.editData)
      row.editing = false
      row.editData = {}
      ElMessage.success('保存成功')
    } else {
      ElMessage.error(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存历史行情数据失败:', error)
    ElMessage.error('保存失败')
  } finally {
    row.saving = false
  }
}

// 数据格式化函数
const formatPrice = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined) return '-'
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(numValue)) return '-'
  return numValue.toFixed(2)
}

const formatPercent = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined) return '-'
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(numValue)) return '-'
  return `${numValue > 0 ? '+' : ''}${numValue.toFixed(2)}%`
}

const formatVolume = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined) return '-'
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(numValue)) return '-'
  
  if (numValue >= 100000000) {
    return `${(numValue / 100000000).toFixed(2)}亿`
  } else if (numValue >= 10000) {
    return `${(numValue / 10000).toFixed(2)}万`
  }
  return numValue.toLocaleString()
}

const formatAmount = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined) return '-'
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(numValue)) return '-'
  
  if (numValue >= 100000000) {
    return `${(numValue / 100000000).toFixed(2)}亿`
  } else if (numValue >= 10000) {
    return `${(numValue / 10000).toFixed(2)}万`
  }
  return numValue.toLocaleString()
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
  await fetchIndexData()
  await fetchIndustryData()
  // await fetchStockList()  // 注释：初次加载时可加载股票列表，若无需默认加载可注释
  await fetchHistoricalData()  // 添加这行，自动加载历史数据
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

/* 搜索和筛选样式 */
.search-section {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.search-section .el-row {
  margin-bottom: 0;
}

.search-section .el-col {
  display: flex;
  align-items: center;
}

.search-section .el-input,
.search-section .el-select {
  width: 100%;
}

.search-section .el-button {
  width: 100%;
  height: 36px;
}

/* 分页组件样式 */
.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
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