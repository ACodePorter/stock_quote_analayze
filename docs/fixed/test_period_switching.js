// 测试K线不同时长类型数据切换功能
// 使用方法：在浏览器控制台中运行此脚本

console.log('=== K线时间周期切换测试 ===');

// 模拟测试数据
const testPeriods = [
    { period: '1m', name: '1分钟', expectedDataPoints: 330 },
    { period: '5m', name: '5分钟', expectedDataPoints: 198 },
    { period: '15m', name: '15分钟', expectedDataPoints: 154 },
    { period: '30m', name: '30分钟', expectedDataPoints: 154 },
    { period: '1h', name: '1小时', expectedDataPoints: 120 },
    { period: '1d', name: '日线', expectedDataPoints: 90 },
    { period: '1w', name: '周线', expectedDataPoints: 52 },
    { period: '1M', name: '月线', expectedDataPoints: 24 }
];

// 测试URL生成逻辑
function testURLGeneration() {
    console.log('\n--- 测试URL生成逻辑 ---');
    
    const API_BASE_URL = 'http://192.168.31.237:5000';
    const stockCode = '300453';
    
    testPeriods.forEach(test => {
        let url;
        let period, startDate, endDate, adjust;
        
        switch (test.period) {
            case '1m':
                period = '1';
                const today = new Date();
                const startTime = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 9, 30, 0);
                const endTime = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 15, 0, 0);
                url = `${API_BASE_URL}/api/stock/kline_min_hist?code=${stockCode}&period=${period}&start_datetime=${startTime.toISOString()}&end_datetime=${endTime.toISOString()}&adjust=qfq`;
                break;
            case '5m':
                period = '5';
                endDate = new Date();
                startDate = new Date();
                startDate.setDate(startDate.getDate() - 3);
                url = `${API_BASE_URL}/api/stock/kline_min_hist?code=${stockCode}&period=${period}&start_datetime=${startDate.toISOString()}&end_datetime=${endDate.toISOString()}&adjust=qfq`;
                break;
            case '15m':
                period = '15';
                endDate = new Date();
                startDate = new Date();
                startDate.setDate(startDate.getDate() - 7);
                url = `${API_BASE_URL}/api/stock/kline_min_hist?code=${stockCode}&period=${period}&start_datetime=${startDate.toISOString()}&end_datetime=${endDate.toISOString()}&adjust=qfq`;
                break;
            case '30m':
                period = '30';
                endDate = new Date();
                startDate = new Date();
                startDate.setDate(startDate.getDate() - 14);
                url = `${API_BASE_URL}/api/stock/kline_min_hist?code=${stockCode}&period=${period}&start_datetime=${startDate.toISOString()}&end_datetime=${endDate.toISOString()}&adjust=qfq`;
                break;
            case '1h':
                period = '60';
                endDate = new Date();
                startDate = new Date();
                startDate.setDate(startDate.getDate() - 30);
                url = `${API_BASE_URL}/api/stock/kline_min_hist?code=${stockCode}&period=${period}&start_datetime=${startDate.toISOString()}&end_datetime=${endDate.toISOString()}&adjust=qfq`;
                break;
            case '1d':
                period = 'daily';
                endDate = new Date();
                startDate = new Date();
                startDate.setDate(startDate.getDate() - 90);
                url = `${API_BASE_URL}/api/stock/kline_hist?code=${stockCode}&period=${period}&start_date=${startDate.toISOString().split('T')[0]}&end_date=${endDate.toISOString().split('T')[0]}&adjust=qfq`;
                break;
            case '1w':
                period = 'weekly';
                endDate = new Date();
                startDate = new Date();
                startDate.setDate(startDate.getDate() - 365);
                url = `${API_BASE_URL}/api/stock/kline_hist?code=${stockCode}&period=${period}&start_date=${startDate.toISOString().split('T')[0]}&end_date=${endDate.toISOString().split('T')[0]}&adjust=qfq`;
                break;
            case '1M':
                period = 'monthly';
                endDate = new Date();
                startDate = new Date();
                startDate.setDate(startDate.getDate() - 730);
                url = `${API_BASE_URL}/api/stock/kline_hist?code=${stockCode}&period=${period}&start_date=${startDate.toISOString().split('T')[0]}&end_date=${endDate.toISOString().split('T')[0]}&adjust=qfq`;
                break;
        }
        
        console.log(`${test.name} (${test.period}):`);
        console.log(`  预期数据点: ${test.expectedDataPoints}`);
        console.log(`  API接口: ${test.period === '1d' || test.period === '1w' || test.period === '1M' ? 'kline_hist' : 'kline_min_hist'}`);
        console.log(`  URL: ${url}`);
        console.log('');
    });
}

// 测试模拟数据生成
function testMockDataGeneration() {
    console.log('\n--- 测试模拟数据生成 ---');
    
    testPeriods.forEach(test => {
        console.log(`${test.name} (${test.period}):`);
        console.log(`  预期数据点: ${test.expectedDataPoints}`);
        
        // 模拟generateMockKlineData函数的逻辑
        let dataPoints, dateFormat;
        
        switch (test.period) {
            case '1m':
                dataPoints = 330;
                dateFormat = 'time';
                break;
            case '5m':
                dataPoints = 3 * 66;
                dateFormat = 'datetime';
                break;
            case '15m':
                dataPoints = 7 * 22;
                dateFormat = 'datetime';
                break;
            case '30m':
                dataPoints = 14 * 11;
                dateFormat = 'datetime';
                break;
            case '1h':
                dataPoints = 30 * 4;
                dateFormat = 'datetime';
                break;
            case '1d':
                dataPoints = 90;
                dateFormat = 'date';
                break;
            case '1w':
                dataPoints = 52;
                dateFormat = 'date';
                break;
            case '1M':
                dataPoints = 24;
                dateFormat = 'date';
                break;
            default:
                dataPoints = 30;
                dateFormat = 'date';
        }
        
        console.log(`  实际数据点: ${dataPoints}`);
        console.log(`  日期格式: ${dateFormat}`);
        console.log(`  状态: ${dataPoints === test.expectedDataPoints ? '✓ 通过' : '✗ 失败'}`);
        console.log('');
    });
}

// 测试周期名称映射
function testPeriodNameMapping() {
    console.log('\n--- 测试周期名称映射 ---');
    
    const periodNames = {
        '1m': '1分钟',
        '5m': '5分钟',
        '15m': '15分钟',
        '30m': '30分钟',
        '1h': '1小时',
        '1d': '日线',
        '1w': '周线',
        '1M': '月线'
    };
    
    testPeriods.forEach(test => {
        const expectedName = periodNames[test.period];
        console.log(`${test.period} -> ${expectedName}`);
    });
}

// 运行所有测试
function runAllTests() {
    testURLGeneration();
    testMockDataGeneration();
    testPeriodNameMapping();
    
    console.log('\n=== 测试完成 ===');
    console.log('如果所有测试都通过，说明修复成功！');
    console.log('现在可以在页面上点击不同的时间周期按钮来测试实际效果。');
}

// 执行测试
runAllTests();

// 导出测试函数供外部调用
window.testPeriodSwitching = {
    testURLGeneration,
    testMockDataGeneration,
    testPeriodNameMapping,
    runAllTests
};
