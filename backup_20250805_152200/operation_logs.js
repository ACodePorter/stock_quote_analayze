/**
 * 系统操作日志独立JavaScript模块
 * 专门处理operation_logs表的显示和交互
 */

class OperationLogsManager {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 20;
        this.filters = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadData();
        this.loadStats();
    }

    bindEvents() {
        // 筛选条件变化 - 使用主管理后台中的元素ID
        document.getElementById('operationStartDate').addEventListener('change', () => this.updateFilters());
        document.getElementById('operationEndDate').addEventListener('change', () => this.updateFilters());
        document.getElementById('operationLogStatusFilter').addEventListener('change', () => this.updateFilters());
        document.getElementById('operationLogTypeFilter').addEventListener('input', () => this.updateFilters());
    }

    updateFilters() {
        this.filters = {
            start_date: document.getElementById('operationStartDate').value,
            end_date: document.getElementById('operationEndDate').value,
            log_status: document.getElementById('operationLogStatusFilter').value,
            log_type: document.getElementById('operationLogTypeFilter').value
        };

        // 清除空值
        Object.keys(this.filters).forEach(key => {
            if (!this.filters[key]) {
                delete this.filters[key];
            }
        });
    }

    async loadData() {
        try {
            this.showLoading(true);
            
            const params = new URLSearchParams({
                page: this.currentPage,
                page_size: this.pageSize,
                ...this.filters
            });

            const response = await this.apiRequest(`/operation-logs/query?${params}`);
            
            if (response.success) {
                this.renderTable(response.data);
                this.updatePagination(response.data.pagination);
            } else {
                this.showToast('加载日志数据失败', 'error');
            }
        } catch (error) {
            console.error('加载日志失败:', error);
            this.showToast('加载日志数据失败', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async loadStats() {
        try {
            const response = await this.apiRequest('/operation-logs/stats');
            
            if (response.success) {
                this.updateStatsDisplay(response.data);
            }
        } catch (error) {
            console.error('加载统计信息失败:', error);
        }
    }

    renderTable(data) {
        const tbody = document.getElementById('operationLogsTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';

        if (!data.data || data.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="no-data">暂无数据</td></tr>';
            return;
        }

        data.data.forEach(log => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${log.id}</td>
                <td>${log.log_type || '-'}</td>
                <td class="log-message">${this.formatLogMessage(log.log_message)}</td>
                <td>${log.affected_count || '-'}</td>
                <td><span class="status-badge status-${this.getStatusClass(log.log_status)}">${this.formatStatus(log.log_status)}</span></td>
                <td class="error-message">${this.formatErrorMessage(log.error_info)}</td>
                <td>${this.formatDate(log.log_time)}</td>
            `;
            tbody.appendChild(row);
        });
    }

    formatLogMessage(message) {
        if (!message || message === '-') return '-';
        // 限制消息长度，避免表格过宽
        return message.length > 100 ? message.substring(0, 100) + '...' : message;
    }

    formatStatus(status) {
        if (!status) return '-';
        return status;
    }

    getStatusClass(status) {
        if (!status) return '';
        if (status === '成功') return 'success';
        if (status === '失败') return 'error';
        return '';
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
        const paginationInfo = document.getElementById('operationPaginationInfo');
        if (!paginationInfo) return;
        
        paginationInfo.textContent = `第 ${pagination.page} 页，共 ${pagination.total_pages} 页 (共 ${pagination.total_count} 条记录)`;

        // 更新分页按钮状态
        const paginationContainer = document.getElementById('operationLogsPagination');
        if (!paginationContainer) return;
        
        const prevBtn = paginationContainer.querySelector('.pagination-btn:first-child');
        const nextBtn = paginationContainer.querySelector('.pagination-btn:last-child');
        
        if (prevBtn) prevBtn.disabled = pagination.page <= 1;
        if (nextBtn) nextBtn.disabled = pagination.page >= pagination.total_pages;
    }

    updateStatsDisplay(stats) {
        let totalCount = 0;
        let successCount = 0;
        let errorCount = 0;

        // 计算统计数据
        stats.status_stats.forEach(item => {
            totalCount += item.count;
            if (item.status === '成功') {
                successCount += item.count;
            } else if (item.status === '失败') {
                errorCount += item.count;
            }
        });

        // 更新显示 - 使用主管理后台中的元素ID
        const totalElement = document.getElementById('operationTotalLogs');
        const successElement = document.getElementById('operationSuccessLogs');
        const errorElement = document.getElementById('operationErrorLogs');
        const rateElement = document.getElementById('operationSuccessRate');
        
        if (totalElement) totalElement.textContent = totalCount;
        if (successElement) successElement.textContent = successCount;
        if (errorElement) errorElement.textContent = errorCount;
        
        // 计算成功率
        const successRate = totalCount > 0 ? Math.round((successCount / totalCount) * 100) : 0;
        if (rateElement) rateElement.textContent = `${successRate}%`;
    }

    async apiRequest(endpoint, options = {}) {
        const token = localStorage.getItem(ADMIN_CONFIG.AUTH.TOKEN_KEY);
        
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
        this.loadData();
        this.loadStats();
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.loadData();
        }
    }

    nextPage() {
        this.currentPage++;
        this.loadData();
    }

    applyFilters() {
        this.updateFilters();
        this.currentPage = 1;
        this.loadData();
        this.loadStats();
    }

    clearFilters() {
        const startDateElement = document.getElementById('operationStartDate');
        const endDateElement = document.getElementById('operationEndDate');
        const statusElement = document.getElementById('operationLogStatusFilter');
        const typeElement = document.getElementById('operationLogTypeFilter');
        
        if (startDateElement) startDateElement.value = '';
        if (endDateElement) endDateElement.value = '';
        if (statusElement) statusElement.value = '';
        if (typeElement) typeElement.value = '';
        
        this.filters = {};
        this.currentPage = 1;
        this.loadData();
        this.loadStats();
    }

    exportData() {
        // 导出功能实现
        this.showToast('导出功能开发中...', 'info');
    }
}

// 全局变量
let operationLogsManager = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 延迟初始化，等待主管理后台加载完成
    setTimeout(() => {
        if (document.getElementById('operationLogsContent')) {
            operationLogsManager = new OperationLogsManager();
            // 将管理器暴露到全局作用域，供其他脚本使用
            window.operationLogsManager = operationLogsManager;
        }
    }, 100);
});

// 全局函数，供HTML调用
function refreshOperationData() {
    if (operationLogsManager) {
        operationLogsManager.refresh();
    }
}

function operationPreviousPage() {
    if (operationLogsManager) {
        operationLogsManager.previousPage();
    }
}

function operationNextPage() {
    if (operationLogsManager) {
        operationLogsManager.nextPage();
    }
}

function applyOperationFilters() {
    if (operationLogsManager) {
        operationLogsManager.applyFilters();
    }
}

function clearOperationFilters() {
    if (operationLogsManager) {
        operationLogsManager.clearFilters();
    }
}

function exportOperationData() {
    if (operationLogsManager) {
        operationLogsManager.exportData();
    }
} 