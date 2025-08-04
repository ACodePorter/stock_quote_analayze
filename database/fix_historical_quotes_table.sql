-- =====================================================
-- 修复 historical_quotes 表主键和索引
-- 解决生产环境缺少主键约束的问题
-- =====================================================

-- 1. 检查当前表结构
SELECT '当前表结构:' as info;
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'historical_quotes' 
ORDER BY ordinal_position;

-- 2. 检查当前约束
SELECT '当前约束:' as info;
SELECT conname, contype, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'historical_quotes'::regclass;

-- 3. 检查当前索引
SELECT '当前索引:' as info;
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'historical_quotes';

-- 4. 检查重复数据
SELECT '重复数据检查:' as info;
SELECT code, date, COUNT(*) as count
FROM historical_quotes 
GROUP BY code, date 
HAVING COUNT(*) > 1
LIMIT 10;

-- 5. 删除重复数据（保留每组的第一条）
DELETE FROM historical_quotes 
WHERE ctid NOT IN (
    SELECT MIN(ctid) 
    FROM historical_quotes 
    GROUP BY code, date
);

-- 6. 删除可能有问题的约束（SQLite迁移过来的）
ALTER TABLE historical_quotes DROP CONSTRAINT IF EXISTS idx_16466_sqlite_autoindex_historical_quotes_1;
ALTER TABLE historical_quotes DROP CONSTRAINT IF EXISTS historical_quotes_pkey;

-- 7. 添加主键约束（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'historical_quotes_pkey' 
        AND conrelid = 'historical_quotes'::regclass
    ) THEN
        ALTER TABLE historical_quotes ADD CONSTRAINT historical_quotes_pkey PRIMARY KEY (code, date);
        RAISE NOTICE '主键约束添加成功';
    ELSE
        RAISE NOTICE '主键约束已存在';
    END IF;
END $$;

-- 8. 创建索引（如果不存在）
-- code索引
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'historical_quotes' 
        AND indexname = 'idx_historical_quotes_code'
    ) THEN
        CREATE INDEX idx_historical_quotes_code ON historical_quotes(code);
        RAISE NOTICE 'code索引创建成功';
    ELSE
        RAISE NOTICE 'code索引已存在';
    END IF;
END $$;

-- date索引
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'historical_quotes' 
        AND indexname = 'idx_historical_quotes_date'
    ) THEN
        CREATE INDEX idx_historical_quotes_date ON historical_quotes(date);
        RAISE NOTICE 'date索引创建成功';
    ELSE
        RAISE NOTICE 'date索引已存在';
    END IF;
END $$;

-- collected_date索引
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'historical_quotes' 
        AND indexname = 'idx_historical_quotes_collected_date'
    ) THEN
        CREATE INDEX idx_historical_quotes_collected_date ON historical_quotes(collected_date);
        RAISE NOTICE 'collected_date索引创建成功';
    ELSE
        RAISE NOTICE 'collected_date索引已存在';
    END IF;
END $$;

-- 9. 更新表统计信息
ANALYZE historical_quotes;

-- 10. 验证修复结果
SELECT '修复后约束:' as info;
SELECT conname, contype, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'historical_quotes'::regclass;

SELECT '修复后索引:' as info;
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'historical_quotes';

-- 11. 测试插入操作
-- 注意：这个测试会插入一条测试数据，然后删除
INSERT INTO historical_quotes (
    code, name, market, date, open, high, low, close, 
    volume, amount, change_percent, collected_source
) VALUES (
    '000001', '平安银行', 'SZ', '20250801', 10.50, 10.80, 10.20, 10.60,
    1000000, 10600000, 2.5, 'test'
) ON CONFLICT (code, date) DO UPDATE SET
    name = EXCLUDED.name,
    market = EXCLUDED.market,
    open = EXCLUDED.open,
    high = EXCLUDED.high,
    low = EXCLUDED.low,
    close = EXCLUDED.close,
    volume = EXCLUDED.volume,
    amount = EXCLUDED.amount,
    change_percent = EXCLUDED.change_percent,
    collected_source = EXCLUDED.collected_source;

-- 清理测试数据
DELETE FROM historical_quotes WHERE code = '000001' AND date = '20250801';

SELECT '修复完成！' as result; 