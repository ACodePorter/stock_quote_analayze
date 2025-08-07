-- 修复operation_logs表结构
-- 添加缺失的字段

-- 1. 检查表是否存在
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'operation_logs') THEN
        -- 如果表不存在，创建完整的表
        CREATE TABLE operation_logs (
            id SERIAL PRIMARY KEY,
            operation_type VARCHAR(100) NOT NULL,
            operation_desc TEXT,
            affected_rows INTEGER DEFAULT 0,
            status VARCHAR(20) NOT NULL DEFAULT 'success',
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- 创建索引
        CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at);
        CREATE INDEX idx_operation_logs_status ON operation_logs(status);
        CREATE INDEX idx_operation_logs_operation_type ON operation_logs(operation_type);
        
        RAISE NOTICE '创建了operation_logs表';
    ELSE
        -- 如果表存在，检查并添加缺失的字段
        RAISE NOTICE 'operation_logs表已存在，检查字段...';
        
        -- 添加operation_type字段（如果不存在）
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'operation_logs' AND column_name = 'operation_type') THEN
            ALTER TABLE operation_logs ADD COLUMN operation_type VARCHAR(100) NOT NULL DEFAULT 'unknown';
            RAISE NOTICE '添加了operation_type字段';
        END IF;
        
        -- 添加operation_desc字段（如果不存在）
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'operation_logs' AND column_name = 'operation_desc') THEN
            ALTER TABLE operation_logs ADD COLUMN operation_desc TEXT;
            RAISE NOTICE '添加了operation_desc字段';
        END IF;
        
        -- 添加affected_rows字段（如果不存在）
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'operation_logs' AND column_name = 'affected_rows') THEN
            ALTER TABLE operation_logs ADD COLUMN affected_rows INTEGER DEFAULT 0;
            RAISE NOTICE '添加了affected_rows字段';
        END IF;
        
        -- 添加status字段（如果不存在）
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'operation_logs' AND column_name = 'status') THEN
            ALTER TABLE operation_logs ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'success';
            RAISE NOTICE '添加了status字段';
        END IF;
        
        -- 添加error_message字段（如果不存在）
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'operation_logs' AND column_name = 'error_message') THEN
            ALTER TABLE operation_logs ADD COLUMN error_message TEXT;
            RAISE NOTICE '添加了error_message字段';
        END IF;
        
        -- 添加created_at字段（如果不存在）
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'operation_logs' AND column_name = 'created_at') THEN
            ALTER TABLE operation_logs ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            RAISE NOTICE '添加了created_at字段';
        END IF;
        
        -- 创建索引（如果不存在）
        IF NOT EXISTS (SELECT FROM pg_indexes WHERE tablename = 'operation_logs' AND indexname = 'idx_operation_logs_created_at') THEN
            CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at);
            RAISE NOTICE '创建了created_at索引';
        END IF;
        
        IF NOT EXISTS (SELECT FROM pg_indexes WHERE tablename = 'operation_logs' AND indexname = 'idx_operation_logs_status') THEN
            CREATE INDEX idx_operation_logs_status ON operation_logs(status);
            RAISE NOTICE '创建了status索引';
        END IF;
        
        IF NOT EXISTS (SELECT FROM pg_indexes WHERE tablename = 'operation_logs' AND indexname = 'idx_operation_logs_operation_type') THEN
            CREATE INDEX idx_operation_logs_operation_type ON operation_logs(operation_type);
            RAISE NOTICE '创建了operation_type索引';
        END IF;
    END IF;
END $$;

-- 2. 显示修复后的表结构
\d operation_logs;

-- 3. 检查是否有数据，如果没有则插入测试数据
DO $$
DECLARE
    record_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO record_count FROM operation_logs;
    
    IF record_count = 0 THEN
        -- 插入测试数据
        INSERT INTO operation_logs (operation_type, operation_desc, affected_rows, status, error_message) VALUES
        ('user_login', '用户登录操作', 1, 'success', NULL),
        ('data_export', '数据导出操作', 100, 'success', NULL),
        ('system_backup', '系统备份操作', 0, 'success', NULL),
        ('data_import', '数据导入操作', 50, 'partial_success', '部分数据导入失败'),
        ('user_logout', '用户登出操作', 1, 'success', NULL),
        ('config_update', '配置更新操作', 1, 'success', NULL),
        ('data_cleanup', '数据清理操作', 200, 'success', NULL),
        ('report_generation', '报告生成操作', 0, 'error', '报告模板不存在'),
        ('user_creation', '用户创建操作', 1, 'success', NULL),
        ('data_validation', '数据验证操作', 75, 'partial_success', '部分数据验证失败');
        
        RAISE NOTICE '插入了10条测试数据';
    ELSE
        RAISE NOTICE '表中已有 % 条记录', record_count;
    END IF;
END $$;

-- 4. 显示最终结果
SELECT COUNT(*) as total_records FROM operation_logs;
SELECT * FROM operation_logs ORDER BY created_at DESC LIMIT 5; 