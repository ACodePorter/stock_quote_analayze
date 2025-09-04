-- 为 stock_basic_info 表添加全量采集标志字段
-- 执行时间: 2025-09-04

-- 1. 检查当前表结构
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'stock_basic_info' 
ORDER BY ordinal_position;

-- 2. 添加全量采集标志字段
-- full_collection_completed: 全量采集完成标志 (true=已完成, false=未完成)
-- full_collection_date: 全量采集完成日期
-- full_collection_start_date: 全量采集开始日期
-- full_collection_end_date: 全量采集结束日期

ALTER TABLE stock_basic_info 
ADD COLUMN IF NOT EXISTS full_collection_completed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS full_collection_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS full_collection_start_date DATE,
ADD COLUMN IF NOT EXISTS full_collection_end_date DATE;

-- 3. 添加注释
COMMENT ON COLUMN stock_basic_info.full_collection_completed IS '全量采集完成标志：true=已完成，false=未完成';
COMMENT ON COLUMN stock_basic_info.full_collection_date IS '全量采集完成时间';
COMMENT ON COLUMN stock_basic_info.full_collection_start_date IS '全量采集开始日期';
COMMENT ON COLUMN stock_basic_info.full_collection_end_date IS '全量采集结束日期';

-- 4. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_stock_basic_info_full_collection_completed 
ON stock_basic_info(full_collection_completed);

CREATE INDEX IF NOT EXISTS idx_stock_basic_info_full_collection_date 
ON stock_basic_info(full_collection_date);

-- 5. 验证字段添加结果
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'stock_basic_info' 
ORDER BY ordinal_position;

-- 6. 显示当前全量采集状态统计
SELECT 
    full_collection_completed,
    COUNT(*) as stock_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM stock_basic_info), 2) as percentage
FROM stock_basic_info 
GROUP BY full_collection_completed 
ORDER BY full_collection_completed;

-- 7. 显示最近完成全量采集的股票（如果有）
SELECT 
    code,
    name,
    full_collection_date,
    full_collection_start_date,
    full_collection_end_date
FROM stock_basic_info 
WHERE full_collection_completed = TRUE 
ORDER BY full_collection_date DESC 
LIMIT 10;
