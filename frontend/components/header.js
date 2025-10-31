// 动态加载header.html并处理登录状态
async function loadHeader(activePage) {
    console.log('开始加载header，当前页面:', activePage);
    
    const headerContainer = document.createElement('div');
    const resp = await fetch('components/header.html');
    headerContainer.innerHTML = await resp.text();
    document.body.prepend(headerContainer);

    console.log('Header HTML已加载到页面');

    // 高亮当前频道
    if (activePage) {
        const nav = document.getElementById('nav-' + activePage);
        if (nav) {
            nav.classList.add('active');
            console.log('导航高亮设置完成:', activePage);
        }
    }

    // 延迟初始化用户菜单，确保DOM完全加载
    setTimeout(() => {
        console.log('开始初始化用户菜单...');
        initUserMenu();
    }, 100);
    
    // 如果CommonUtils已经加载，让它重新初始化用户显示
    if (window.CommonUtils && window.CommonUtils.auth) {
        setTimeout(() => {
            console.log('CommonUtils已加载，更新用户显示...');
            CommonUtils.auth.updateUserDisplay(CommonUtils.auth.getUserInfo());
        }, 200);
    }
}

// 初始化用户菜单
function initUserMenu() {
    console.log('=== 开始初始化用户菜单 ===');
    
    const userMenu = document.getElementById('userMenu');
    const userStatus = document.getElementById('userStatus');
    const userDropdown = document.getElementById('userDropdown');
    const menuLogout = document.getElementById('menuLogout');
    const menuChangePassword = document.getElementById('menuChangePassword');
    
    console.log('DOM元素检查:');
    console.log('- userMenu:', userMenu);
    console.log('- userStatus:', userStatus);
    console.log('- userDropdown:', userDropdown);
    console.log('- menuLogout:', menuLogout);
    
    if (!userMenu || !userStatus) {
        console.error('❌ 用户菜单元素未找到');
        return;
    }
    
    // 检查登录状态
    const accessToken = localStorage.getItem('access_token');
    const userInfo = localStorage.getItem('userInfo');
    
    console.log('登录状态检查:');
    console.log('- accessToken:', accessToken ? '存在' : '不存在');
    console.log('- userInfo:', userInfo ? '存在' : '不存在');
    
    if (accessToken && userInfo) {
        try {
            const user = JSON.parse(userInfo);
            console.log('用户信息:', user);
            
            userStatus.textContent = user.username || '已登录';
            userMenu.style.cursor = 'pointer';
            
            console.log('✅ 用户状态已设置:', userStatus.textContent);
            
            // 绑定用户菜单点击事件
            userMenu.addEventListener('click', function(e) {
                console.log('🎯 用户菜单被点击');
                e.stopPropagation();
                toggleUserDropdown();
            });
            
            // 点击其他地方关闭菜单
            document.addEventListener('click', function(e) {
                if (!userMenu.contains(e.target)) {
                    console.log('🖱️ 点击外部区域，关闭菜单');
                    closeUserDropdown();
                }
            });
            
            // 绑定“修改密码”事件
            if (menuChangePassword) {
                menuChangePassword.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    openChangePasswordModal();
                });
            }

            // 绑定退出登录事件
            if (menuLogout) {
                menuLogout.addEventListener('click', function(e) {
                    console.log('🚪 退出登录被点击');
                    e.preventDefault();
                    e.stopPropagation();
                    handleLogout();
                });
            }
            
            console.log('✅ 用户菜单初始化成功');
        } catch (error) {
            console.error('❌ 解析用户信息失败:', error);
            setLoggedOutState();
        }
    } else {
        console.log('用户未登录，设置未登录状态');
        setLoggedOutState();
    }
    
    console.log('=== 用户菜单初始化完成 ===');
}

// 切换用户下拉菜单
function toggleUserDropdown() {
    const userMenu = document.getElementById('userMenu');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenu && userDropdown) {
        const isOpen = userMenu.classList.contains('open');
        
        if (isOpen) {
            closeUserDropdown();
        } else {
            openUserDropdown();
        }
    }
}

// 打开用户下拉菜单
function openUserDropdown() {
    const userMenu = document.getElementById('userMenu');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenu && userDropdown) {
        userMenu.classList.add('open');
        
        // 强制设置所有必要的样式，确保菜单可见
        userDropdown.style.cssText = `
            display: flex !important;
            position: absolute !important;
            right: 0 !important;
            top: 120% !important;
            background: #fff !important;
            color: #222 !important;
            min-width: 120px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            border-radius: 6px !important;
            z-index: 9999 !important;
            flex-direction: column !important;
            padding: 6px 0 !important;
            border: 1px solid #e0e0e0 !important;
            visibility: visible !important;
            opacity: 1 !important;
            height: auto !important;
            width: auto !important;
            overflow: visible !important;
        `;
        
        // 确保父元素也有正确的定位
        userMenu.style.position = 'relative';
        userMenu.style.zIndex = '9998';
        
        console.log('用户菜单已打开');
        console.log('用户菜单状态:', userMenu.classList.contains('open'));
        console.log('下拉菜单显示状态:', userDropdown.style.display);
        console.log('下拉菜单z-index:', userDropdown.style.zIndex);
        console.log('下拉菜单位置:', userDropdown.style.position);
        
        // 添加调试信息
        console.log('下拉菜单计算样式:', window.getComputedStyle(userDropdown));
    } else {
        console.error('用户菜单元素未找到:', { userMenu: !!userMenu, userDropdown: !!userDropdown });
    }
}

