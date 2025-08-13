// 快速诊断脚本 - 在浏览器控制台中运行
console.log('=== 开始快速诊断 ===');

// 1. 检查基础环境
console.log('1. 基础环境检查:');
console.log('  - window对象:', typeof window !== 'undefined' ? '✅' : '❌');
console.log('  - document对象:', typeof document !== 'undefined' ? '✅' : '❌');
console.log('  - 页面URL:', window.location.href);
console.log('  - 页面标题:', document.title);

// 2. 检查脚本加载
console.log('\n2. 脚本加载检查:');
console.log('  - Config对象:', typeof Config !== 'undefined' ? '✅' : '❌');
console.log('  - echarts库:', typeof echarts !== 'undefined' ? '✅' : '❌');
console.log('  - API_BASE_URL:', typeof API_BASE_URL !== 'undefined' ? '✅' : '❌');
console.log('  - CommonUtils:', typeof CommonUtils !== 'undefined' ? '✅' : '❌');

if (typeof echarts !== 'undefined') {
    console.log('  - ECharts版本:', echarts.version);
}

// 3. 检查DOM元素
console.log('\n3. DOM元素检查:');
const klineChart = document.getElementById('klineChart');
const minuteChart = document.getElementById('minuteChart');
console.log('  - klineChart元素:', klineChart ? '✅' : '❌');
console.log('  - minuteChart元素:', minuteChart ? '✅' : '❌');

if (klineChart) {
    console.log('  - klineChart尺寸:', klineChart.offsetWidth, 'x', klineChart.offsetHeight);
    console.log('  - klineChart样式:', window.getComputedStyle(klineChart).display);
}

if (minuteChart) {
    console.log('  - minuteChart尺寸:', minuteChart.offsetWidth, 'x', minuteChart.offsetHeight);
    console.log('  - minuteChart样式:', window.getComputedStyle(minuteChart).display);
}

// 4. 检查 StockPage 对象
console.log('\n4. StockPage对象检查:');
console.log('  - StockPage对象:', typeof StockPage !== 'undefined' ? '✅' : '❌');

if (typeof StockPage !== 'undefined') {
    console.log('  - StockPage.stockCode:', StockPage.stockCode);
    console.log('  - StockPage.klineChart:', StockPage.klineChart ? '已初始化' : '未初始化');
    console.log('  - StockPage.minuteChart:', StockPage.minuteChart ? '已初始化' : '未初始化');
}

// 5. 检查事件监听器
console.log('\n5. 事件监听器检查:');
const eventListeners = getEventListeners ? getEventListeners(document) : '无法获取';
console.log('  - DOM事件监听器:', eventListeners);

// 6. 尝试手动初始化图表
console.log('\n6. 手动初始化测试:');
if (typeof echarts !== 'undefined' && klineChart) {
    try {
        console.log('  尝试手动初始化K线图表...');
        const testChart = echarts.init(klineChart);
        const testOption = {
            title: { text: '测试图表' },
            xAxis: { type: 'category', data: ['A', 'B', 'C'] },
            yAxis: { type: 'value' },
            series: [{ data: [10, 20, 30], type: 'bar' }]
        };
        testChart.setOption(testOption);
        console.log('  ✅ 手动初始化成功');
        
        // 清理测试图表
        setTimeout(() => {
            testChart.dispose();
            console.log('  测试图表已清理');
        }, 3000);
        
    } catch (error) {
        console.error('  ❌ 手动初始化失败:', error);
    }
} else {
    console.log('  ⚠️ 无法进行手动初始化测试');
}

// 7. 检查控制台错误
console.log('\n7. 控制台错误检查:');
console.log('  请查看控制台是否有红色错误信息');

// 8. 检查网络请求
console.log('\n8. 网络请求检查:');
console.log('  请查看Network标签页是否有失败的请求');

console.log('\n=== 诊断完成 ===');
console.log('如果发现问题，请提供具体的错误信息');

// 辅助函数：获取所有事件监听器（如果可用）
function getEventListeners(element) {
    try {
        // 这是一个简化的检查，实际上浏览器不提供直接访问事件监听器的API
        return '需要手动检查';
    } catch (error) {
        return '无法获取';
    }
}
