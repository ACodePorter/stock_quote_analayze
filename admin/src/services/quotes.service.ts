import { apiService } from './api'
import { getCurrentEnvConfig } from '@/config/environment'

export interface StockQuoteParams {
  page: number
  pageSize: number
  keyword?: string
  market?: string
  sortBy?: string
}

export interface IndexQuoteParams {
  page: number
  pageSize: number
  keyword?: string
  sortBy?: string
}

export interface IndustryQuoteParams {
  page: number
  pageSize: number
  keyword?: string
  sortBy?: string
}

export interface QuotesResponse<T> {
  success: boolean
  data: T[]
  total: number
  page: number
  pageSize: number
  message?: string
}

export interface QuotesStats {
  totalStocks: number
  totalIndices: number
  totalIndustries: number
  lastUpdateTime: string
}

class QuotesService {
  private getQuotesApiUrl(endpoint: string): string {
    // 使用独立的API基础URL来访问行情数据
    const config = getCurrentEnvConfig()
    const baseUrl = config.apiBaseUrl.replace('/api/admin', '/api')
    return `${baseUrl}/quotes${endpoint}`
  }

  /**
   * 获取股票实时行情数据
   */
  async getStockQuotes(params: StockQuoteParams): Promise<QuotesResponse<any>> {
    const queryParams = new URLSearchParams()
    queryParams.append('page', params.page.toString())
    queryParams.append('page_size', params.pageSize.toString())
    
    if (params.keyword) {
      queryParams.append('keyword', params.keyword)
    }
    if (params.market) {
      queryParams.append('market', params.market)
    }
    if (params.sortBy) {
      queryParams.append('sort_by', params.sortBy)
    }
    
    return apiService.get<QuotesResponse<any>>(this.getQuotesApiUrl(`/stocks?${queryParams}`))
  }

  /**
   * 获取指数实时行情数据
   */
  async getIndexQuotes(params: IndexQuoteParams): Promise<QuotesResponse<any>> {
    const queryParams = new URLSearchParams()
    queryParams.append('page', params.page.toString())
    queryParams.append('page_size', params.pageSize.toString())
    
    if (params.keyword) {
      queryParams.append('keyword', params.keyword)
    }
    if (params.sortBy) {
      queryParams.append('sort_by', params.sortBy)
    }
    
    return apiService.get<QuotesResponse<any>>(this.getQuotesApiUrl(`/indices?${queryParams}`))
  }

  /**
   * 获取行业板块实时行情数据
   */
  async getIndustryQuotes(params: IndustryQuoteParams): Promise<QuotesResponse<any>> {
    const queryParams = new URLSearchParams()
    queryParams.append('page', params.page.toString())
    queryParams.append('page_size', params.pageSize.toString())
    
    if (params.keyword) {
      queryParams.append('keyword', params.keyword)
    }
    if (params.sortBy) {
      queryParams.append('sort_by', params.sortBy)
    }
    
    return apiService.get<QuotesResponse<any>>(this.getQuotesApiUrl(`/industries?${queryParams}`))
  }

  /**
   * 获取行情数据统计信息
   */
  async getQuotesStats(): Promise<{ success: boolean; data: QuotesStats }> {
    return apiService.get<{ success: boolean; data: QuotesStats }>(this.getQuotesApiUrl('/stats'))
  }

  /**
   * 刷新所有行情数据
   */
  async refreshAllQuotes(): Promise<{ success: boolean; message: string }> {
    return apiService.post<{ success: boolean; message: string }>(this.getQuotesApiUrl('/refresh'))
  }
}

export const quotesService = new QuotesService()