// 关闭用户下拉菜单
function closeUserDropdown() {
    const userMenu = document.getElementById('userMenu');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenu && userDropdown) {
        userMenu.classList.remove('open');
        
        // 强制隐藏下拉菜单
        userDropdown.style.cssText = `
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        `;
        
        console.log('用户菜单已关闭');
        console.log('用户菜单状态:', userMenu.classList.contains('open'));
        console.log('下拉菜单显示状态:', userDropdown.style.display);
    } else {
        console.error('用户菜单元素未找到:', { userMenu: !!userMenu, userDropdown: !!userDropdown });
    }
}

// 处理退出登录
function handleLogout() {
    console.log('开始退出登录...');
    
    // 使用CommonUtils的logout函数
    if (window.CommonUtils && window.CommonUtils.auth) {
        CommonUtils.auth.logout();
    } else {
        // 备用方案
        console.log('使用备用退出登录方案');
        localStorage.removeItem('access_token');
        localStorage.removeItem('userInfo');
        localStorage.removeItem('token');
        localStorage.removeItem('adminLoggedIn');
        localStorage.removeItem('adminData');
        localStorage.removeItem('admin_token');
        
        // 显示退出成功消息
        showToast('已安全退出', 'success');
        
        // 直接跳转到登录页面
        window.location.href = 'login.html';
    }
}

// 设置未登录状态
function setLoggedOutState() {
    const userStatus = document.getElementById('userStatus');
    const userMenu = document.getElementById('userMenu');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userStatus) {
        userStatus.textContent = '未登录';
    }
    
    if (userMenu) {
        userMenu.style.cursor = 'default';
        userMenu.classList.remove('open');
    }
    
    if (userDropdown) {
        userDropdown.style.display = 'none';
    }
}

// 显示Toast消息
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${type === 'success' ? '#16a34a' : type === 'error' ? '#dc2626' : '#2563eb'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (toast.parentNode) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// 添加动画样式
if (!document.querySelector('#header-animations')) {
    const style = document.createElement('style');
    style.id = 'header-animations';
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}

// 导出函数供外部使用
window.initUserMenu = initUserMenu;
window.toggleUserDropdown = toggleUserDropdown;
window.openUserDropdown = openUserDropdown;
window.closeUserDropdown = closeUserDropdown;
window.handleLogout = handleLogout; 

// ===== 修改密码弹窗逻辑 =====
function getChangePasswordElements() {
    return {
        modal: document.getElementById('changePasswordModal'),
        form: document.getElementById('changePasswordForm'),
        oldInput: document.getElementById('oldPassword'),
        newInput: document.getElementById('newPassword'),
        confirmInput: document.getElementById('confirmPassword'),
        cancelBtn: document.getElementById('cpCancelBtn'),
        submitBtn: document.getElementById('cpSubmitBtn')
    };
}

function openChangePasswordModal() {
    const { modal, cancelBtn, submitBtn } = getChangePasswordElements();
    if (!modal) return;
    modal.style.display = 'flex';
    // 绑定一次性事件
    if (cancelBtn) cancelBtn.onclick = closeChangePasswordModal;
    if (submitBtn) submitBtn.onclick = submitChangePassword;
    // 点击遮罩关闭
    modal.onclick = (e) => {
        if (e.target === modal) closeChangePasswordModal();
    };
}

function closeChangePasswordModal() {
    const { modal, form } = getChangePasswordElements();
    if (!modal) return;
    modal.style.display = 'none';
    if (form) form.reset();
}

function validateChangePassword(oldPwd, newPwd, confirmPwd) {
    if (!oldPwd || !newPwd || !confirmPwd) {
        showToast('请完整填写所有字段', 'error');
        return false;
    }
    if (newPwd.length < 6) {
        showToast('新密码至少需要6位', 'error');
        return false;
    }
    if (newPwd === oldPwd) {
        showToast('新密码不能与旧密码相同', 'error');
        return false;
    }
    if (newPwd !== confirmPwd) {
        showToast('两次输入的新密码不一致', 'error');
        return false;
    }
    return true;
}

async function submitChangePassword() {
    const { oldInput, newInput, confirmInput, submitBtn } = getChangePasswordElements();
    const oldPwd = oldInput ? oldInput.value.trim() : '';
    const newPwd = newInput ? newInput.value.trim() : '';
    const confirmPwd = confirmInput ? confirmInput.value.trim() : '';

    if (!validateChangePassword(oldPwd, newPwd, confirmPwd)) return;

    // 禁用按钮避免重复提交
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = '提交中...';
    }

    try {
        const baseUrl = (typeof API_BASE_URL !== 'undefined' && API_BASE_URL) ? API_BASE_URL : '';
        // 后端实际接口：PUT /api/users/me/password（查询参数 old_password/new_password）
        const url = `${baseUrl}/api/users/me/password?old_password=${encodeURIComponent(oldPwd)}&new_password=${encodeURIComponent(newPwd)}`;

        const reqInit = {
            method: 'PUT'
        };

        // 优先使用带自动401处理的 authFetch
        const resp = (typeof authFetch === 'function')
            ? await authFetch(url, reqInit)
            : await fetch(url, {
                ...reqInit,
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('access_token') || ''}`
                }
            });

        const data = await resp.json().catch(() => ({}));
        if (resp.ok || data.success) {
            showToast('密码修改成功', 'success');
            closeChangePasswordModal();
        } else {
            const msg = data.message || '密码修改失败';
            showToast(msg, 'error');
        }
    } catch (err) {
        console.error('修改密码请求失败:', err);
        showToast('网络错误，请稍后重试', 'error');
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = '确定';
        }
    }
}

// 导出弹窗相关函数（可用于调试）
window.openChangePasswordModal = openChangePasswordModal;
window.closeChangePasswordModal = closeChangePasswordModal;