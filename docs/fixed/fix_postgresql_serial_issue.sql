-- 修复PostgreSQL中stock_news表id字段的SERIAL问题
-- 执行此脚本前请先备份数据库

-- 1. 检查当前表结构
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    CASE 
        WHEN column_name = 'id' THEN 
            (SELECT pg_get_serial_sequence('stock_news', 'id'))::text
        ELSE 'N/A'
    END as sequence_name
FROM information_schema.columns 
WHERE table_name = 'stock_news' 
ORDER BY ordinal_position;

-- 2. 检查序列状态
SELECT 
    schemaname,
    sequencename,
    last_value,
    is_called,
    is_cycled
FROM pg_sequences 
WHERE sequencename LIKE '%stock_news%';

-- 3. 如果序列不存在或有问题，重新创建序列
-- 注意：这会重置id字段的计数，请谨慎操作

-- 删除现有的序列（如果存在）
DROP SEQUENCE IF EXISTS stock_news_id_seq CASCADE;

-- 重新创建序列
CREATE SEQUENCE stock_news_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

-- 4. 将序列关联到id字段
ALTER TABLE stock_news ALTER COLUMN id SET DEFAULT nextval('stock_news_id_seq');

-- 5. 设置序列的所有者
ALTER SEQUENCE stock_news_id_seq OWNED BY stock_news.id;

-- 6. 重置序列到当前表中的最大id值
SELECT setval('stock_news_id_seq', COALESCE((SELECT MAX(id) FROM stock_news), 0) + 1, false);

-- 7. 验证修复结果
SELECT 
    'Sequence created' as status,
    sequencename,
    last_value,
    is_called
FROM pg_sequences 
WHERE sequencename = 'stock_news_id_seq';

-- 8. 测试插入（可选，用于验证）
-- INSERT INTO stock_news (stock_code, title, content, created_at) 
-- VALUES ('TEST', 'Test Title', 'Test Content', NOW())
-- RETURNING id;

-- 9. 如果测试成功，可以删除测试数据
-- DELETE FROM stock_news WHERE stock_code = 'TEST';

-- 10. 最终验证
SELECT 
    'Final check' as check_type,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'stock_news' AND column_name = 'id';
