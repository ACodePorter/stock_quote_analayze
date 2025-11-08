// 模拟交易个人中心页面脚本
const ProfilePage = {
    state: {
        dashboard: null,
        positions: [],
    },

    async init() {
        try {
            await CommonUtils.auth.init();
            this.bindTabs();
            this.bindActions();
            await this.loadDashboard();
        } catch (error) {
            console.error('个人中心初始化失败:', error);
            CommonUtils.showToast('初始化个人中心失败', 'error');
        }
    },

    bindTabs() {
        document.querySelectorAll('.profile-tab').forEach((tab) => {
            tab.addEventListener('click', (event) => {
                event.preventDefault();
                const target = tab.dataset.tab;
                document.querySelectorAll('.profile-tab').forEach((btn) => {
                    btn.classList.toggle('active', btn.dataset.tab === target);
                });
                document.querySelectorAll('.tab-panel').forEach((panel) => {
                    panel.classList.toggle('active', panel.id === target);
                });
            });
        });
    },

    bindActions() {
        const addPositionBtn = document.querySelector('.add-position-btn');
        if (addPositionBtn) {
            addPositionBtn.addEventListener('click', () => {
                this.showTradeModal();
            });
        }

        // 绑定交易表单事件
        this.bindTradeModal();
    },

    bindTradeModal() {
        const modal = document.getElementById('tradeModal');
        const form = document.getElementById('tradeForm');
        const closeBtn = document.getElementById('tradeModalClose');
        const cancelBtn = document.getElementById('tradeCancelBtn');

        if (!modal || !form) return;

        // 关闭按钮
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hideTradeModal());
        }

        // 取消按钮
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.hideTradeModal());
        }

        // 点击遮罩关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hideTradeModal();
            }
        });

        // 表单提交
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleTradeSubmit();
        });

        // 股票代码输入时自动获取股票名称
        const stockCodeInput = document.getElementById('stockCode');
        if (stockCodeInput) {
            stockCodeInput.addEventListener('blur', () => {
                this.fetchStockName(stockCodeInput.value.trim());
            });
        }
    },

    showTradeModal(code = '', name = '', side = 'buy') {
        const modal = document.getElementById('tradeModal');
        const titleEl = document.getElementById('tradeModalTitle');
        const codeInput = document.getElementById('stockCode');
        const nameInput = document.getElementById('stockName');
        const sideSelect = document.getElementById('tradeSide');
        const quantityInput = document.getElementById('quantity');
        const priceInput = document.getElementById('price');
        const remarkInput = document.getElementById('remark');

        if (!modal) return;

        // 设置标题
        if (titleEl) {
            titleEl.textContent = code ? `${side === 'buy' ? '买入' : '卖出'} ${name || code}` : '新增持仓';
        }

        // 填充表单
        if (codeInput) codeInput.value = code;
        if (nameInput) nameInput.value = name;
        if (sideSelect) sideSelect.value = side;
        if (quantityInput) quantityInput.value = '100';
        if (priceInput) priceInput.value = '';
        if (remarkInput) remarkInput.value = '';

        // 如果已有代码，禁用代码输入
        if (codeInput) {
            codeInput.disabled = !!code;
        }

        // 显示模态框
        modal.style.display = 'flex';
    },

    hideTradeModal() {
        const modal = document.getElementById('tradeModal');
        const form = document.getElementById('tradeForm');
        const codeInput = document.getElementById('stockCode');

        if (modal) {
            modal.style.display = 'none';
        }

        if (form) {
            form.reset();
        }

        // 恢复代码输入框
        if (codeInput) {
            codeInput.disabled = false;
        }
    },

    async fetchStockName(code) {
        if (!code) return;

        const nameInput = document.getElementById('stockName');
        if (!nameInput || nameInput.value.trim()) return; // 如果已有名称则不自动获取

        try {
            // 尝试从本地缓存获取
            const cached = localStorage.getItem('stockBasicInfo');
            if (cached) {
                const stocks = JSON.parse(cached);
                const stock = stocks.find(s => String(s.code) === code);
                if (stock && stock.name) {
                    nameInput.value = stock.name;
                    return;
                }
            }

            // 从API获取
            const response = await fetch(`${API_BASE_URL}/api/stock/list?query=${encodeURIComponent(code)}&limit=1`);
            const data = await response.json();
            if (data.success && data.data && data.data.length > 0) {
                const stock = data.data[0];
                if (stock.code === code && stock.name) {
                    nameInput.value = stock.name;
                }
            }
        } catch (error) {
            console.error('获取股票名称失败:', error);
        }
    },

    async handleTradeSubmit() {
        if (!CommonUtils.checkLoginAndHandleExpiry()) {
            return;
        }

        const codeInput = document.getElementById('stockCode');
        const nameInput = document.getElementById('stockName');
        const sideSelect = document.getElementById('tradeSide');
        const quantityInput = document.getElementById('quantity');
        const priceInput = document.getElementById('price');
        const remarkInput = document.getElementById('remark');
        const submitBtn = document.getElementById('tradeSubmitBtn');

        if (!codeInput || !sideSelect || !quantityInput) {
            CommonUtils.showToast('表单数据不完整', 'error');
            return;
        }

        const stockCode = codeInput.value.trim().toUpperCase();
        const stockName = nameInput.value.trim();
        const side = sideSelect.value;
        const quantity = parseInt(quantityInput.value, 10);
        const priceValue = priceInput.value.trim();
        const remark = remarkInput.value.trim();

        // 验证
        if (!stockCode) {
            CommonUtils.showToast('请输入股票代码', 'error');
            codeInput.focus();
            return;
        }

        if (!quantity || quantity <= 0) {
            CommonUtils.showToast('请输入正确的交易数量', 'error');
            quantityInput.focus();
            return;
        }

        if (quantity % 100 !== 0) {
            CommonUtils.showToast('交易数量必须是100的整数倍', 'error');
            quantityInput.focus();
            return;
        }

        let price = null;
        if (priceValue) {
            const parsed = parseFloat(priceValue);
            if (Number.isNaN(parsed) || parsed <= 0) {
                CommonUtils.showToast('请输入正确的价格', 'error');
                priceInput.focus();
                return;
            }
            price = parsed;
        }

        // 禁用提交按钮
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = '提交中...';
        }

        try {
            const payload = {
                stock_code: stockCode,
                stock_name: stockName || stockCode,
                side,
                quantity,
            };

            if (price !== null) {
                payload.price = price;
            }

            if (remark) {
                payload.remark = remark;
            }

            const label = side === 'sell' ? '卖出' : '买入';
            await this.submitSimTradeOrder(payload, `${label}指令已提交`);
            this.hideTradeModal();
        } catch (error) {
            console.error('交易提交失败:', error);
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = '确认交易';
            }
        }
    },

    async loadDashboard() {
        try {
            const response = await authFetch(`${API_BASE_URL}/api/simtrade/dashboard`);
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || error.message || '加载失败');
            }
            this.state.dashboard = await response.json();
            this.renderDashboard();
        } catch (error) {
            console.error('加载模拟交易数据失败:', error);
            CommonUtils.showToast('加载模拟交易数据失败', 'error');
        }
    },

    renderDashboard() {
        if (!this.state.dashboard) {
            return;
        }

        const { account, positions, recent_orders: orders } = this.state.dashboard;

        this.state.positions = positions || [];
        this.updateAccountSummary(account);
        this.renderPositions(this.state.positions);
        this.renderTransactions(orders || []);
        this.renderRecentTrades(orders || []);
        this.updateProfileStats(this.state.positions, orders || []);
        this.drawPortfolioChart(this.state.positions);
    },

    updateAccountSummary(account) {
        const totalAssets = account?.total_assets || 0;
        const marketValue = account?.total_market_value || 0;
        const cashBalance = account?.cash_balance || 0;
        const totalProfit = account?.total_profit || 0;
        const totalProfitRate = account?.total_profit_rate || 0;

        this.setText('totalAssetsDisplay', this.formatCurrency(totalAssets));
        this.setText('marketValueDisplay', this.formatCurrency(marketValue));
        this.setText('cashBalanceDisplay', this.formatCurrency(cashBalance));

        const marketPercent = totalAssets > 0 ? (marketValue / totalAssets) * 100 : 0;
        const cashPercent = totalAssets > 0 ? (cashBalance / totalAssets) * 100 : 0;
        this.setText('marketValuePercent', this.formatPercent(marketPercent));
        this.setText('cashBalancePercent', this.formatPercent(cashPercent));

        this.setText('todayProfitValue', this.formatCurrency(0));
        this.setText('todayProfitPercent', this.formatPercent(0));
        this.setText('totalProfitValue', this.formatCurrency(totalProfit, true));
        this.setText('totalProfitPercent', this.formatPercent(totalProfitRate));
        this.setText('annualizedReturnValue', this.formatPercent(totalProfitRate));
        this.setText('annualizedReturnHint', '模拟账户');

        this.updateProfitClasses('todayProfitValue', 'todayProfitPercent', 0);
        this.updateProfitClasses('totalProfitValue', 'totalProfitPercent', totalProfit);
    },

    renderPositions(positions) {
        const container = document.getElementById('positionsTableBody');
        if (!container) return;

        if (!positions.length) {
            container.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align:center; color:#6b7280; padding:16px;">
                        暂无持仓，前往 <a href="markets.html" style="color:#2563eb;">行情中心</a> 模拟交易
                    </td>
                </tr>`;
            return;
        }

        container.innerHTML = positions.map((position) => {
            const profit = position.unrealized_profit || 0;
            const profitPercent = position.unrealized_percent || 0;
            const profitClass = this.getProfitClass(profit);
            return `
                <tr>
                    <td>
                        <div class="stock-info">
                            <span class="stock-name">${position.stock_name || position.stock_code}</span>
                            <span class="stock-code">${position.stock_code}</span>
                        </div>
                    </td>
                    <td>${this.formatShares(position.quantity)}</td>
                    <td>${this.formatPrice(position.avg_price)}</td>
                    <td>${this.formatPrice(position.last_price)}</td>
                    <td>${this.formatCurrency(position.market_value)}</td>
                    <td class="${profitClass}">${this.formatCurrency(profit, true)}</td>
                    <td class="${profitClass}">${this.formatPercent(profitPercent)}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="ProfilePage.quickTrade('${position.stock_code}', '${position.stock_name || ''}', 'buy')">买入</button>
                        <button class="btn btn-sm btn-danger" style="margin-left:6px;" onclick="ProfilePage.quickTrade('${position.stock_code}', '${position.stock_name || ''}', 'sell')">卖出</button>
                    </td>
                </tr>`;
        }).join('');
    },

    renderTransactions(orders) {
        const container = document.getElementById('transactionsList');
        if (!container) return;

        if (!orders.length) {
            container.innerHTML = '<div class="transaction-item empty">暂无交易记录</div>';
            return;
        }

        container.innerHTML = orders.map((order) => {
            const typeClass = order.side === 'sell' ? 'sell' : 'buy';
            return `
                <div class="transaction-item">
                    <div class="transaction-date">${this.formatDateTime(order.created_at)}</div>
                    <div class="transaction-stock">
                        <span class="stock-name">${order.stock_name || order.stock_code}</span>
                        <span class="stock-code">${order.stock_code}</span>
                    </div>
                    <div class="transaction-type ${typeClass}">${order.side === 'sell' ? '卖出' : '买入'}</div>
                    <div class="transaction-details">
                        <span class="quantity">${this.formatShares(order.quantity)}</span>
                        <span class="price">${this.formatPrice(order.price)}</span>
                        <span class="amount">${this.formatCurrency(order.amount)}</span>
                    </div>
                    <div class="transaction-status success">${order.status === 'filled' ? '已成交' : order.status}</div>
                </div>`;
        }).join('');
    },

    renderRecentTrades(orders) {
        const container = document.getElementById('recentTradesList');
        if (!container) return;

        if (!orders.length) {
            container.innerHTML = '<div class="trade-item empty">暂无近期交易</div>';
            return;
        }

        container.innerHTML = orders.slice(0, 5).map((order) => {
            const actionClass = order.side === 'sell' ? 'sell' : 'buy';
            return `
                <div class="trade-item">
                    <div class="trade-stock">
                        <span class="stock-name">${order.stock_name || order.stock_code}</span>
                        <span class="stock-code">${order.stock_code}</span>
                    </div>
                    <div class="trade-action ${actionClass}">${order.side === 'sell' ? '卖出' : '买入'}</div>
                    <div class="trade-amount">${this.formatShares(order.quantity)}</div>
                    <div class="trade-time">${this.formatRelativeTime(order.created_at)}</div>
                </div>`;
        }).join('');
    },

    async submitSimTradeOrder(payload, successMessage) {
        try {
            const response = await authFetch(`${API_BASE_URL}/api/simtrade/orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const result = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(result.detail || result.message || '下单失败');
            }

            CommonUtils.showToast(successMessage, 'success');
            this.state.dashboard = result;
            this.renderDashboard();
        } catch (error) {
            console.error('模拟交易下单失败:', error);
            CommonUtils.showToast(error.message || '模拟交易下单失败', 'error');
        }
    },

    async quickTrade(code, name, side) {
        if (!CommonUtils.checkLoginAndHandleExpiry()) {
            return;
        }
        this.showTradeModal(code, name, side);
    },

    async createNewPosition() {
        if (!CommonUtils.checkLoginAndHandleExpiry()) {
            return;
        }
        this.showTradeModal();
    },

    updateProfileStats(positions, orders) {
        const usageDaysEl = document.getElementById('profileUsageDays');
        const watchlistCountEl = document.getElementById('profileWatchlistCount');
        const infoCountEl = document.getElementById('profileInfoCount');

        if (usageDaysEl) {
            const userInfo = CommonUtils.auth.getUserInfo();
            if (userInfo && userInfo.created_at) {
                const start = new Date(userInfo.created_at);
                const diff = Math.max(1, Math.ceil((Date.now() - start.getTime()) / 86400000));
                usageDaysEl.textContent = diff;
            } else {
                usageDaysEl.textContent = '--';
            }
        }

        if (watchlistCountEl) {
            watchlistCountEl.textContent = positions.length;
        }

        if (infoCountEl) {
            infoCountEl.textContent = orders.length;
        }
    },

    drawPortfolioChart(positions) {
        const canvas = document.getElementById('portfolioChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) / 2 - 10;

        ctx.clearRect(0, 0, width, height);

        const data = (positions || [])
            .map((pos) => ({ label: pos.stock_name || pos.stock_code, value: pos.market_value || 0 }))
            .filter((item) => item.value > 0);

        if (!data.length) {
            ctx.fillStyle = '#9ca3af';
            ctx.font = '14px "Microsoft YaHei"';
            ctx.textAlign = 'center';
            ctx.fillText('暂无持仓', centerX, centerY);
            return;
        }

        const total = data.reduce((sum, item) => sum + item.value, 0);
        let currentAngle = -Math.PI / 2;
        const palette = ['#2563eb', '#16a34a', '#f59e0b', '#dc2626', '#6b7280'];

        data.forEach((item, index) => {
            const sliceAngle = (item.value / total) * Math.PI * 2;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.fillStyle = palette[index % palette.length];
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.closePath();
            ctx.fill();
            currentAngle += sliceAngle;
        });

        ctx.beginPath();
        ctx.arc(centerX, centerY, radius * 0.55, 0, Math.PI * 2);
        ctx.fillStyle = '#fff';
        ctx.fill();

        ctx.fillStyle = '#1f2937';
        ctx.font = 'bold 14px "Microsoft YaHei"';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('持仓分布', centerX, centerY);
    },

    updateProfitClasses(valueId, percentId, profit) {
        const cls = this.getProfitClass(profit);
        const valueEl = document.getElementById(valueId);
        const percentEl = document.getElementById(percentId);
        if (valueEl) valueEl.className = `performance-value ${cls}`;
        if (percentEl) percentEl.className = `performance-percent ${cls}`;
    },

    getProfitClass(value) {
        if (value > 0) return 'positive';
        if (value < 0) return 'negative';
        return 'neutral';
    },

    setText(id, text) {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = text;
        }
    },

    formatCurrency(value, withSign = false) {
        const num = Number(value) || 0;
        const sign = withSign ? (num > 0 ? '+' : '') : '';
        return `${sign}¥${num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    },

    formatPercent(value) {
        const num = Number(value) || 0;
        const sign = num > 0 ? '+' : '';
        return `${sign}${num.toFixed(2)}%`;
    },

    formatPrice(value) {
        const num = Number(value);
        if (Number.isNaN(num)) return '--';
        return `¥${num.toFixed(2)}`;
    },

    formatShares(value) {
        const num = Number(value) || 0;
        return `${num.toLocaleString()}股`;
    },

    formatDateTime(value) {
        if (!value) return '--';
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return value;
        return date.toLocaleString('zh-CN', { hour12: false });
    },

    formatRelativeTime(value) {
        if (!value) return '--';
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return value;

        const diff = Date.now() - date.getTime();
        if (diff < 60000) return '刚刚';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`;
        return `${Math.floor(diff / 86400000)} 天前`;
    },
};

document.addEventListener('DOMContentLoaded', () => {
    ProfilePage.init();
});

// 导出到全局作用域，以便 onclick 事件可以访问
window.ProfilePage = ProfilePage; 