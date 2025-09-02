-- 添加60天涨跌%字段（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'historical_quotes' 
        AND column_name = 'sixty_day_change_percent'
    ) THEN
        ALTER TABLE historical_quotes ADD COLUMN sixty_day_change_percent DECIMAL(8,2);
        RAISE NOTICE '60天涨跌%字段添加成功';
    ELSE
        RAISE NOTICE '60天涨跌%字段已存在';
    END IF;
END $$;
