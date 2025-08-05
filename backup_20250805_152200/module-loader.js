/**
 * 模块加载器
 * 负责动态加载各个功能模块的HTML内容
 */

class ModuleLoader {
    constructor() {
        this.cache = new Map(); // 缓存已加载的模块
        this.currentModule = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadDefaultModule();
    }

    bindEvents() {
        // 监听导航链接点击事件
        document.addEventListener('click', (e) => {
            if (e.target.closest('.nav-link')) {
                e.preventDefault();
                const link = e.target.closest('.nav-link');
                const page = link.getAttribute('data-page');
                this.loadModule(page);
            }
        });

        // 监听浏览器前进后退
        window.addEventListener('popstate', (e) => {
            const page = e.state?.page || 'dashboard';
            this.loadModule(page, false);
        });
    }

    async loadModule(pageName, updateHistory = true) {
        try {
            // 显示加载状态
            this.showLoading();

            // 更新导航状态
            this.updateNavigation(pageName);

            // 检查缓存
            if (this.cache.has(pageName)) {
                this.renderModule(pageName, this.cache.get(pageName));
                this.hideLoading();
                return;
            }

            // 加载模块内容
            const content = await this.fetchModuleContent(pageName);
            
            // 缓存内容
            this.cache.set(pageName, content);
            
            // 渲染模块
            this.renderModule(pageName, content);

            // 更新浏览器历史
            if (updateHistory) {
                this.updateHistory(pageName);
            }

        } catch (error) {
            console.error('加载模块失败:', error);
            this.showError(`加载 ${pageName} 模块失败: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    async fetchModuleContent(pageName) {
        const moduleFile = `${pageName}.html`;
        const response = await fetch(moduleFile);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.text();
    }

    renderModule(pageName, content) {
        const contentBody = document.getElementById('contentBody');
        contentBody.innerHTML = content;
        
        // 更新页面标题
        this.updatePageTitle(pageName);
        
        this.currentModule = pageName;
        
        // 确保DOM更新完成后再初始化模块脚本
        // 将延迟从50ms增加到300ms，给浏览器更多时间解析innerHTML
        setTimeout(() => {
            this.initModuleScripts(pageName);
        }, 300); // 增加延迟时间
    }

    updateNavigation(pageName) {
        // 移除所有活动状态
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // 添加当前页面的活动状态
        const currentLink = document.querySelector(`[data-page="${pageName}"]`);
        if (currentLink) {
            currentLink.classList.add('active');
        }
    }

    updatePageTitle(pageName) {
        const pageTitle = document.getElementById('pageTitle');
        const currentPage = document.getElementById('currentPage');
        
        const titles = {
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

        const title = titles[pageName] || pageName;
        pageTitle.textContent = title;
        currentPage.textContent = title;
    }

    updateHistory(pageName) {
        const url = `#${pageName}`;
        const state = { page: pageName };
        window.history.pushState(state, '', url);
    }

    initModuleScripts(pageName) {
        // 根据模块名称初始化特定的JavaScript功能
        switch (pageName) {
            case 'dashboard':
                this.initDashboard();
                break;
            case 'users':
                this.initUsers();
                break;
            case 'quotes':
                this.initQuotes();
                break;
            case 'logs':
                this.initLogs();
                break;
            case 'datasource':
                this.initDataSource();
                break;
            case 'datacollect':
                this.initDataCollect();
                break;
            case 'monitoring':
                this.initMonitoring();
                break;
            case 'models':
                this.initModels();
                break;
            case 'content':
                this.initContent();
                break;
            case 'announcements':
                this.initAnnouncements();
                break;
        }
    }

    // 各模块初始化方法
    initDashboard() {
        // 仪表板初始化
        console.log('初始化仪表板模块');
        // 这里可以添加仪表板特定的初始化代码
    }

    initUsers() {
        // 用户管理初始化
        console.log('初始化用户管理模块');
        // 这里可以添加用户管理特定的初始化代码
    }

    initQuotes() {
        // 行情数据初始化
        console.log('初始化行情数据模块');
        // 这里可以添加行情数据特定的初始化代码
    }

    initLogs() {
        // 系统日志初始化
        console.log('初始化系统日志模块');
        
        // 等待DOM元素加载完成后初始化日志管理器
        setTimeout(() => {
            // 调用全局初始化函数
            if (window.initLogsManager) {
                console.log('调用全局initLogsManager函数');
                window.initLogsManager();
            } else {
                console.log('initLogsManager函数不存在，尝试直接初始化');
                // 检查logs.js是否已经加载并创建了LogsManager实例
                if (window.logsManager) {
                    console.log('使用现有的LogsManager实例');
                    window.logsManager.refresh();
                } else {
                    console.log('创建新的LogsManager实例');
                    // 如果logs.js还没有初始化，手动创建LogsManager实例
                    if (typeof LogsManager !== 'undefined') {
                        window.logsManager = new LogsManager();
                    } else {
                        console.error('LogsManager类未定义，logs.js可能未正确加载');
                    }
                }
            }
        }, 200); // 增加延迟时间，确保DOM完全加载
    }

    initDataSource() {
        // 数据源配置初始化
        console.log('初始化数据源配置模块');
        // 这里可以添加数据源配置特定的初始化代码
    }

    initDataCollect() {
        // 数据采集初始化
        console.log('初始化数据采集模块');
        // 这里可以添加数据采集特定的初始化代码
    }

    initMonitoring() {
        // 系统监控初始化
        console.log('初始化系统监控模块');
        // 这里可以添加系统监控特定的初始化代码
    }

    initModels() {
        // 预测模型初始化
        console.log('初始化预测模型模块');
        // 这里可以添加预测模型特定的初始化代码
    }

    initContent() {
        // 内容管理初始化
        console.log('初始化内容管理模块');
        // 这里可以添加内容管理特定的初始化代码
    }

    initAnnouncements() {
        // 公告发布初始化
        console.log('初始化公告发布模块');
        // 这里可以添加公告发布特定的初始化代码
    }

    loadDefaultModule() {
        // 加载默认模块（仪表板）
        const hash = window.location.hash.slice(1) || 'dashboard';
        this.loadModule(hash, false);
    }

    showLoading() {
        const loadingContent = document.getElementById('loadingContent');
        if (loadingContent) {
            loadingContent.style.display = 'flex';
        }
    }

    hideLoading() {
        const loadingContent = document.getElementById('loadingContent');
        if (loadingContent) {
            loadingContent.style.display = 'none';
        }
    }

    showError(message) {
        const contentBody = document.getElementById('contentBody');
        contentBody.innerHTML = `
            <div class="error-content">
                <div class="error-icon">❌</div>
                <h3>加载失败</h3>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="moduleLoader.loadDefaultModule()">返回首页</button>
            </div>
        `;
    }

    // 清除缓存
    clearCache() {
        this.cache.clear();
    }

    // 清除特定模块缓存
    clearModuleCache(pageName) {
        this.cache.delete(pageName);
    }

    // 重新加载当前模块
    reloadCurrentModule() {
        if (this.currentModule) {
            this.clearModuleCache(this.currentModule);
            this.loadModule(this.currentModule);
        }
    }
}

// 创建全局模块加载器实例
const moduleLoader = new ModuleLoader();

// 导出到全局作用域
window.moduleLoader = moduleLoader; 