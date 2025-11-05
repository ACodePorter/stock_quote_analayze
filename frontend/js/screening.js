// 选股页面功能模块
const ScreeningPage = {
    API_BASE_URL: Config ? Config.getApiBaseUrl() : 'http://192.168.31.237:5000',
    
    // 初始化
    async init() {
        await this.loadHeader();
        this.bindEvents();
    },
    
    // 加载头部导航
    async loadHeader() {
        try {
            const headerContainer = document.getElementById('header-container');
            if (headerContainer) {
                // 动态加载头部组件HTML
                const response = await fetch('components/header.html');
                if (response.ok) {
                    const headerHtml = await response.text();
                    headerContainer.innerHTML = headerHtml;
                    
                    // 等待DOM更新后初始化头部功能
                    setTimeout(() => {
                        // 高亮当前频道
                        const nav = document.getElementById('nav-screening');
                        if (nav) {
                            nav.classList.add('active');
                        }
                        
                        // 初始化用户菜单
                        if (typeof initUserMenu === 'function') {
                            initUserMenu();
                        }
                        
                        // 初始化股票搜索功能
                        if (typeof initStockSearch === 'function') {
                            initStockSearch();
                        } else {
                            console.warn('initStockSearch函数未找到，等待header.js加载');
                            // 等待header.js加载完成
                            const checkInterval = setInterval(() => {
                                if (typeof initStockSearch === 'function') {
                                    initStockSearch();
                                    clearInterval(checkInterval);
                                }
                            }, 100);
                            
                            // 5秒后停止检查
                            setTimeout(() => clearInterval(checkInterval), 5000);
                        }
                        
                        // 更新用户显示
                        if (window.CommonUtils && window.CommonUtils.auth) {
                            CommonUtils.auth.updateUserDisplay(CommonUtils.auth.getUserInfo());
                        }
                    }, 100);
                }
            }
        } catch (error) {
            console.error('加载头部导航失败:', error);
        }
    },
    
    // 绑定事件
    bindEvents() {
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadScreeningResults();
            });
        }
    },
    
    // 加载选股结果
    async loadScreeningResults() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const errorMessage = document.getElementById('errorMessage');
        const resultsTableBody = document.getElementById('resultsTableBody');
        const resultsCount = document.getElementById('resultsCount');
        const refreshBtn = document.getElementById('refreshBtn');
        const searchDate = document.getElementById('searchDate');
        
        // 显示加载状态
        if (loadingIndicator) {
            loadingIndicator.style.display = 'flex';
        }
        if (errorMessage) {
            errorMessage.style.display = 'none';
            errorMessage.textContent = '';
        }
        if (refreshBtn) {
            refreshBtn.disabled = true;
        }
        
        try {
            // 获取API基础URL
            const apiBaseUrl = this.API_BASE_URL;
            const url = `${apiBaseUrl}/api/screening/cyb-midline-strategy?months=4`;
            
            // 使用authFetch或fetch
            const fetchFn = (typeof authFetch === 'function')
                ? authFetch
                : async (url, options) => {
                    const token = localStorage.getItem('access_token');
                    const headers = options?.headers || {};
                    if (token) {
                        headers['Authorization'] = 'Bearer ' + token;
                    }
                    return fetch(url, { ...options, headers });
                };
            
            const response = await fetchFn(url);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || result.message || '请求失败');
            }
            
            if (result.success && result.data) {
                this.renderResults(result.data, result.search_date);
                if (searchDate) {
                    searchDate.textContent = `筛选时间: ${result.search_date}`;
                }
            } else {
                throw new Error(result.message || '未找到符合条件的股票');
            }
            
        } catch (error) {
            console.error('加载选股结果失败:', error);
            if (errorMessage) {
                errorMessage.textContent = `加载失败: ${error.message}`;
                errorMessage.style.display = 'block';
            }
            if (resultsTableBody) {
                resultsTableBody.innerHTML = '<tr><td colspan="12" class="empty-state">加载失败，请稍后重试</td></tr>';
            }
            if (resultsCount) {
                resultsCount.textContent = '共找到 0 只符合条件的股票';
            }
        } finally {
            // 隐藏加载状态
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            if (refreshBtn) {
                refreshBtn.disabled = false;
            }
        }
    },
    
    // 渲染结果
    renderResults(data, searchDate) {
        const resultsTableBody = document.getElementById('resultsTableBody');
        const resultsCount = document.getElementById('resultsCount');
        
        if (!resultsTableBody) {
            return;
        }
        
        if (!data || data.length === 0) {
            resultsTableBody.innerHTML = '<tr><td colspan="12" class="empty-state">未找到符合条件的股票</td></tr>';
            if (resultsCount) {
                resultsCount.textContent = '共找到 0 只符合条件的股票';
            }
            return;
        }
        
        // 更新计数
        if (resultsCount) {
            resultsCount.textContent = `共找到 ${data.length} 只符合条件的股票`;
        }
        
        // 渲染表格
        let html = '';
        data.forEach((stock, index) => {
            const changePercent = stock.current_change_percent || 0;
            const changeClass = changePercent > 0 ? 'price-positive' : (changePercent < 0 ? 'price-negative' : 'price-neutral');
            const changeSymbol = changePercent > 0 ? '+' : '';
            
            html += `
                <tr>
                    <td><span class="stock-code">${stock.code}</span></td>
                    <td><span class="stock-name">${stock.name}</span></td>
                    <td>${stock.limit_up_date}</td>
                    <td>${stock.limit_up_price.toFixed(2)}</td>
                    <td>${stock.breakthrough_date}</td>
                    <td>${stock.breakthrough_price.toFixed(2)}</td>
                    <td>${stock.current_price.toFixed(2)}</td>
                    <td class="${changeClass}">${changeSymbol}${changePercent.toFixed(2)}%</td>
                    <td>${stock.ma5.toFixed(2)}</td>
                    <td>${stock.ma10.toFixed(2)}</td>
                    <td>${stock.ma20.toFixed(2)}</td>
                    <td>
                        <div class="action-links">
                            <a href="stock_history.html?code=${stock.code}" class="action-link" target="_blank">历史</a>
                            <a href="stock.html?code=${stock.code}&name=${encodeURIComponent(stock.name)}" class="action-link" target="_blank">详情</a>
                        </div>
                    </td>
                </tr>
            `;
        });
        
        resultsTableBody.innerHTML = html;
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    ScreeningPage.init();
});

