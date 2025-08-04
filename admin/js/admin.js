// 管理后台主JavaScript文件
// 完全独立于frontend目录

class AdminPanel {
    constructor() {
        this.currentPage = 'dashboard';
        this.adminInfo = null;
        this.init();
    }

    init() {
        this.checkLoginStatus();
        this.bindEvents();
        this.loadDashboardData();
    }

    // 检查登录状态
    checkLoginStatus() {
        const token = localStorage.getItem(ADMIN_CONFIG.AUTH.TOKEN_KEY);
        if (token) {
            this.validateToken(token);
        } else {
            this.showLoginPage();
        }
    }

    // 验证token
    async validateToken(token) {
        try {
            const response = await fetch(`${ADMIN_CONFIG.API.BASE_URL}/auth/verify`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.adminInfo = data.admin;
                this.showAdminPage();
                this.updateUserInfo();
            } else {
                this.showLoginPage();
            }
        } catch (error) {
            console.error('Token验证失败:', error);
            this.showLoginPage();
        }
    }

    // 显示登录页面
    showLoginPage() {
        document.getElementById('loginPage').style.display = 'flex';
        document.getElementById('adminPage').style.display = 'none';
    }

    // 显示管理页面
    showAdminPage() {
        document.getElementById('loginPage').style.display = 'none';
        document.getElementById('adminPage').style.display = 'flex';
        this.loadPageContent('dashboard');
    }

