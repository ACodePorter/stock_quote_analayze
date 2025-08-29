-- 添加5天升跌%字段到historical_quotes表
-- 执行时间：2025-01-XX
-- 说明：为历史行情数据添加5天升跌%计算字段

-- 1. 检查字段是否存在，如果不存在则添加
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

-- 2. 创建计算5天升跌%的函数
CREATE OR REPLACE FUNCTION calculate_five_day_change(p_stock_code VARCHAR(20))
RETURNS VOID AS $$
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

-- 3. 创建批量计算所有股票5天升跌%的函数
CREATE OR REPLACE FUNCTION calculate_all_five_day_change()
RETURNS TABLE(stock_code VARCHAR(20), status TEXT) AS $$
DECLARE
    stock_record RECORD;
    success_count INTEGER := 0;
    failed_count INTEGER := 0;
BEGIN
    -- 遍历所有股票代码
    FOR stock_record IN 
        SELECT DISTINCT code FROM historical_quotes
    LOOP
        BEGIN
            PERFORM calculate_five_day_change(stock_record.code);
            success_count := success_count + 1;
            stock_code := stock_record.code;
            status := '成功';
            RETURN NEXT;
        EXCEPTION WHEN OTHERS THEN
            failed_count := failed_count + 1;
            stock_code := stock_record.code;
            status := '失败: ' || SQLERRM;
            RETURN NEXT;
        END;
    END LOOP;
    
    RAISE NOTICE '批量计算完成，成功: %, 失败: %', success_count, failed_count;
END;
$$ LANGUAGE plpgsql;

-- 4. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_historical_quotes_five_day_change 
ON historical_quotes(code, date, five_day_change_percent);

-- 5. 创建视图，显示已计算5天升跌%的数据
CREATE OR REPLACE VIEW v_five_day_change_status AS
SELECT 
    code as stock_code,
    COUNT(*) as total_records,
    COUNT(five_day_change_percent) as calculated_records,
    ROUND(COUNT(five_day_change_percent) * 100.0 / COUNT(*), 2) as calculation_rate,
    MAX(date) as latest_date,
    MAX(CASE WHEN five_day_change_percent IS NOT NULL THEN date END) as latest_calculated_date
FROM historical_quotes
GROUP BY code
ORDER BY calculation_rate DESC, total_records DESC;

-- 6. 创建触发器，在插入新数据后自动计算5天升跌%
CREATE OR REPLACE FUNCTION trigger_calculate_five_day_change()
RETURNS TRIGGER AS $$
BEGIN
    -- 延迟计算，避免在事务中立即计算
    PERFORM pg_notify('calculate_five_day_change', NEW.code);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器（可选，用于实时计算）
-- DROP TRIGGER IF EXISTS tr_calculate_five_day_change ON historical_quotes;
-- CREATE TRIGGER tr_calculate_five_day_change
--     AFTER INSERT OR UPDATE ON historical_quotes
--     FOR EACH ROW
--     EXECUTE FUNCTION trigger_calculate_five_day_change();

-- 7. 创建统计函数
CREATE OR REPLACE FUNCTION get_five_day_change_stats()
RETURNS TABLE(
    total_stocks INTEGER,
    total_records BIGINT,
    calculated_records BIGINT,
    calculation_rate DECIMAL(5,2),
    avg_five_day_change DECIMAL(8,2),
    max_five_day_change DECIMAL(8,2),
    min_five_day_change DECIMAL(8,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT h.code)::INTEGER as total_stocks,
        COUNT(*)::BIGINT as total_records,
        COUNT(h.five_day_change_percent)::BIGINT as calculated_records,
        ROUND(COUNT(h.five_day_change_percent) * 100.0 / COUNT(*), 2) as calculation_rate,
        ROUND(AVG(h.five_day_change_percent), 2) as avg_five_day_change,
        ROUND(MAX(h.five_day_change_percent), 2) as max_five_day_change,
        ROUND(MIN(h.five_day_change_percent), 2) as min_five_day_change
    FROM historical_quotes h;
END;
$$ LANGUAGE plpgsql;

-- 8. 创建清理函数，用于重新计算
CREATE OR REPLACE FUNCTION reset_five_day_change_calculations(p_stock_code VARCHAR(20) DEFAULT NULL)
RETURNS INTEGER AS $$
DECLARE
    affected_rows INTEGER;
BEGIN
    IF p_stock_code IS NULL THEN
        -- 重置所有股票的5天升跌%
        UPDATE historical_quotes SET five_day_change_percent = NULL;
        GET DIAGNOSTICS affected_rows = ROW_COUNT;
        RAISE NOTICE '已重置 % 条记录的5天升跌%', affected_rows;
    ELSE
        -- 重置指定股票的5天升跌%
        UPDATE historical_quotes 
        SET five_day_change_percent = NULL 
        WHERE code = p_stock_code;
        GET DIAGNOSTICS affected_rows = ROW_COUNT;
        RAISE NOTICE '已重置股票 % 的 % 条记录的5天升跌%', p_stock_code, affected_rows;
    END IF;
    
    RETURN affected_rows;
END;
$$ LANGUAGE plpgsql;

-- 9. 创建测试数据验证函数
CREATE OR REPLACE FUNCTION test_five_day_change_calculation(p_stock_code VARCHAR(20))
RETURNS TABLE(
    test_date DATE,
    current_close DECIMAL(10,2),
    five_day_ago_close DECIMAL(10,2),
    calculated_change DECIMAL(8,2),
    stored_change DECIMAL(8,2),
    is_valid BOOLEAN
) AS $$
DECLARE
    test_record RECORD;
    five_day_ago_record RECORD;
BEGIN
    -- 获取指定股票的最新5条记录
    FOR test_record IN 
        SELECT date, close, five_day_change_percent
        FROM historical_quotes 
        WHERE code = p_stock_code 
        AND five_day_change_percent IS NOT NULL
        ORDER BY date DESC 
        LIMIT 5
    LOOP
        -- 获取5天前的记录
        SELECT date, close INTO five_day_ago_record
        FROM historical_quotes 
        WHERE code = p_stock_code 
        AND date < test_record.date
        ORDER BY date DESC 
        LIMIT 1 OFFSET 4;
        
        IF five_day_ago_record.close IS NOT NULL AND five_day_ago_record.close > 0 THEN
            test_date := test_record.date;
            current_close := test_record.close;
            five_day_ago_close := five_day_ago_record.close;
            calculated_change := ROUND(((test_record.close - five_day_ago_record.close) / five_day_ago_record.close * 100), 2);
            stored_change := test_record.five_day_change_percent;
            is_valid := ABS(calculated_change - test_record.five_day_change_percent) < 0.01;
            RETURN NEXT;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 10. 执行初始计算（可选，数据量大时建议分批执行）
-- SELECT calculate_five_day_change('000001');  -- 计算平安银行的5天升跌%
-- SELECT calculate_five_day_change('000002');  -- 计算万科的5天升跌%

-- 11. 查看计算状态
-- SELECT * FROM v_five_day_change_status LIMIT 10;
-- SELECT * FROM get_five_day_change_stats();

-- 12. 测试验证（可选）
-- SELECT * FROM test_five_day_change_calculation('000001') LIMIT 3;
