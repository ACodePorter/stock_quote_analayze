/**
 * 日志管理JavaScript模块
 * 提供日志查询、筛选、分页等功能
 */

class LogsManager {
    constructor() {
        this.currentTab = 'historical_collect';
        this.currentPage = 1;
        this.pageSize = 20;
        this.filters = {};
        this.logTables = {};
        this.initialized = false;
    }

    // 字段映射函数，适配不同的表结构
    getFieldMapping(tableKey) {
        const mappings = {
            'operation': {
                'operation_type': 'log_type',
                'operation_desc': 'log_message',
                'affected_rows': 'affected_count',
                'status': 'log_status',
                'error_message': 'error_info',
                'created_at': 'log_time'
            },
            'historical_collect': {
                'operation_type': 'operation_type',
                'operation_desc': 'operation_desc',
                'affected_rows': 'affected_rows',
                'status': 'status',
                'error_message': 'error_message',
                'created_at': 'created_at'
            },
            'realtime_collect': {
                'operation_type': 'operation_type',
                'operation_desc': 'operation_desc',
                'affected_rows': 'affected_rows',
                'status': 'status',
                'error_message': 'error_message',
                'created_at': 'created_at'
            },
            'watchlist_history': {
                'operation_type': null,
                'operation_desc': null,
                'affected_rows': 'affected_rows',
                'status': 'status',
                'error_message': 'error_message',
                'created_at': 'created_at'
            }
        };
        return mappings[tableKey] || mappings['historical_collect'];
    }

    init() {
        if (this.initialized) {
            console.log('LogsManager已经初始化，跳过重复初始化');
            return;
        }
        
        console.log('初始化LogsManager...');
        
        // 简化初始化逻辑，参考dashboard的实现方式
        this.bindEvents();
        this.loadLogTables();
        this.updateTableHeaders();
        this.loadLogs();
        this.loadLogStats();
        
        this.initialized = true;
        console.log('LogsManager初始化完成');
    }