    // 绑定事件
    bindEvents() {
        // 登录表单提交
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // 导航链接点击
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.currentTarget.getAttribute('data-page');
                this.navigateToPage(page);
            });
        });
    }

    // 处理登录
    async handleLogin() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (!username || !password) {
            this.showToast('请输入用户名和密码', 'error');
            return;
        }

        this.showLoading(true);

        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch(`${ADMIN_CONFIG.API.BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem(ADMIN_CONFIG.AUTH.TOKEN_KEY, data.access_token);
                this.adminInfo = data.admin;
                this.showToast(ADMIN_CONFIG.MESSAGES.LOGIN_SUCCESS, 'success');
                this.showAdminPage();
                this.updateUserInfo();
            } else {
                this.showToast(data.message || ADMIN_CONFIG.MESSAGES.LOGIN_FAILED, 'error');
            }
        } catch (error) {
            console.error('登录失败:', error);
            this.showToast(ADMIN_CONFIG.MESSAGES.NETWORK_ERROR, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // 退出登录
    logout() {
        localStorage.removeItem(ADMIN_CONFIG.AUTH.TOKEN_KEY);
        this.showToast(ADMIN_CONFIG.MESSAGES.LOGOUT_SUCCESS, 'info');
        this.showLoginPage();
    }

    // 更新用户信息显示
    updateUserInfo() {
        if (this.adminInfo) {
            document.getElementById('userName').textContent = this.adminInfo.username || '管理员';
            document.getElementById('adminInfo').textContent = this.adminInfo.username || '管理员';
        }
    }

    // 导航到指定页面
    navigateToPage(page) {
        this.currentPage = page;
        
        // 更新导航状态
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-page="${page}"]`).classList.add('active');

        // 更新页面标题
        const pageTitles = {
            'dashboard': '仪表板',
            'users': '用户管理',
            'quotes': '行情数据',
            'datasource': '数据源配置',
            'datacollect': '数据采集',
            'monitoring': '系统监控',
            'models': '预测模型',
            'logs': '系统日志',
            'content': '内容管理',
            'announcements': '公告发布'
        };

        document.getElementById('pageTitle').textContent = pageTitles[page] || '页面';
        document.getElementById('currentPage').textContent = pageTitles[page] || '页面';

        // 加载页面内容
        this.loadPageContent(page);
    }

    // 加载页面内容
    loadPageContent(page) {
        // 隐藏所有页面
        document.querySelectorAll('.page-content').forEach(content => {
            content.classList.remove('active');
        });

        // 显示当前页面
        const currentPageElement = document.getElementById(`${page}Page`);
        if (currentPageElement) {
            currentPageElement.classList.add('active');
        }

        // 根据页面类型加载数据
        switch (page) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'users':
                this.loadUsersData();
                break;
            case 'quotes':
                this.loadQuotesData();
                break;
            default:
                // 其他页面暂时显示占位符
                break;
        }
    }

    // 加载仪表板数据
    async loadDashboardData() {
        try {
            const response = await this.apiRequest('/dashboard/stats');
            if (response.success) {
                this.updateDashboardStats(response.data);
            }
        } catch (error) {
            console.error('加载仪表板数据失败:', error);
        }
    }

    // 更新仪表板统计
    updateDashboardStats(data) {
        document.getElementById('userCount').textContent = data.userCount || 0;
        document.getElementById('stockCount').textContent = data.stockCount || 0;
        document.getElementById('quoteCount').textContent = data.quoteCount || 0;
        document.getElementById('alertCount').textContent = data.alertCount || 0;
    }

    // 加载用户数据
    async loadUsersData() {
        try {
            const response = await this.apiRequest('/users');
            if (response.success) {
                this.renderUsersTable(response.data);
            }
        } catch (error) {
            console.error('加载用户数据失败:', error);
        }
    }

    // 渲染用户表格
    renderUsersTable(users) {
        const tbody = document.getElementById('usersTableBody');
        tbody.innerHTML = '';

        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>${user.email || '-'}</td>
                <td><span class="status-badge ${user.disabled ? 'disabled' : 'active'}">${user.disabled ? '已禁用' : '正常'}</span></td>
                <td>${this.formatDate(user.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="editUser(${user.id})">编辑</button>
                    <button class="btn btn-sm btn-warning" onclick="toggleUserStatus(${user.id})">${user.disabled ? '启用' : '禁用'}</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // 加载行情数据
    async loadQuotesData() {
        try {
            const response = await this.apiRequest('/quotes');
            if (response.success) {
                this.renderQuotesTable(response.data);
            }
        } catch (error) {
            console.error('加载行情数据失败:', error);
        }
    }

    // 渲染行情表格
    renderQuotesTable(quotes) {
        const tbody = document.getElementById('quotesTableBody');
        tbody.innerHTML = '';

        quotes.forEach(quote => {
            const row = document.createElement('tr');
            const changeClass = quote.change_percent >= 0 ? 'positive' : 'negative';
            row.innerHTML = `
                <td>${quote.code}</td>
                <td>${quote.name}</td>
                <td>${quote.current_price}</td>
                <td class="${changeClass}">${quote.change_percent}%</td>
                <td>${this.formatNumber(quote.volume)}</td>
                <td>${this.formatDate(quote.update_time)}</td>
            `;
            tbody.appendChild(row);
        });
    }

    // 通用API请求
    async apiRequest(endpoint, options = {}) {
        const token = localStorage.getItem(ADMIN_CONFIG.AUTH.TOKEN_KEY);
        const url = `${ADMIN_CONFIG.API.BASE_URL}${endpoint}`;

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token ? `Bearer ${token}` : ''
            }
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    this.logout();
                    return;
                }
                throw new Error(data.message || '请求失败');
            }

            return data;
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }

    // 显示加载状态
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    // 显示提示消息
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // 格式化数字
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    // 格式化日期
    formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');

        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    }
}

// 全局函数
function logout() {
    adminPanel.logout();
}

function showAddUserModal() {
    // 显示添加用户模态框
    showModal('添加用户', `
        <form id="addUserForm">
            <div class="form-group">
                <label for="newUsername">用户名</label>
                <input type="text" id="newUsername" required>
            </div>
            <div class="form-group">
                <label for="newEmail">邮箱</label>
                <input type="email" id="newEmail" required>
            </div>
            <div class="form-group">
                <label for="newPassword">密码</label>
                <input type="password" id="newPassword" required>
            </div>
            <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">取消</button>
                <button type="submit" class="btn btn-primary">添加</button>
            </div>
        </form>
    `);
}

function refreshQuotes() {
    adminPanel.loadQuotesData();
    adminPanel.showToast('数据已刷新', 'success');
}

function exportQuotes() {
    adminPanel.showToast('导出功能开发中...', 'info');
}

function showModal(title, content) {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalBody').innerHTML = content;
    document.getElementById('modalOverlay').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modalOverlay').style.display = 'none';
}

// 初始化管理后台
let adminPanel;
document.addEventListener('DOMContentLoaded', () => {
    adminPanel = new AdminPanel();
}); 