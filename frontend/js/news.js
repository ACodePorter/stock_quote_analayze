/**
 * 资讯频道JavaScript
 */

const NewsChannel = {
    currentPage: 1,
    pageSize: 20,
    currentCategory: null,
    isLoading: false,
    hasMore: true,
    searchKeyword: '',

    // 初始化
    async init() {
        console.log('🚀 初始化资讯频道...');
        
        // 加载头部导航
        await this.loadHeader();
        
        // 加载分类
        await this.loadCategories();
        
        // 加载头条新闻
        await this.loadFeaturedNews();
        
        // 加载资讯列表
        await this.loadNewsList();
        
        // 加载热门资讯
        await this.loadHotNews();
        
        // 绑定搜索事件
        this.bindSearchEvents();
        
        // 初始化无限滚动
        this.initInfiniteScroll();
        
        console.log('✅ 资讯频道初始化完成');
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
                        const nav = document.getElementById('nav-news');
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

    // 加载分类
    async loadCategories() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/news/categories`);
            const data = await response.json();
            
            if (data.success) {
                this.renderCategories(data.data);
            } else {
                console.error('获取分类失败:', data.message);
            }
        } catch (error) {
            console.error('加载分类失败:', error);
            // 使用默认分类
            this.renderDefaultCategories();
        }
    },

    // 渲染分类
    renderCategories(categories) {
        const container = document.getElementById('category-tabs');
        if (!container) return;
        
        container.innerHTML = categories.map(category => `
            <button class="category-tab ${category.id === 1 ? 'active' : ''}" 
                    onclick="NewsChannel.filterByCategory(${category.id === 1 ? null : category.id})"
                    data-category-id="${category.id}">
                ${category.name}
            </button>
        `).join('');
    },

    // 渲染默认分类
    renderDefaultCategories() {
        const container = document.getElementById('category-tabs');
        if (!container) return;
        
        const defaultCategories = [
            { id: 1, name: '全部' },
            { id: 2, name: '市场动态' },
            { id: 3, name: '政策解读' },
            { id: 4, name: '公司资讯' },
            { id: 5, name: '国际财经' },
            { id: 6, name: '分析研判' }
        ];
        
        this.renderCategories(defaultCategories);
    },

    // 加载头条新闻
    async loadFeaturedNews() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/news/featured`);
            const data = await response.json();
            
            if (data.success) {
                this.renderFeaturedNews(data.data);
            } else {
                console.error('获取头条新闻失败:', data.message);
                this.renderDefaultFeaturedNews();
            }
        } catch (error) {
            console.error('加载头条新闻失败:', error);
            this.renderDefaultFeaturedNews();
        }
    },

    // 渲染头条新闻
    renderFeaturedNews(news) {
        const featuredCard = document.getElementById('featured-card');
        if (!featuredCard) return;
        
        document.getElementById('featured-title').textContent = news.title;
        document.getElementById('featured-summary').textContent = news.summary;
        document.getElementById('featured-source').textContent = news.source;
        document.getElementById('featured-time').textContent = this.formatTime(news.publish_time);
        document.getElementById('featured-reads').textContent = `${this.formatNumber(news.read_count)}阅读`;
        
        // 添加点击事件
        featuredCard.onclick = () => this.showNewsDetail(news.id);
    },

    // 渲染默认头条新闻
    renderDefaultFeaturedNews() {
        const featuredCard = document.getElementById('featured-card');
        if (!featuredCard) return;
        
        document.getElementById('featured-title').textContent = 'A股三大指数集体收涨 科技板块领涨';
        document.getElementById('featured-summary').textContent = '今日A股市场表现强劲，上证指数上涨0.8%，深证成指上涨1.2%，创业板指上涨1.5%。科技股、新能源汽车、AI概念等板块表现突出...';
        document.getElementById('featured-source').textContent = '财经日报';
        document.getElementById('featured-time').textContent = '2小时前';
        document.getElementById('featured-reads').textContent = '1.2万阅读';
    },

    // 加载资讯列表
    async loadNewsList() {
        if (this.isLoading) return;
        this.isLoading = true;

        try {
            // 如果是第一页，显示加载状态
            if (this.currentPage === 1) {
                this.showLoading('news-container', '正在加载资讯...');
            }

            const params = new URLSearchParams({
                page: this.currentPage,
                page_size: this.pageSize
            });
            
            if (this.currentCategory) {
                params.append('category_id', this.currentCategory);
            }

            const response = await fetch(`${API_BASE_URL}/api/news/list?${params}`);
            const data = await response.json();
            
            if (data.success) {
                if (this.currentPage === 1) {
                    this.renderNewsList(data.data.items);
                } else {
                    this.appendNewsList(data.data.items);
                }
                this.hasMore = data.data.items.length === this.pageSize;
                this.updateLoadMoreButton();
            } else {
                console.error('获取资讯列表失败:', data.message);
                this.showError('获取资讯列表失败: ' + data.message);
            }
        } catch (error) {
            console.error('加载资讯列表失败:', error);
            this.showError('网络请求失败，请检查网络连接');
        } finally {
            this.isLoading = false;
            this.hideLoading('news-container');
        }
    },

    // 渲染资讯列表
    renderNewsList(newsList) {
        const container = document.getElementById('news-container');
        if (!container) return;
        
        if (this.currentPage === 1) {
            container.innerHTML = '';
        }

        if (newsList.length === 0 && this.currentPage === 1) {
            this.showEmptyState();
            return;
        }

        newsList.forEach(news => {
            const newsItem = document.createElement('div');
            newsItem.className = 'news-item';
            newsItem.innerHTML = `
                <div class="news-icon">${this.getNewsIcon(news.category_id)}</div>
                <div class="news-content">
                    <h3 class="news-title">${news.title}</h3>
                    <p class="news-summary">${news.summary}</p>
                    <div class="news-meta">
                        <span class="news-source">${news.source}</span>
                        <span class="news-time">${this.formatTime(news.publish_time)}</span>
                        <span class="news-category">${this.getCategoryName(news.category_id)}</span>
                        <span class="news-reads">${this.formatNumber(news.read_count)}阅读</span>
                        ${news.is_hot ? '<span class="hot-tag">热点</span>' : ''}
                    </div>
                </div>
            `;
            
            newsItem.onclick = () => this.showNewsDetail(news.id);
            container.appendChild(newsItem);
        });
    },

    // 追加资讯列表（用于分页加载）
    appendNewsList(newsList) {
        const container = document.getElementById('news-container');
        if (!container) return;

        newsList.forEach(news => {
            const newsItem = document.createElement('div');
            newsItem.className = 'news-item';
            newsItem.innerHTML = `
                <div class="news-icon">${this.getNewsIcon(news.category_id)}</div>
                <div class="news-content">
                    <h3 class="news-title">${news.title}</h3>
                    <p class="news-summary">${news.summary}</p>
                    <div class="news-meta">
                        <span class="news-source">${news.source}</span>
                        <span class="news-time">${this.formatTime(news.publish_time)}</span>
                        <span class="news-category">${this.getCategoryName(news.category_id)}</span>
                        <span class="news-reads">${this.formatNumber(news.read_count)}阅读</span>
                        ${news.is_hot ? '<span class="hot-tag">热点</span>' : ''}
                    </div>
                </div>
            `;
            
            newsItem.onclick = () => this.showNewsDetail(news.id);
            container.appendChild(newsItem);
        });
    },

    // 加载热门资讯
    async loadHotNews() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/news/hot?limit=5`);
            const data = await response.json();
            
            if (data.success) {
                this.renderHotNews(data.data);
            } else {
                console.error('获取热门资讯失败:', data.message);
                this.renderDefaultHotNews();
            }
        } catch (error) {
            console.error('加载热门资讯失败:', error);
            this.renderDefaultHotNews();
        }
    },

    // 渲染热门资讯
    renderHotNews(hotNews) {
        const container = document.getElementById('hot-news-list');
        if (!container) return;
        
        if (hotNews.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>暂无热门资讯</p></div>';
            return;
        }
        
        container.innerHTML = hotNews.map((news, index) => `
            <div class="hot-news-item" onclick="NewsChannel.showNewsDetail(${news.id})">
                <span class="hot-rank">${index + 1}</span>
                <div class="hot-content">
                    <h4>${news.title}</h4>
                    <div class="hot-meta">
                        <span>${this.formatNumber(news.read_count)}阅读</span>
                    </div>
                </div>
            </div>
        `).join('');
    },

    // 渲染默认热门资讯
    renderDefaultHotNews() {
        const container = document.getElementById('hot-news-list');
        if (!container) return;
        
        const defaultHotNews = [
            { id: 1, title: 'A股迎来新一轮上涨行情', read_count: 105000 },
            { id: 2, title: '科技股集体爆发 AI概念涨停潮', read_count: 82000 },
            { id: 3, title: '央行降准释放流动性1万亿', read_count: 78000 },
            { id: 4, title: '新能源车销量数据超预期', read_count: 65000 },
            { id: 5, title: '银行股集体上涨', read_count: 58000 }
        ];
        
        this.renderHotNews(defaultHotNews);
    },

    // 按分类过滤
    filterByCategory(categoryId) {
        this.currentCategory = categoryId;
        this.currentPage = 1;
        this.hasMore = true;
        
        // 更新分类标签状态
        document.querySelectorAll('.category-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        const activeTab = document.querySelector(`[data-category-id="${categoryId || 1}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
        
        // 重新加载列表
        this.loadNewsList();
    },

    // 搜索资讯
    async searchNews() {
        const searchInput = document.getElementById('search-input');
        if (!searchInput) return;
        
        const keyword = searchInput.value.trim();
        if (!keyword) {
            CommonUtils.showToast('请输入搜索关键词', 'warning');
            return;
        }
        
        this.searchKeyword = keyword;
        this.currentPage = 1;
        this.hasMore = true;
        
        try {
            const params = new URLSearchParams({
                keyword: keyword,
                page: this.currentPage,
                page_size: this.pageSize
            });
            
            if (this.currentCategory) {
                params.append('category_id', this.currentCategory);
            }

            const response = await fetch(`${API_BASE_URL}/api/news/search?${params}`);
            const data = await response.json();
            
            if (data.success) {
                this.showSearchResults(data.data);
            } else {
                CommonUtils.showToast('搜索失败: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('搜索失败:', error);
            CommonUtils.showToast('搜索请求失败', 'error');
        }
    },

    // 显示搜索结果
    showSearchResults(data) {
        const modal = document.getElementById('search-modal');
        const resultsContainer = document.getElementById('search-results');
        
        if (!modal || !resultsContainer) return;
        
        if (data.items.length === 0) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🔍</div>
                    <h3>未找到相关资讯</h3>
                    <p>请尝试其他关键词</p>
                </div>
            `;
        } else {
            resultsContainer.innerHTML = data.items.map(news => `
                <div class="search-result-item" onclick="NewsChannel.showNewsDetail(${news.id}); NewsChannel.closeSearchModal();">
                    <div class="search-result-title">${news.title}</div>
                    <div class="search-result-summary">${news.summary}</div>
                    <div class="news-meta">
                        <span>${news.source}</span>
                        <span>${this.formatTime(news.publish_time)}</span>
                        <span>${this.formatNumber(news.read_count)}阅读</span>
                    </div>
                </div>
            `).join('');
        }
        
        modal.style.display = 'block';
    },

    // 关闭搜索模态框
    closeSearchModal() {
        const modal = document.getElementById('search-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    },

    // 显示加载状态
    showLoading(containerId, message = '加载中...') {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <p class="loading-text">${message}</p>
            </div>
        `;
    },

    // 隐藏加载状态
    hideLoading(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const loadingState = container.querySelector('.loading-state');
        if (loadingState) {
            loadingState.remove();
        }
    },

    // 显示错误状态
    showError(message) {
        const container = document.getElementById('news-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="error-state">
                <div class="error-icon">⚠️</div>
                <p class="error-text">${message}</p>
                <button class="retry-btn" onclick="NewsChannel.loadNewsList()">重试</button>
            </div>
        `;
    },

    // 更新加载更多按钮
    updateLoadMoreButton() {
        const loadMoreDiv = document.getElementById('load-more');
        if (!loadMoreDiv) return;
        
        if (this.hasMore) {
            loadMoreDiv.style.display = 'block';
            const button = loadMoreDiv.querySelector('.load-more-btn');
            if (button) {
                button.disabled = this.isLoading;
                button.textContent = this.isLoading ? '加载中...' : '加载更多';
            }
        } else {
            loadMoreDiv.style.display = 'none';
        }
    },

    // 显示资讯详情
    async showNewsDetail(newsId) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/news/detail/${newsId}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderNewsDetail(data.data);
                document.getElementById('news-modal').style.display = 'block';
            } else {
                CommonUtils.showToast('获取资讯详情失败: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('加载资讯详情失败:', error);
            CommonUtils.showToast('网络请求失败', 'error');
        }
    },

    // 渲染资讯详情
    renderNewsDetail(news) {
        const modal = document.getElementById('news-modal');
        if (!modal) return;
        
        document.getElementById('modal-title').textContent = news.title;
        document.getElementById('modal-body').innerHTML = `
            <div class="news-detail-meta">
                <span class="detail-source">${news.source}</span>
                <span class="detail-time">${this.formatTime(news.publish_time)}</span>
                <span class="detail-reads">${this.formatNumber(news.read_count)}阅读</span>
            </div>
            <div class="news-detail-content">
                ${this.formatNewsContent(news.content)}
            </div>
            ${news.url ? `<div class="news-detail-link"><a href="${news.url}" target="_blank">查看原文</a></div>` : ''}
        `;
    },

    // 关闭模态框
    closeModal() {
        const modal = document.getElementById('news-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    },

    // 绑定搜索事件
    bindSearchEvents() {
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            // 回车搜索
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.searchNews();
                }
            });
            
            // 清空搜索
            searchInput.addEventListener('input', (e) => {
                if (e.target.value.trim() === '') {
                    this.searchKeyword = '';
                    this.currentPage = 1;
                    this.hasMore = true;
                    this.loadNewsList();
                }
            });
        }
        
        // 点击模态框外部关闭
        document.addEventListener('click', (e) => {
            const newsModal = document.getElementById('news-modal');
            const searchModal = document.getElementById('search-modal');
            
            if (e.target === newsModal) {
                this.closeModal();
            }
            if (e.target === searchModal) {
                this.closeSearchModal();
            }
        });
    },

    // 显示空状态
    showEmptyState() {
        const container = document.getElementById('news-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📰</div>
                <h3>暂无资讯</h3>
                <p>当前分类下没有找到相关资讯</p>
            </div>
        `;
    },

    // 显示错误信息
    showError(message) {
        const container = document.getElementById('news-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>加载失败</h3>
                <p>${message}</p>
                <button onclick="NewsChannel.loadNewsList()" class="load-more-btn">重试</button>
            </div>
        `;
    },

    // 格式化时间
    formatTime(timeStr) {
        if (!timeStr) return '未知时间';
        
        try {
            const time = new Date(timeStr);
            const now = new Date();
            const diff = now - time;
            
            if (diff < 60000) return '刚刚';
            if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
            if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
            if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`;
            
            return time.toLocaleDateString('zh-CN');
        } catch (error) {
            return timeStr;
        }
    },

    // 格式化数字
    formatNumber(num) {
        if (!num) return '0';
        if (num < 1000) return num.toString();
        if (num < 10000) return (num / 1000).toFixed(1) + 'k';
        if (num < 100000000) return (num / 10000).toFixed(1) + '万';
        return (num / 100000000).toFixed(1) + '亿';
    },

    // 获取分类名称
    getCategoryName(categoryId) {
        const categories = {
            1: '全部',
            2: '市场动态',
            3: '政策解读',
            4: '公司资讯',
            5: '国际财经',
            6: '分析研判'
        };
        return categories[categoryId] || '未知';
    },

    // 获取新闻图标
    getNewsIcon(categoryId) {
        const icons = {
            1: '📰',
            2: '📈',
            3: '📋',
            4: '🏢',
            5: '🌍',
            6: '📊'
        };
        return icons[categoryId] || '📰';
    },

    // 格式化新闻内容
    formatNewsContent(content) {
        if (!content) return '';
        
        // 简单的HTML转义
        return content
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>')
            .replace(/\s{2,}/g, '&nbsp;&nbsp;');
    },
    loadMore() {
        if (this.hasMore && !this.isLoading) {
            this.currentPage++;
            this.loadNewsList();
        }
    },

    // 初始化无限滚动
    initInfiniteScroll() {
        // 监听滚动事件
        window.addEventListener('scroll', () => {
            if (this.isLoading || !this.hasMore) return;
            
            // 检查是否滚动到底部
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const windowHeight = window.innerHeight;
            const documentHeight = document.documentElement.scrollHeight;
            
            // 当滚动到距离底部100px时开始加载
            if (scrollTop + windowHeight >= documentHeight - 100) {
                this.loadMore();
            }
        });
    },

    // 重置分页状态
    resetPagination() {
        this.currentPage = 1;
        this.hasMore = true;
        this.isLoading = false;
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('📰 资讯频道页面加载完成');
    NewsChannel.init();
});

// 导出到全局作用域
window.NewsChannel = NewsChannel;