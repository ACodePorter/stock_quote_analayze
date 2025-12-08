// 选股页面功能模块
const ScreeningPage = {
    API_BASE_URL: Config ? Config.getApiBaseUrl() : 'http://192.168.31.237:5000',
    currentStrategy: 'cyb-midline', // 当前选中的策略

    // 初始化
    async init() {
        await this.loadHeader();
        this.bindEvents();
        this.initStrategyTabs();
    },

    // 初始化策略标签页
    initStrategyTabs() {
        const tabs = document.querySelectorAll('.strategy-tab');
        tabs.forEach(tab => {
            // 跳过隐藏的标签页（停机坪、回踩年线、高而窄的旗形）
            const hiddenStrategies = ['parking-apron', 'backtrace-ma250', 'high-tight-flag'];
            if (hiddenStrategies.includes(tab.dataset.strategy)) {
                return; // 跳过隐藏的策略
            }
            
            tab.addEventListener('click', () => {
                const strategy = tab.dataset.strategy;
                this.switchStrategy(strategy);
            });
        });
    },

    // 切换策略标签页
    switchStrategy(strategy) {
        // 检查是否为隐藏的策略
        const hiddenStrategies = ['parking-apron', 'backtrace-ma250', 'high-tight-flag'];
        if (hiddenStrategies.includes(strategy)) {
            console.warn(`策略 ${strategy} 已被隐藏，无法切换`);
            return;
        }
        
        this.currentStrategy = strategy;

        // 更新标签页状态
        document.querySelectorAll('.strategy-tab').forEach(t => {
            t.classList.remove('active');
        });
        const targetTab = document.querySelector(`[data-strategy="${strategy}"]`);
        if (targetTab) {
            targetTab.classList.add('active');
        }

        // 更新内容区域显示
        document.querySelectorAll('.strategy-content').forEach(c => {
            c.classList.remove('active');
        });
        const targetContent = document.getElementById(`${strategy}-content`);
        if (targetContent) {
            targetContent.classList.add('active');
        }
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
        // 绑定所有刷新按钮
        document.querySelectorAll('.refresh-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const strategy = btn.dataset.strategy;
                this.loadScreeningResults(strategy);
            });
        });
    },

    // 加载选股结果
    async loadScreeningResults(strategy = null) {
        if (!strategy) {
            strategy = this.currentStrategy;
        }

        let suffix;
        if (strategy === 'cyb-midline') {
            suffix = 'cyb';
        } else if (strategy === 'parking-apron') {
            suffix = 'parking';
        } else if (strategy === 'backtrace-ma250') {
            suffix = 'backtrace';
        } else if (strategy === 'high-tight-flag') {
            suffix = 'high-tight';
        } else if (strategy === 'keep-increasing') {
            suffix = 'keep-increasing';
        } else if (strategy === 'long-lower-shadow') {
            suffix = 'long-lower-shadow';
        } else {
            suffix = 'cyb';
        }
        const loadingIndicator = document.getElementById(`loadingIndicator-${suffix}`);
        const errorMessage = document.getElementById(`errorMessage-${suffix}`);
        const resultsTableBody = document.getElementById(`resultsTableBody-${suffix}`);
        const resultsCount = document.getElementById(`resultsCount-${suffix}`);
        const refreshBtn = document.getElementById(`refreshBtn-${strategy}`);
        const searchDate = document.getElementById(`searchDate-${suffix}`);

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
            let url;

            if (strategy === 'cyb-midline') {
                url = `${apiBaseUrl}/api/screening/cyb-midline-strategy?months=4`;
            } else if (strategy === 'parking-apron') {
                url = `${apiBaseUrl}/api/screening/parking-apron-strategy`;
            } else if (strategy === 'backtrace-ma250') {
                url = `${apiBaseUrl}/api/screening/backtrace-ma250-strategy`;
            } else if (strategy === 'high-tight-flag') {
                url = `${apiBaseUrl}/api/screening/high-tight-flag-strategy`;
            } else if (strategy === 'keep-increasing') {
                url = `${apiBaseUrl}/api/screening/keep-increasing-strategy`;
            } else if (strategy === 'long-lower-shadow') {
                url = `${apiBaseUrl}/api/screening/long-lower-shadow-strategy`;
            } else {
                throw new Error('未知的策略类型');
            }

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
                this.renderResults(result.data, result.search_date, strategy);
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
            let colSpan;
            if (strategy === 'cyb-midline') {
                colSpan = 12;
            } else if (strategy === 'parking-apron') {
                colSpan = 7;
            } else if (strategy === 'backtrace-ma250') {
                colSpan = 9;
            } else if (strategy === 'high-tight-flag') {
                colSpan = 7;
            } else if (strategy === 'keep-increasing') {
                colSpan = 8;
            } else if (strategy === 'long-lower-shadow') {
                colSpan = 11;
            } else {
                colSpan = 12;
            }
            if (resultsTableBody) {
                resultsTableBody.innerHTML = `<tr><td colspan="${colSpan}" class="empty-state">加载失败，请稍后重试</td></tr>`;
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
    renderResults(data, searchDate, strategy = 'cyb-midline') {
        let suffix;
        if (strategy === 'cyb-midline') {
            suffix = 'cyb';
        } else if (strategy === 'parking-apron') {
            suffix = 'parking';
        } else if (strategy === 'backtrace-ma250') {
            suffix = 'backtrace';
        } else if (strategy === 'high-tight-flag') {
            suffix = 'high-tight';
        } else if (strategy === 'keep-increasing') {
            suffix = 'keep-increasing';
        } else if (strategy === 'long-lower-shadow') {
            suffix = 'long-lower-shadow';
        } else {
            suffix = 'cyb';
        }
        const resultsTableBody = document.getElementById(`resultsTableBody-${suffix}`);
        const resultsCount = document.getElementById(`resultsCount-${suffix}`);

        if (!resultsTableBody) {
            return;
        }

        if (!data || data.length === 0) {
            let colSpan;
            if (strategy === 'cyb-midline') {
                colSpan = 12;
            } else if (strategy === 'parking-apron') {
                colSpan = 7;
            } else if (strategy === 'backtrace-ma250') {
                colSpan = 9;
            } else if (strategy === 'high-tight-flag') {
                colSpan = 7;
            } else if (strategy === 'keep-increasing') {
                colSpan = 8;
            } else if (strategy === 'long-lower-shadow') {
                colSpan = 11;
            } else {
                colSpan = 12;
            }
            resultsTableBody.innerHTML = `<tr><td colspan="${colSpan}" class="empty-state">未找到符合条件的股票</td></tr>`;
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

            if (strategy === 'cyb-midline') {
                // 创业板中线选股策略表格
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
            } else if (strategy === 'parking-apron') {
                // 停机坪策略表格
                html += `
                    <tr>
                        <td><span class="stock-code">${stock.code}</span></td>
                        <td><span class="stock-name">${stock.name}</span></td>
                        <td>${stock.limit_up_date || '--'}</td>
                        <td>${stock.limit_up_price ? stock.limit_up_price.toFixed(2) : '--'}</td>
                        <td>${stock.current_price ? stock.current_price.toFixed(2) : '--'}</td>
                        <td class="${changeClass}">${changeSymbol}${changePercent.toFixed(2)}%</td>
                        <td>
                            <div class="action-links">
                                <a href="stock_history.html?code=${stock.code}" class="action-link" target="_blank">历史</a>
                                <a href="stock.html?code=${stock.code}&name=${encodeURIComponent(stock.name)}" class="action-link" target="_blank">详情</a>
                            </div>
                        </td>
                    </tr>
                `;
            } else if (strategy === 'backtrace-ma250') {
                // 回踩年线策略表格
                html += `
                    <tr>
                        <td><span class="stock-code">${stock.code}</span></td>
                        <td><span class="stock-name">${stock.name}</span></td>
                        <td>${stock.highest_date || '--'}</td>
                        <td>${stock.highest_price ? stock.highest_price.toFixed(2) : '--'}</td>
                        <td>${stock.lowest_date || '--'}</td>
                        <td>${stock.lowest_price ? stock.lowest_price.toFixed(2) : '--'}</td>
                        <td>${stock.current_price ? stock.current_price.toFixed(2) : '--'}</td>
                        <td class="${changeClass}">${changeSymbol}${changePercent.toFixed(2)}%</td>
                        <td>
                            <div class="action-links">
                                <a href="stock_history.html?code=${stock.code}" class="action-link" target="_blank">历史</a>
                                <a href="stock.html?code=${stock.code}&name=${encodeURIComponent(stock.name)}" class="action-link" target="_blank">详情</a>
                            </div>
                        </td>
                    </tr>
                `;
            } else if (strategy === 'high-tight-flag') {
                // 高而窄的旗形策略表格
                html += `
                    <tr>
                        <td><span class="stock-code">${stock.code}</span></td>
                        <td><span class="stock-name">${stock.name}</span></td>
                        <td>${stock.current_price ? stock.current_price.toFixed(2) : '--'}</td>
                        <td class="${changeClass}">${changeSymbol}${changePercent.toFixed(2)}%</td>
                        <td>${stock.period_low ? stock.period_low.toFixed(2) : '--'}</td>
                        <td>${stock.price_ratio ? stock.price_ratio.toFixed(2) : '--'}</td>
                        <td>
                            <div class="action-links">
                                <a href="stock_history.html?code=${stock.code}" class="action-link" target="_blank">历史</a>
                                <a href="stock.html?code=${stock.code}&name=${encodeURIComponent(stock.name)}" class="action-link" target="_blank">详情</a>
                            </div>
                        </td>
                    </tr>
                `;
            } else if (strategy === 'keep-increasing') {
                // 持续上涨（MA30向上）策略表格
                html += `
                    <tr>
                        <td><span class="stock-code">${stock.code}</span></td>
                        <td><span class="stock-name">${stock.name}</span></td>
                        <td>${stock.current_price ? stock.current_price.toFixed(2) : '--'}</td>
                        <td class="${changeClass}">${changeSymbol}${changePercent.toFixed(2)}%</td>
                        <td>${stock.current_ma30 ? stock.current_ma30.toFixed(2) : '--'}</td>
                        <td>${stock.ma30_before_30 ? stock.ma30_before_30.toFixed(2) : '--'}</td>
                        <td>${stock.ma30_increase_ratio ? (stock.ma30_increase_ratio * 100).toFixed(2) + '%' : '--'}</td>
                        <td>
                            <div class="action-links">
                                <a href="stock_history.html?code=${stock.code}" class="action-link" target="_blank">历史</a>
                                <a href="stock.html?code=${stock.code}&name=${encodeURIComponent(stock.name)}" class="action-link" target="_blank">详情</a>
                            </div>
                        </td>
                    </tr>
                `;
            } else if (strategy === 'long-lower-shadow') {
                // 长下影阳线策略表格
                html += `
                    <tr>
                        <td><span class="stock-code">${stock.code}</span></td>
                        <td><span class="stock-name">${stock.name}</span></td>
                        <td>${stock.pattern_date || '--'}</td>
                        <td>${stock.pattern_close ? stock.pattern_close.toFixed(2) : '--'}</td>
                        <td>${stock.lower_shadow ? stock.lower_shadow.toFixed(2) : '--'}</td>
                        <td>${stock.body_length ? stock.body_length.toFixed(2) : '--'}</td>
                        <td>${stock.shadow_body_ratio ? stock.shadow_body_ratio.toFixed(2) : '--'}</td>
                        <td>${stock.amplitude ? (stock.amplitude * 100).toFixed(2) + '%' : '--'}</td>
                        <td>${stock.current_price ? stock.current_price.toFixed(2) : '--'}</td>
                        <td class="${changeClass}">${changeSymbol}${changePercent.toFixed(2)}%</td>
                        <td>${stock.ma20 ? stock.ma20.toFixed(2) : '--'}</td>
                        <td class="${stock.deviation_from_ma20 < 0 ? 'negative' : (stock.deviation_from_ma20 > 0 ? 'positive' : '')}">${stock.deviation_from_ma20 ? (stock.deviation_from_ma20 * 100).toFixed(2) + '%' : '--'}</td>
                        <td>
                            <div class="action-links">
                                <a href="stock_history.html?code=${stock.code}" class="action-link" target="_blank">历史</a>
                                <a href="stock.html?code=${stock.code}&name=${encodeURIComponent(stock.name)}" class="action-link" target="_blank">详情</a>
                            </div>
                        </td>
                    </tr>
                `;
            }
        });

        resultsTableBody.innerHTML = html;
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    ScreeningPage.init();
});

