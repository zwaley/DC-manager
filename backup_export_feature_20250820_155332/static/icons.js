/**
 * 图标管理系统 - 动力资源管理系统
 * 提供SVG图标的便捷使用方法
 */

// 图标映射表
const ICON_MAP = {
    // 基础图标
    'user': 'icon-user',
    'server': 'icon-server',
    'plus': 'icon-plus',
    'edit': 'icon-edit',
    'trash': 'icon-trash',
    'delete': 'icon-trash',
    'search': 'icon-search',
    'filter': 'icon-filter',
    'download': 'icon-download',
    'upload': 'icon-upload',
    'settings': 'icon-settings',
    'lifecycle': 'icon-lifecycle',
    'chart': 'icon-bar-chart',
    'stats': 'icon-bar-chart',
    'refresh': 'icon-refresh',
    'view': 'icon-eye',
    'calendar': 'icon-calendar',
    'file': 'icon-file',
    'home': 'icon-home',
    
    // 状态图标
    'success': 'icon-check',
    'check': 'icon-check',
    'error': 'icon-x',
    'close': 'icon-x',
    'warning': 'icon-alert',
    'alert': 'icon-alert',
    'info': 'icon-info'
};

// 生命周期状态映射
const LIFECYCLE_STATUS_MAP = {
    '新设备': { icon: 'plus', class: 'status-new' },
    '运行中': { icon: 'check', class: 'status-active' },
    '维护中': { icon: 'settings', class: 'status-maintenance' },
    '已退役': { icon: 'alert', class: 'status-retired' },
    '已淘汰': { icon: 'close', class: 'status-obsolete' }
};

/**
 * 创建SVG图标元素
 * @param {string} iconName - 图标名称
 * @param {string} size - 图标大小 (sm, md, lg, xl)
 * @param {string} className - 额外的CSS类名
 * @returns {string} SVG图标的HTML字符串
 */
function createIcon(iconName, size = '', className = '') {
    const iconId = ICON_MAP[iconName] || iconName;
    const sizeClass = size ? `icon-${size}` : '';
    const classes = ['icon', sizeClass, className].filter(Boolean).join(' ');
    
    return `<svg class="${classes}">
        <use href="/static/icons.svg#${iconId}"></use>
    </svg>`;
}

/**
 * 创建带图标的按钮HTML
 * @param {string} iconName - 图标名称
 * @param {string} text - 按钮文字
 * @param {string} btnClass - 按钮CSS类名
 * @param {string} iconSize - 图标大小
 * @returns {string} 按钮HTML字符串
 */
function createIconButton(iconName, text = '', btnClass = 'btn-primary', iconSize = 'sm') {
    const icon = createIcon(iconName, iconSize);
    const textPart = text ? ` ${text}` : '';
    
    return `<button class="btn ${btnClass}">
        ${icon}${textPart}
    </button>`;
}

/**
 * 创建生命周期状态标签
 * @param {string} status - 生命周期状态
 * @returns {string} 状态标签HTML字符串
 */
function createLifecycleStatus(status) {
    const statusConfig = LIFECYCLE_STATUS_MAP[status];
    if (!statusConfig) {
        return `<span class="status-icon">${status}</span>`;
    }
    
    const icon = createIcon(statusConfig.icon, 'sm');
    return `<span class="status-icon ${statusConfig.class}">
        ${icon}
        ${status}
    </span>`;
}

/**
 * 创建生命周期状态徽章
 * @param {string} status - 状态类型
 * @param {string} text - 显示文本
 * @param {boolean} showIcon - 是否显示图标
 * @returns {HTMLElement} 状态徽章元素
 */
function createLifecycleBadge(status, text, showIcon = true) {
    const statusMap = {
        'normal': { icon: 'check', text: '正常' },
        'warning': { icon: 'alert', text: '预警' },
        'expired': { icon: 'close', text: '过期' },
        'unknown': { icon: 'info', text: '未知' }
    };
    
    const config = statusMap[status] || statusMap['unknown'];
    const displayText = text || config.text;
    
    const badge = document.createElement('span');
    badge.className = `lifecycle-badge ${status}`;
    
    if (showIcon) {
        const iconHtml = createIcon(config.icon, 'sm');
        badge.innerHTML = iconHtml;
    }
    
    const textSpan = document.createElement('span');
    textSpan.textContent = displayText;
    badge.appendChild(textSpan);
    
    return badge;
}

/**
 * 创建生命周期状态指示器
 * @param {string} status - 状态类型
 * @returns {HTMLElement} 状态指示器元素
 */
function createLifecycleIndicator(status) {
    const indicator = document.createElement('span');
    indicator.className = `lifecycle-indicator ${status}`;
    indicator.title = getLifecycleStatusText(status);
    return indicator;
}

/**
 * 创建生命周期进度条
 * @param {string} status - 状态类型
 * @param {number} percentage - 进度百分比
 * @returns {HTMLElement} 进度条元素
 */
function createLifecycleProgress(status, percentage) {
    const container = document.createElement('div');
    container.className = 'lifecycle-progress';
    
    const bar = document.createElement('div');
    bar.className = `lifecycle-progress-bar ${status}`;
    bar.style.width = `${Math.min(100, Math.max(0, percentage))}%`;
    
    container.appendChild(bar);
    return container;
}

/**
 * 创建生命周期状态卡片
 * @param {string} status - 状态类型
 * @param {string} title - 卡片标题
 * @param {string} description - 描述信息
 * @param {number} percentage - 进度百分比（可选）
 * @returns {HTMLElement} 状态卡片元素
 */