    bindEvents() {
        // 标签页切换
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.getAttribute('data-tab'));
            });
        });

        // 筛选条件变化 - 添加DOM元素存在性检查
        const startDate = document.getElementById('startDate');
        const endDate = document.getElementById('endDate');
        const statusFilter = document.getElementById('statusFilter');
        const operationTypeFilter = document.getElementById('operationTypeFilter');
        const stockCodeInput = document.getElementById('stockCodeInput');

        if (startDate) {
            startDate.addEventListener('change', () => this.updateFilters());
        }
        if (endDate) {
            endDate.addEventListener('change', () => this.updateFilters());
        }
        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.updateFilters());
        }
        if (operationTypeFilter) {
            operationTypeFilter.addEventListener('input', () => this.updateFilters());
        }
        if (stockCodeInput) {
            stockCodeInput.addEventListener('input', () => this.updateFilters());
        }
    }

    async loadLogTables() {
        try {
            const response = await this.apiRequest('/logs/tables');
            if (response.success) {
                this.logTables = response.data.tables.reduce((acc, table) => {
                    acc[table.key] = table;
                    return acc;
                }, {});
            }
        } catch (error) {
            console.error('加载日志表失败:', error);
            this.showToast('加载日志表失败', 'error');
        }
    }

    switchTab(tabKey) {
        // 更新标签页状态
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const activeTab = document.querySelector(`[data-tab="${tabKey}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }

        // 更新当前标签页
        this.currentTab = tabKey;
        this.currentPage = 1;

        // 处理系统操作日志标签页
        if (tabKey === 'operation') {
            // 隐藏通用日志内容，显示系统操作日志内容
            const generalContent = document.getElementById('generalLogsContent');
            const operationContent = document.getElementById('operationLogsContent');
            
            if (generalContent) generalContent.style.display = 'none';
            if (operationContent) operationContent.style.display = 'block';
            
            // 初始化系统操作日志管理器
            if (window.operationLogsManager) {
                window.operationLogsManager.refresh();
            }
            return;
        } else {
            // 显示通用日志内容，隐藏系统操作日志内容
            const generalContent = document.getElementById('generalLogsContent');
            const operationContent = document.getElementById('operationLogsContent');
            
            if (generalContent) generalContent.style.display = 'block';
            if (operationContent) operationContent.style.display = 'none';
        }

        // 显示/隐藏股票代码筛选（仅适用于watchlist_history表）
        const stockCodeFilter = document.getElementById('stockCodeFilter');
        if (stockCodeFilter) {
            if (tabKey === 'watchlist_history') {
                stockCodeFilter.style.display = 'block';
            } else {
                stockCodeFilter.style.display = 'none';
            }
        }

        // 更新表头
        this.updateTableHeaders();

        // 重新加载数据
        this.loadLogs();
    }

    updateTableHeaders() {
        const thead = document.querySelector('#logsTable thead tr');
        if (!thead) return;

        let headers = [];
        
        switch (this.currentTab) {
            case 'watchlist_history':
                headers = ['ID', '股票代码', '操作描述', '影响行数', '状态', '错误信息', '创建时间'];
                break;
            case 'operation':
                headers = ['ID', '日志类型', '日志消息', '影响数量', '日志状态', '错误信息', '日志时间'];
                break;
            default:
                headers = ['ID', '操作类型', '操作描述', '影响行数', '状态', '错误信息', '创建时间'];
        }

        thead.innerHTML = headers.map(header => `<th>${header}</th>`).join('');
    }

    updateFilters() {
        this.filters = {
            start_date: document.getElementById('startDate')?.value || '',
            end_date: document.getElementById('endDate')?.value || '',
            status: document.getElementById('statusFilter')?.value || '',
            operation_type: document.getElementById('operationTypeFilter')?.value || '',
            stock_code: document.getElementById('stockCodeInput')?.value || ''
        };

        // 清除空值
        Object.keys(this.filters).forEach(key => {
            if (!this.filters[key]) {
                delete this.filters[key];
            }
        });
    }

    async loadLogs() {
        try {
            this.showLoading(true);
            
            const params = new URLSearchParams({
                page: this.currentPage,
                page_size: this.pageSize,
                ...this.filters
            });

            const response = await this.apiRequest(`/logs/query/${this.currentTab}?${params}`);
            
            if (response.success) {
                this.renderLogsTable(response.data);
                this.updatePagination(response.data.pagination);
                this.loadLogStats();
            } else {
                console.warn('API请求失败，使用模拟数据:', response.error);
                // 使用模拟数据
                this.showMockData();
            }
        } catch (error) {
            console.error('加载日志失败:', error);
            // 使用模拟数据
            this.showMockData();
        } finally {
            this.showLoading(false);
        }
    }

    showMockData() {
        // 显示模拟数据，确保页面有内容
        const mockData = {
            data: [
                {
                    id: 1,
                    operation_type: '数据采集',
                    operation_desc: '模拟数据采集操作 - 历史数据采集',
                    affected_rows: 100,
                    status: 'success',
                    error_message: null,
                    created_at: new Date().toISOString()
                },
                {
                    id: 2,
                    operation_type: '数据更新',
                    operation_desc: '模拟数据更新操作 - 实时数据同步',
                    affected_rows: 50,
                    status: 'success',
                    error_message: null,
                    created_at: new Date(Date.now() - 3600000).toISOString()
                },
                {
                    id: 3,
                    operation_type: '系统维护',
                    operation_desc: '模拟系统维护操作 - 数据库清理',
                    affected_rows: 25,
                    status: 'partial_success',
                    error_message: '部分数据清理失败',
                    created_at: new Date(Date.now() - 7200000).toISOString()
                }
            ],
            pagination: {
                total: 3,
                page: 1,
                page_size: 20,
                total_pages: 1
            }
        };
        
        this.renderLogsTable(mockData);
        this.updatePagination(mockData.pagination);
        
        // 更新统计信息
        const mockStats = {
            status_stats: [
                { status: 'success', count: 2 },
                { status: 'partial_success', count: 1 },
                { status: 'error', count: 0 }
            ]
        };
        this.updateStatsDisplay(mockStats);
        
        this.showToast('使用模拟数据（API暂时不可用）', 'info');
    }

    renderLogsTable(data) {
        const tbody = document.getElementById('logsTableBody');
        tbody.innerHTML = '';

        if (!data.data || data.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="no-data">暂无数据</td></tr>';
            return;
        }

        const fieldMapping = this.getFieldMapping(this.currentTab);

        data.data.forEach(log => {
            const row = document.createElement('tr');
            
            // 根据当前标签页决定显示内容
            if (this.currentTab === 'watchlist_history') {
                // 自选股历史采集日志特殊处理
                row.innerHTML = `
                    <td>${log.id}</td>
                    <td>${log.stock_code || '-'}</td>
                    <td class="log-desc">-</td>
                    <td>${log.affected_rows || '-'}</td>
                    <td><span class="status-badge status-${log.status}">${this.formatStatus(log.status)}</span></td>
                    <td class="error-message">${this.formatErrorMessage(log.error_message)}</td>
                    <td>${this.formatDate(log.created_at)}</td>
                `;
            } else {
                // 其他日志表使用字段映射
                const operationType = fieldMapping.operation_type ? log[fieldMapping.operation_type] : '-';
                const operationDesc = fieldMapping.operation_desc ? log[fieldMapping.operation_desc] : '-';
                const affectedRows = fieldMapping.affected_rows ? log[fieldMapping.affected_rows] : '-';
                const status = fieldMapping.status ? log[fieldMapping.status] : '-';
                const errorMessage = fieldMapping.error_message ? log[fieldMapping.error_message] : '-';
                const createdAt = fieldMapping.created_at ? log[fieldMapping.created_at] : '-';
                
                row.innerHTML = `
                    <td>${log.id}</td>
                    <td>${operationType || '-'}</td>
                    <td class="log-desc">${this.formatLogDescription(operationDesc)}</td>
                    <td>${affectedRows || '-'}</td>
                    <td><span class="status-badge status-${status}">${this.formatStatus(status)}</span></td>
                    <td class="error-message">${this.formatErrorMessage(errorMessage)}</td>
                    <td>${this.formatDate(createdAt)}</td>
                `;
            }
            tbody.appendChild(row);
        });
    }

    formatLogDescription(desc) {
        if (!desc || desc === '-') return '-';
        // 限制描述长度，避免表格过宽
        return desc.length > 100 ? desc.substring(0, 100) + '...' : desc;
    }

    formatStatus(status) {
        const statusMap = {
            'success': '成功',
            'error': '失败',
            'partial_success': '部分成功'
        };
        return statusMap[status] || status;
    }

    formatErrorMessage(error) {
        if (!error || error === '-') return '-';
        // 限制错误信息长度
        return error.length > 50 ? error.substring(0, 50) + '...' : error;
    }

    formatDate(dateStr) {
        if (!dateStr) return '-';
        try {
            const date = new Date(dateStr);
            return date.toLocaleString('zh-CN');
        } catch (e) {
            return dateStr;
        }
    }

    updatePagination(pagination) {
        const paginationInfo = document.getElementById('paginationInfo');
        paginationInfo.textContent = `第 ${pagination.page} 页，共 ${pagination.total_pages} 页 (共 ${pagination.total_count} 条记录)`;

        // 更新分页按钮状态
        const prevBtn = document.querySelector('.pagination-btn:first-child');
        const nextBtn = document.querySelector('.pagination-btn:last-child');
        
        prevBtn.disabled = pagination.page <= 1;
        nextBtn.disabled = pagination.page >= pagination.total_pages;
    }

    async loadLogStats() {
        try {
            // 获取全部数据的统计信息（不传days参数）
            const response = await this.apiRequest(`/logs/stats/${this.currentTab}`);
            
            if (response.success) {
                this.updateStatsDisplay(response.data);
            }
        } catch (error) {
            console.error('加载统计信息失败:', error);
        }
    }

    updateStatsDisplay(stats) {
        let totalCount = 0;
        let successCount = 0;
        let errorCount = 0;
        let partialSuccessCount = 0;

        // 计算统计数据
        stats.status_stats.forEach(item => {
            totalCount += item.count;
            if (item.status === 'success') {
                successCount += item.count;
            } else if (item.status === 'error') {
                errorCount += item.count;
            } else if (item.status === 'partial_success') {
                partialSuccessCount += item.count;
            }
        });

        // 更新显示
        document.getElementById('totalLogs').textContent = totalCount;
        document.getElementById('successLogs').textContent = successCount;
        // 失败记录包括error和partial_success
        document.getElementById('errorLogs').textContent = errorCount + partialSuccessCount;
        
        // 计算成功率（只包括完全成功的记录）
        const successRate = totalCount > 0 ? Math.round((successCount / totalCount) * 100) : 0;
        document.getElementById('successRate').textContent = `${successRate}%`;
    }

    async apiRequest(endpoint, options = {}) {
        const token = localStorage.getItem(ADMIN_CONFIG.AUTH.TOKEN_KEY);
        
        if (!token) {
            console.error('认证token不存在，请重新登录');
            return { success: false, error: '认证token不存在，请重新登录' };
        }
        
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(`${ADMIN_CONFIG.API.BASE_URL}${endpoint}`, finalOptions);
            
            if (response.status === 401) {
                console.error('认证失败，请重新登录');
                // 清除无效token
                localStorage.removeItem(ADMIN_CONFIG.AUTH.TOKEN_KEY);
                return { success: false, error: '认证失败，请重新登录' };
            }
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return { success: true, data };
        } catch (error) {
            console.error('API请求失败:', error);
            return { success: false, error: error.message };
        }
    }

    showLoading(show) {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = show ? 'flex' : 'none';
        }
    }

    showToast(message, type = 'info') {
        // 创建toast元素
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // 添加到页面
        document.body.appendChild(toast);
        
        // 显示动画
        setTimeout(() => toast.classList.add('show'), 100);
        
        // 自动移除
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }

    // 公共方法，供全局函数调用
    refresh() {
        if (!this.initialized) {
            this.init();
        } else {
            // 如果当前是系统操作日志标签页，调用操作日志管理器的刷新方法
            if (this.currentTab === 'operation' && window.operationLogsManager) {
                window.operationLogsManager.refresh();
            } else {
                this.loadLogs();
                this.loadLogStats();
            }
        }
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.loadLogs();
        }
    }

    nextPage() {
        this.currentPage++;
        this.loadLogs();
    }

    applyFilters() {
        this.updateFilters();
        this.currentPage = 1;
        this.loadLogs();
    }

    clearFilters() {
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';
        document.getElementById('statusFilter').value = '';
        document.getElementById('operationTypeFilter').value = '';
        document.getElementById('stockCodeInput').value = '';
        
        this.filters = {};
        this.currentPage = 1;
        this.loadLogs();
    }

    exportLogs() {
        // 如果当前是系统操作日志标签页，调用操作日志管理器的导出方法
        if (this.currentTab === 'operation' && window.operationLogsManager) {
            window.operationLogsManager.exportData();
        } else {
            // 导出功能实现
            this.showToast('导出功能开发中...', 'info');
        }
    }
}

// 全局变量
let logsManager = null;
let isInitializing = false; // 添加初始化状态标志

// 自动初始化函数
function initLogsManager() {
    console.log('尝试初始化LogsManager...');
    
    // 防止重复初始化
    if (isInitializing) {
        console.log('LogsManager正在初始化中，跳过重复调用');
        return;
    }
    
    // 简化初始化逻辑，参考dashboard的实现方式
    if (typeof LogsManager !== 'undefined') {
        if (!window.logsManager) {
            console.log('创建新的LogsManager实例');
            isInitializing = true;
            try {
                window.logsManager = new LogsManager();
                window.logsManager.init(); // 确保调用init方法
                console.log('LogsManager创建并初始化成功');
            } catch (error) {
                console.error('LogsManager创建失败:', error);
            } finally {
                isInitializing = false;
            }
        } else {
            console.log('LogsManager已经存在，刷新数据');
            try {
                if (!window.logsManager.initialized) {
                    window.logsManager.init();
                }
                window.logsManager.refresh();
            } catch (error) {
                console.error('LogsManager刷新失败:', error);
            }
        }
    } else {
        console.error('LogsManager类未定义，logs.js可能未正确加载');
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initLogsManager, 100);
});

// 监听页面切换事件
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('nav-link') && e.target.getAttribute('data-page') === 'logs') {
        setTimeout(initLogsManager, 100);
    }
});

// 暴露初始化函数到全局作用域
window.initLogsManager = initLogsManager;

// 全局函数，供HTML调用
function refreshLogs() {
    if (window.logsManager) {
        window.logsManager.refresh();
    }
}

function previousPage() {
    if (window.logsManager) {
        window.logsManager.previousPage();
    }
}

function nextPage() {
    if (window.logsManager) {
        window.logsManager.nextPage();
    }
}

function applyFilters() {
    if (window.logsManager) {
        window.logsManager.applyFilters();
    }
}

function clearFilters() {
    if (window.logsManager) {
        window.logsManager.clearFilters();
    }
}

function exportLogs() {
    if (window.logsManager) {
        window.logsManager.exportLogs();
    }
}


