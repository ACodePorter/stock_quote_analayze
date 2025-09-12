-- 创建系统操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id SERIAL PRIMARY KEY,
    operation_type VARCHAR(100) NOT NULL,
    operation_desc TEXT,
    affected_rows INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_operation_logs_created_at ON operation_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_operation_logs_status ON operation_logs(status);
CREATE INDEX IF NOT EXISTS idx_operation_logs_operation_type ON operation_logs(operation_type);

-- 插入一些测试数据
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

-- 查看创建的表结构
\d operation_logs;

-- 查看插入的数据
SELECT * FROM operation_logs ORDER BY created_at DESC LIMIT 5; 