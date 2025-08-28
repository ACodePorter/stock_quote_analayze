-- =====================================================
-- 扩展 historical_quotes 表结构
-- 添加累计升跌%、5天升跌%和备注字段
-- =====================================================

-- 1. 检查当前表结构
SELECT '当前表结构:' as info;
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'historical_quotes' 
ORDER BY ordinal_position;

-- 2. 添加新字段（如果不存在）
-- 累计升跌%字段
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'historical_quotes' 
        AND column_name = 'cumulative_change_percent'
    ) THEN
        ALTER TABLE historical_quotes ADD COLUMN cumulative_change_percent DECIMAL(8,2);
        RAISE NOTICE '累计升跌%字段添加成功';
    ELSE
        RAISE NOTICE '累计升跌%字段已存在';
    END IF;
END $$;

-- 5天升跌%字段
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'historical_quotes' 
        AND column_name = 'five_day_change_percent'
    ) THEN
        ALTER TABLE historical_quotes ADD COLUMN five_day_change_percent DECIMAL(8,2);
        RAISE NOTICE '5天升跌%字段添加成功';
    ELSE
        RAISE NOTICE '5天升跌%字段已存在';
    END IF;
END $$;

-- 备注字段
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'historical_quotes' 
        AND column_name = 'remarks'
    ) THEN
        ALTER TABLE historical_quotes ADD COLUMN remarks TEXT;
        RAISE NOTICE '备注字段添加成功';
    ELSE
        RAISE NOTICE '备注字段已存在';
    END IF;
END $$;

-- 3. 创建备注管理表
CREATE TABLE IF NOT EXISTS trading_notes (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    notes TEXT,
    strategy_type VARCHAR(50),  -- 策略类型：如"买入信号"、"卖出信号"、"观察"等
    risk_level VARCHAR(20),     -- 风险等级：如"低"、"中"、"高"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),     -- 创建用户
    UNIQUE(stock_code, trade_date)
);

-- 4. 创建索引
-- trading_notes表的索引
CREATE INDEX IF NOT EXISTS idx_trading_notes_stock_code ON trading_notes(stock_code);
CREATE INDEX IF NOT EXISTS idx_trading_notes_trade_date ON trading_notes(trade_date);
CREATE INDEX IF NOT EXISTS idx_trading_notes_strategy_type ON trading_notes(strategy_type);

-- 5. 创建视图：合并历史行情和交易备注
CREATE OR REPLACE VIEW historical_quotes_with_notes AS
SELECT 
    h.*,
    COALESCE(tn.notes, '') as user_notes,
    COALESCE(tn.strategy_type, '') as strategy_type,
    COALESCE(tn.risk_level, '') as risk_level,
    COALESCE(tn.created_by, '') as notes_creator,
    tn.created_at as notes_created_at,
    tn.updated_at as notes_updated_at
FROM historical_quotes h
LEFT JOIN trading_notes tn ON h.code = tn.stock_code AND h.date = tn.trade_date;

-- 6. 创建函数：计算累计升跌%
CREATE OR REPLACE FUNCTION calculate_cumulative_change(
    p_stock_code VARCHAR(20),
    p_base_date DATE DEFAULT NULL
) RETURNS VOID AS $$
DECLARE
    v_base_date DATE;
    v_base_price DECIMAL(10,2);
BEGIN
    -- 如果没有指定基准日期，使用最早的数据作为基准
    IF p_base_date IS NULL THEN
        SELECT MIN(date) INTO v_base_date 
        FROM historical_quotes 
        WHERE code = p_stock_code;
    ELSE
        v_base_date := p_base_date;
    END IF;
    
    -- 获取基准价格
    SELECT close INTO v_base_price 
    FROM historical_quotes 
    WHERE code = p_stock_code AND date = v_base_date;
    
    -- 计算累计升跌%
    UPDATE historical_quotes 
    SET cumulative_change_percent = CASE 
        WHEN v_base_price > 0 THEN ((close - v_base_price) / v_base_price * 100)
        ELSE NULL 
    END
    WHERE code = p_stock_code;
    
    RAISE NOTICE '股票 % 的累计升跌%计算完成，基准日期: %, 基准价格: %', 
        p_stock_code, v_base_date, v_base_price;
