
// 全局API前缀
//const API_BASE_URL = Config ? Config.getApiBaseUrl() : 'http://192.168.31.237:5000';

// 股票历史行情页面JavaScript
class StockHistoryPage {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 20;
        this.totalPages = 0;
        this.currentStockCode = '';
        this.currentStockName = '';
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.setDefaultDates();
        this.loadStockFromUrl();
    }
    
    bindEvents() {
        // 查询按钮
        document.getElementById('searchBtn').addEventListener('click', () => {
            this.searchHistory();
        });
        
        // 导出按钮
        document.getElementById('exportBtn').addEventListener('click', () => {
            this.exportHistory();
        });
        
        // 分页按钮
        document.getElementById('firstPage').addEventListener('click', () => {
            this.goToPage(1);
        });
        
        document.getElementById('prevPage').addEventListener('click', () => {
            this.goToPage(this.currentPage - 1);
        });
        
        document.getElementById('nextPage').addEventListener('click', () => {
            this.goToPage(this.currentPage + 1);
        });
        
        document.getElementById('lastPage').addEventListener('click', () => {
            this.goToPage(this.totalPages);
        });
        
        // 回车键搜索
        document.getElementById('startDate').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchHistory();
        });
        
        document.getElementById('endDate').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchHistory();
        });
    }
    
    setDefaultDates() {
        const today = new Date();
        const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
        
        document.getElementById('startDate').value = this.formatDate(thirtyDaysAgo);
        document.getElementById('endDate').value = this.formatDate(today);
    }
    
    formatDate(date) {
        return date.toISOString().split('T')[0];
    }
    
    loadStockFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        const stockCode = urlParams.get('code');
        
        if (stockCode) {
            this.currentStockCode = stockCode;
            this.searchHistory();
        }
    }
    
    async searchHistory() {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        const includeNotes = document.getElementById('includeNotes').checked;
        
        if (!this.currentStockCode) {
            alert('请先选择股票');
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/stock/history?code=${this.currentStockCode}&start_date=${startDate}&end_date=${endDate}&include_notes=${includeNotes}&page=${this.currentPage}&size=${this.pageSize}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.displayHistory(data.items);
            this.updatePagination(data.total);
            
        } catch (error) {
            console.error('查询历史行情失败:', error);
            alert('查询失败: ' + error.message);
        }
    }
    
    displayHistory(items) {
        const tbody = document.querySelector('#historyTable tbody');
        tbody.innerHTML = '';
        
        if (!items || items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="15" style="text-align: center; padding: 20px;">暂无数据</td></tr>';
            return;
        }
        
        items.forEach(item => {
            const row = document.createElement('tr');
            
            // 设置涨跌样式
            if (item.change_percent > 0) {
                row.classList.add('row-up');
            } else if (item.change_percent < 0) {
                row.classList.add('row-down');
            }
            
            row.innerHTML = `
                <td>${item.code}</td>
                <td>${item.name}</td>
                <td>${item.date}</td>
                <td>${this.formatNumber(item.open)}</td>
                <td>${this.formatNumber(item.close)}</td>
                <td>${this.formatNumber(item.high)}</td>
                <td>${this.formatNumber(item.low)}</td>
                <td>${this.formatVolume(item.volume)}</td>
                <td>${this.formatAmount(item.amount)}</td>
                <td class="${item.change_percent > 0 ? 'cell-up' : item.change_percent < 0 ? 'cell-down' : ''}">${this.formatPercent(item.change_percent)}</td>
                <td class="${item.change > 0 ? 'cell-up' : item.change < 0 ? 'cell-down' : ''}">${this.formatNumber(item.change)}</td>
                <td>${this.formatPercent(item.turnover_rate)}</td>
                <td class="${item.cumulative_change_percent > 0 ? 'cell-up' : item.cumulative_change_percent < 0 ? 'cell-down' : ''}">${this.formatPercent(item.cumulative_change_percent)}</td>
                <td class="${item.five_day_change_percent > 0 ? 'cell-up' : item.five_day_change_percent < 0 ? 'cell-down' : ''}">${this.formatPercent(item.five_day_change_percent)}</td>
                <td class="notes-cell ${item.remarks ? 'has-notes' : ''}" onclick="stockHistoryPage.editNote('${item.code}', '${item.date}', '${item.remarks || ''}')">${item.remarks || '点击添加'}</td>
            `;
            
            tbody.appendChild(row);
        });
        
        // 更新股票信息
        if (items.length > 0) {
            this.currentStockName = items[0].name;
        }
    }
    
    formatNumber(num) {
        if (num === null || num === undefined) return '-';
        return Number(num).toFixed(2);
    }
    
    formatPercent(num) {
        if (num === null || num === undefined) return '-';
        return Number(num).toFixed(2) + '%';
    }
    
    formatVolume(volume) {
        if (volume === null || volume === undefined) return '-';
        const vol = Number(volume);
        if (vol >= 10000) {
            return (vol / 10000).toFixed(2) + '万';
        }
        return vol.toFixed(0);
    }
    
    formatAmount(amount) {
        if (amount === null || amount === undefined) return '-';
        const amt = Number(amount);
        if (amt >= 100000000) {
            return (amt / 100000000).toFixed(2) + '亿';
        } else if (amt >= 10000) {
            return (amt / 10000).toFixed(2) + '万';
        }
        return amt.toFixed(0);
    }
    
    updatePagination(total) {
        this.totalPages = Math.ceil(total / this.pageSize);
        
        document.getElementById('pageInfo').textContent = `第 ${this.currentPage} 页，共 ${this.totalPages} 页，总计 ${total} 条`;
        
        // 更新按钮状态
        document.getElementById('firstPage').disabled = this.currentPage === 1;
        document.getElementById('prevPage').disabled = this.currentPage === 1;
        document.getElementById('nextPage').disabled = this.currentPage === this.totalPages;
        document.getElementById('lastPage').disabled = this.currentPage === this.totalPages;
    }
    
    goToPage(page) {
        if (page < 1 || page > this.totalPages) return;
        
        this.currentPage = page;
        this.searchHistory();
    }
    
    async exportHistory() {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        const includeNotes = document.getElementById('includeNotes').checked;
        
        if (!this.currentStockCode) {
            alert('请先选择股票');
                return;
            }
        
        try {
            const url = `${API_BASE_URL}/api/stock/history/export?code=${this.currentStockCode}&start_date=${startDate}&end_date=${endDate}&include_notes=${includeNotes}`;
            
            // 创建下载链接
            const link = document.createElement('a');
            link.href = url;
            link.download = `${this.currentStockCode}_历史行情_${new Date().toISOString().slice(0, 10)}.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
        } catch (error) {
            console.error('导出失败:', error);
            alert('导出失败: ' + error.message);
        }
    }
    
    editNote(stockCode, tradeDate, currentNotes) {
        document.getElementById('noteStockCode').value = stockCode;
        document.getElementById('noteTradeDate').value = tradeDate;
        document.getElementById('noteContent').value = currentNotes;
        
        // 显示弹窗
        document.getElementById('notesModal').style.display = 'block';
        
        // 绑定弹窗事件
        this.bindModalEvents();
    }
    
    bindModalEvents() {
        const modal = document.getElementById('notesModal');
        const closeBtn = document.querySelector('.close-notes');
        const saveBtn = document.getElementById('saveNoteBtn');
        const deleteBtn = document.getElementById('deleteNoteBtn');
        const cancelBtn = document.getElementById('cancelNoteBtn');
        
        // 关闭弹窗
        closeBtn.onclick = () => modal.style.display = 'none';
        
        // 点击弹窗外部关闭
        modal.onclick = (e) => {
            if (e.target === modal) modal.style.display = 'none';
        };
        
        // 保存备注
        saveBtn.onclick = () => this.saveNote();
        
        // 删除备注
        deleteBtn.onclick = () => this.deleteNote();
        
        // 取消
        cancelBtn.onclick = () => modal.style.display = 'none';
    }
    
    async saveNote() {
        const stockCode = document.getElementById('noteStockCode').value;
        const tradeDate = document.getElementById('noteTradeDate').value;
        const notes = document.getElementById('noteContent').value;
        const strategyType = document.getElementById('noteStrategyType').value;
        const riskLevel = document.getElementById('noteRiskLevel').value;
        
        if (!notes.trim()) {
            alert('请输入备注内容');
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/trading_notes/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    stock_code: stockCode,
                    trade_date: tradeDate,
                    notes: notes,
                    strategy_type: strategyType,
                    risk_level: riskLevel,
                    created_by: 'wangxw1' // 这里应该从用户登录信息获取
                })
            });
            
            if (response.ok) {
                alert('备注保存成功');
                document.getElementById('notesModal').style.display = 'none';
                this.searchHistory(); // 刷新数据
            } else {
                throw new Error('保存失败');
            }
            
        } catch (error) {
            console.error('保存备注失败:', error);
            alert('保存失败: ' + error.message);
        }
    }
    
    async deleteNote() {
        const stockCode = document.getElementById('noteStockCode').value;
        const tradeDate = document.getElementById('noteTradeDate').value;
        
        if (!confirm('确定要删除这条备注吗？')) return;
        
        try {
            // 这里需要先查询备注ID，然后删除
            // 简化处理，直接提示用户手动删除
            alert('删除功能需要备注ID，请通过管理界面删除');
            document.getElementById('notesModal').style.display = 'none';
            
        } catch (error) {
            console.error('删除备注失败:', error);
            alert('删除失败: ' + error.message);
        }
    }
    }

    // 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.stockHistoryPage = new StockHistoryPage();
}); 