function createLifecycleStatusCard(status, title, description, percentage) {
    const card = document.createElement('div');
    card.className = `lifecycle-status-card ${status}`;
    
    const header = document.createElement('div');
    header.style.cssText = 'display: flex; align-items: center; margin-bottom: 0.5rem;';
    
    const indicator = createLifecycleIndicator(status);
    const titleElement = document.createElement('h4');
    titleElement.className = `lifecycle-text ${status}`;
    titleElement.textContent = title;
    titleElement.style.cssText = 'margin: 0; font-size: 1rem;';
    
    header.appendChild(indicator);
    header.appendChild(titleElement);
    
    const descElement = document.createElement('p');
    descElement.textContent = description;
    descElement.style.cssText = 'margin: 0 0 0.5rem 0; color: #6b7280; font-size: 0.875rem;';
    
    card.appendChild(header);
    card.appendChild(descElement);
    
    if (percentage !== undefined) {
        const progress = createLifecycleProgress(status, percentage);
        card.appendChild(progress);
    }
    
    return card;
}

/**
 * 获取生命周期状态文本
 * @param {string} status - 状态类型
 * @returns {string} 状态文本
 */
function getLifecycleStatusText(status) {
    const textMap = {
        'normal': '正常',
        'warning': '预警',
        'expired': '过期',
        'unknown': '未知'
    };
    return textMap[status] || '未知';
}

/**
 * 为现有按钮添加图标
 * @param {HTMLElement} button - 按钮元素
 * @param {string} iconName - 图标名称
 * @param {string} position - 图标位置 ('before' 或 'after')
 */
function addIconToButton(button, iconName, position = 'before') {
    const icon = createIcon(iconName, 'sm');
    
    if (position === 'before') {
        button.innerHTML = icon + ' ' + button.innerHTML;
    } else {
        button.innerHTML = button.innerHTML + ' ' + icon;
    }
}

/**
 * 批量为按钮添加图标
 * @param {Object} buttonIconMap - 按钮选择器和图标名称的映射
 */
function initializeButtonIcons(buttonIconMap) {
    Object.entries(buttonIconMap).forEach(([selector, iconName]) => {
        const buttons = document.querySelectorAll(selector);
        buttons.forEach(button => {
            if (!button.querySelector('.icon')) {
                addIconToButton(button, iconName);
            }
        });
    });
}

/**
 * 初始化页面图标
 * 为常见的按钮和元素自动添加图标
 */
function initializePageIcons() {
    // 常见按钮图标映射
    const buttonIconMap = {
        '.btn-primary:contains("添加")': 'plus',
        '.btn-primary:contains("新增")': 'plus',
        '.btn-secondary:contains("编辑")': 'edit',
        '.btn-secondary:contains("修改")': 'edit',
        '.btn-danger:contains("删除")': 'trash',
        '.btn-info:contains("查看")': 'view',
        '.btn-success:contains("下载")': 'download',
        '.btn:contains("搜索")': 'search',
        '.btn:contains("筛选")': 'filter',
        '.btn:contains("刷新")': 'refresh',
        '.btn:contains("设置")': 'settings'
    };
    
    // 使用更精确的选择器
    document.querySelectorAll('button, .btn').forEach(button => {
        const text = button.textContent.trim();
        let iconName = null;
        
        if (text.includes('添加') || text.includes('新增')) iconName = 'plus';
        else if (text.includes('编辑') || text.includes('修改')) iconName = 'edit';
        else if (text.includes('删除')) iconName = 'trash';
        else if (text.includes('查看')) iconName = 'view';
        else if (text.includes('下载')) iconName = 'download';
        else if (text.includes('上传')) iconName = 'upload';
        else if (text.includes('搜索')) iconName = 'search';
        else if (text.includes('筛选')) iconName = 'filter';
        else if (text.includes('刷新')) iconName = 'refresh';
        else if (text.includes('设置')) iconName = 'settings';
        
        if (iconName && !button.querySelector('.icon')) {
            addIconToButton(button, iconName);
        }
    });
    
    // 为生命周期状态添加图标
    document.querySelectorAll('[data-lifecycle-status]').forEach(element => {
        const status = element.getAttribute('data-lifecycle-status');
        element.innerHTML = createLifecycleStatus(status);
    });
}

/**
 * 更新表格中的生命周期状态显示
 * @param {HTMLElement} table - 表格元素
 * @param {number} statusColumnIndex - 状态列的索引
 */
function updateTableLifecycleStatus(table, statusColumnIndex = -1) {
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        
        // 如果没有指定列索引，自动查找包含生命周期状态的列
        if (statusColumnIndex === -1) {
            cells.forEach((cell, index) => {
                const text = cell.textContent.trim();
                if (LIFECYCLE_STATUS_MAP[text]) {
                    cell.innerHTML = createLifecycleStatus(text);
                }
            });
        } else if (cells[statusColumnIndex]) {
            const text = cells[statusColumnIndex].textContent.trim();
            if (LIFECYCLE_STATUS_MAP[text]) {
                cells[statusColumnIndex].innerHTML = createLifecycleStatus(text);
            }
        }
    });
}

// 页面加载完成后自动初始化图标
document.addEventListener('DOMContentLoaded', function() {
    initializePageIcons();
    
    // 为所有数据表格更新生命周期状态显示
    document.querySelectorAll('.data-table').forEach(table => {
        updateTableLifecycleStatus(table);
    });
});

// 导出函数供全局使用
window.IconManager = {
    createIcon,
    createIconButton,
    createLifecycleStatus,
    createLifecycleBadge,
    createLifecycleIndicator,
    createLifecycleProgress,
    createLifecycleStatusCard,
    getLifecycleStatusText,
    addIconToButton,
    initializeButtonIcons,
    initializePageIcons,
    updateTableLifecycleStatus
};