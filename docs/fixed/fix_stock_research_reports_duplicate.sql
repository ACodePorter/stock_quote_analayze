-- 修复生产环境stock_research_reports表重复数据问题的SQL脚本
-- 执行前请务必备份数据库！

-- 1. 创建备份表
CREATE TABLE stock_research_reports_backup_$(date +%Y%m%d_%H%M%S) AS 
SELECT * FROM stock_research_reports;

-- 2. 查找重复记录（查看用，不执行）
/*
SELECT stock_code, stock_name, report_name, report_date, COUNT(*) as count
FROM stock_research_reports
GROUP BY stock_code, stock_name, report_name, report_date
HAVING COUNT(*) > 1
ORDER BY count DESC, stock_code, report_date;
*/

-- 3. 移除重复记录，保留最新的一条（基于updated_at和id）
DELETE FROM stock_research_reports 
WHERE id IN (
    SELECT id FROM (
        SELECT id,
               ROW_NUMBER() OVER (
                   PARTITION BY stock_code, stock_name, report_name, report_date
                   ORDER BY updated_at DESC, id DESC
               ) as rn
        FROM stock_research_reports
    ) t
    WHERE t.rn > 1
);

-- 4. 验证是否还有重复记录
/*
SELECT stock_code, stock_name, report_name, report_date, COUNT(*) as count
FROM stock_research_reports
GROUP BY stock_code, stock_name, report_name, report_date
HAVING COUNT(*) > 1;
*/

-- 5. 添加唯一约束防止未来重复（如果不存在的话）
-- 注意：如果约束已存在，此语句会失败，可以忽略
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conrelid = 'stock_research_reports'::regclass 
        AND conname = 'uk_stock_research_reports_unique'
    ) THEN
        ALTER TABLE stock_research_reports 
        ADD CONSTRAINT uk_stock_research_reports_unique 
        UNIQUE (stock_code, report_name, report_date);
        RAISE NOTICE '唯一约束添加成功';
    ELSE
        RAISE NOTICE '唯一约束已存在';
    END IF;
END $$;

-- 6. 显示修复后的记录数
SELECT COUNT(*) as total_records FROM stock_research_reports;

-- 7. 显示表的约束信息
SELECT conname, contype, pg_get_constraintdef(oid) as constraint_def
FROM pg_constraint 
WHERE conrelid = 'stock_research_reports'::regclass;