END;
$$ LANGUAGE plpgsql;

-- 7. 创建函数：计算5天升跌%
CREATE OR REPLACE FUNCTION calculate_five_day_change(
    p_stock_code VARCHAR(20)
) RETURNS VOID AS $$
BEGIN
    -- 计算5天涨跌幅
    UPDATE historical_quotes h1
    SET five_day_change_percent = (
        SELECT CASE 
            WHEN h2.close > 0 THEN ((h1.close - h2.close) / h2.close * 100)
            ELSE NULL 
        END
        FROM historical_quotes h2
        WHERE h2.code = h1.code 
        AND h2.date = (
            SELECT MAX(date) 
            FROM historical_quotes h3 
            WHERE h3.code = h1.code 
            AND h3.date < h1.date
            AND h3.date >= h1.date - INTERVAL '7 days'
        )
    )
    WHERE h1.code = p_stock_code;
    
    RAISE NOTICE '股票 % 的5天升跌%计算完成', p_stock_code;
END;
$$ LANGUAGE plpgsql;

-- 8. 创建触发器：自动更新updated_at字段
CREATE OR REPLACE FUNCTION update_trading_notes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_trading_notes_updated_at
    BEFORE UPDATE ON trading_notes
    FOR EACH ROW
    EXECUTE FUNCTION update_trading_notes_updated_at();

-- 9. 验证表结构
SELECT '扩展后表结构:' as info;
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'historical_quotes' 
ORDER BY ordinal_position;

SELECT 'trading_notes表结构:' as info;
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'trading_notes' 
ORDER BY ordinal_position;

-- 10. 测试数据插入
-- 插入测试备注数据
INSERT INTO trading_notes (stock_code, trade_date, notes, strategy_type, risk_level, created_by)
VALUES 
    ('000001', '2025-08-01', '放量上涨，明天如果过7元就卖掉', '卖出信号', '中', 'wangxw1'),
    ('000001', '2025-08-02', '放量上涨', '观察', '低', 'wangxw1'),
    ('000001', '2025-08-03', '缩量下跌，跌到7元以下的时候可以买入一点', '买入信号', '中', 'wangxw1')
ON CONFLICT (stock_code, trade_date) DO UPDATE SET
    notes = EXCLUDED.notes,
    strategy_type = EXCLUDED.strategy_type,
    risk_level = EXCLUDED.risk_level,
    updated_at = CURRENT_TIMESTAMP;

-- 11. 测试视图查询
SELECT '测试视图查询:' as info;
SELECT 
    stock_code, 
    trade_date, 
    user_notes, 
    strategy_type, 
    risk_level
FROM historical_quotes_with_notes 
WHERE stock_code = '000001' 
ORDER BY trade_date DESC 
LIMIT 5;

-- 12. 测试函数调用
SELECT '测试函数调用:' as info;
-- 注意：这里需要替换为实际存在的股票代码
-- SELECT calculate_cumulative_change('000001');
-- SELECT calculate_five_day_change('000001');

-- 13. 清理测试数据（可选）
-- DELETE FROM trading_notes WHERE stock_code = '000001';

-- 14. 显示完成信息
SELECT '表结构扩展完成！' as status;
SELECT '新增字段:' as info;
SELECT '  - cumulative_change_percent: 累计升跌%' as field_info
UNION ALL
SELECT '  - five_day_change_percent: 5天升跌%' as field_info
UNION ALL
SELECT '  - remarks: 备注' as field_info;

SELECT '新增功能:' as info;
SELECT '  - trading_notes表: 交易备注管理' as feature
UNION ALL
SELECT '  - historical_quotes_with_notes视图: 合并显示' as feature
UNION ALL
SELECT '  - calculate_cumulative_change函数: 计算累计升跌%' as feature
UNION ALL
SELECT '  - calculate_five_day_change函数: 计算5天升跌%' as feature;
