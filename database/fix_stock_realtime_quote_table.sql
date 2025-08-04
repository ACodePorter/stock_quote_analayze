-- 修复 stock_realtime_quote 表结构
-- 参考 stock_basic_info 的主外键约束处理和检查

-- 1. 检查当前表结构
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'stock_realtime_quote' 
ORDER BY ordinal_position;

-- 2. 检查约束
SELECT conname, contype, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'stock_realtime_quote'::regclass;

-- 3. 如果表不存在，创建表
CREATE TABLE IF NOT EXISTS stock_realtime_quote (
    code TEXT PRIMARY KEY,
    name TEXT,
    current_price REAL,
    change_percent REAL,
    volume REAL,
    amount REAL,
    high REAL,
    low REAL,
    open REAL,
    pre_close REAL,
    turnover_rate REAL,
    pe_dynamic REAL,
    total_market_value REAL,
    pb_ratio REAL,
    circulating_market_value REAL,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 如果表存在但没有主键约束，添加主键约束
-- 首先删除可能存在的重复数据
DELETE FROM stock_realtime_quote a USING stock_realtime_quote b 
WHERE a.ctid < b.ctid AND a.code = b.code;

-- 删除可能有问题的约束（SQLite迁移过来的）
ALTER TABLE stock_realtime_quote DROP CONSTRAINT IF EXISTS idx_16466_sqlite_autoindex_stock_realtime_quote_1;
ALTER TABLE stock_realtime_quote DROP CONSTRAINT IF EXISTS stock_realtime_quote_code_fkey;

-- 添加主键约束（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'stock_realtime_quote_pkey' 
        AND conrelid = 'stock_realtime_quote'::regclass
    ) THEN
        ALTER TABLE stock_realtime_quote ADD CONSTRAINT stock_realtime_quote_pkey PRIMARY KEY (code);
    END IF;
END $$;

-- 5. 添加外键约束（如果stock_basic_info表存在且有主键）
DO $$
BEGIN
    -- 检查stock_basic_info表是否存在
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'stock_basic_info'
    ) THEN
        -- 检查stock_basic_info是否有主键约束
        IF EXISTS (
            SELECT 1 FROM pg_constraint 
            WHERE conrelid = 'stock_basic_info'::regclass 
            AND contype = 'p'
        ) THEN
            -- 添加外键约束（如果不存在）
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint 
                WHERE conname = 'fk_stock_realtime_quote_code' 
                AND conrelid = 'stock_realtime_quote'::regclass
            ) THEN
                ALTER TABLE stock_realtime_quote 
                ADD CONSTRAINT fk_stock_realtime_quote_code 
                FOREIGN KEY (code) REFERENCES stock_basic_info(code);
            END IF;
        END IF;
    END IF;
END $$;

-- 6. 创建索引（如果不存在）
CREATE INDEX IF NOT EXISTS idx_stock_realtime_quote_update_time ON stock_realtime_quote(update_time);
CREATE INDEX IF NOT EXISTS idx_stock_realtime_quote_name ON stock_realtime_quote(name);

-- 7. 验证修复结果
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'stock_realtime_quote' 
ORDER BY ordinal_position;

SELECT 
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint 
WHERE conrelid = 'stock_realtime_quote'::regclass;

-- 8. 测试插入（可选）
-- INSERT INTO stock_realtime_quote (
--     code, name, current_price, change_percent, volume, amount,
--     high, low, open, pre_close, turnover_rate, pe_dynamic,
--     total_market_value, pb_ratio, circulating_market_value, update_time
-- ) VALUES (
--     '000001', '平安银行', 10.50, 2.5, 1000000, 10500000,
--     10.80, 10.20, 10.30, 10.25, 1.2, 15.5,
--     1000000000, 1.2, 800000000, '2025-08-01 16:30:00'
-- ) ON CONFLICT (code) DO UPDATE SET
--     name = EXCLUDED.name,
--     current_price = EXCLUDED.current_price,
--     change_percent = EXCLUDED.change_percent,
--     volume = EXCLUDED.volume,
--     amount = EXCLUDED.amount,
--     high = EXCLUDED.high,
--     low = EXCLUDED.low,
--     open = EXCLUDED.open,
--     pre_close = EXCLUDED.pre_close,
--     turnover_rate = EXCLUDED.turnover_rate,
--     pe_dynamic = EXCLUDED.pe_dynamic,
--     total_market_value = EXCLUDED.total_market_value,
--     pb_ratio = EXCLUDED.pb_ratio,
--     circulating_market_value = EXCLUDED.circulating_market_value,
--     update_time = EXCLUDED.update_time; 