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

    async quickTrade(code, name, side) {
        const label = side === 'sell' ? '卖出' : '买入';
        const quantityInput = prompt(`请输入${label}股数`, '100');
        if (!quantityInput) return;

        const quantity = parseInt(quantityInput, 10);
        if (!quantity || quantity <= 0) {
            CommonUtils.showToast('请输入正确的股数', 'error');
            return;
        }

        const priceInput = prompt('请输入成交价格，留空则使用最新价', '');
        let price = null;
        if (priceInput && priceInput.trim()) {
            const parsed = parseFloat(priceInput.trim());
            if (Number.isNaN(parsed) || parsed <= 0) {
                CommonUtils.showToast('请输入正确的价格', 'error');
                return;
            }
            price = parsed;
        }

        try {
            const payload = {
                stock_code: code,
                stock_name: name,
                side,
                quantity,
            };
            if (price !== null) {
                payload.price = price;
            }

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

            CommonUtils.showToast(`${label}指令已提交`, 'success');
            this.state.dashboard = result;
            this.renderDashboard();
        } catch (error) {
            console.error('模拟交易下单失败:', error);
            CommonUtils.showToast(error.message || '模拟交易下单失败', 'error');
        }
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