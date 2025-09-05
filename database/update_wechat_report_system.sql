-- 每日股票报告系统数据库更新脚本

-- 1. 添加用户微信绑定字段
ALTER TABLE users ADD COLUMN wechat_user_id VARCHAR(100) NULL COMMENT '企业微信用户ID';

-- 2. 创建索引
CREATE INDEX idx_users_wechat_user_id ON users(wechat_user_id);

-- 3. 创建报告发送日志表
CREATE TABLE IF NOT EXISTS report_send_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    report_type VARCHAR(50) NOT NULL COMMENT '报告类型: daily_summary, daily_detailed',
    file_path VARCHAR(500) NOT NULL COMMENT '报告文件路径',
    send_status ENUM('success', 'failed') NOT NULL COMMENT '发送状态',
    error_message TEXT NULL COMMENT '错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报告发送日志表';

-- 4. 创建用户报告配置表
CREATE TABLE IF NOT EXISTS user_report_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    report_type VARCHAR(50) NOT NULL DEFAULT 'daily_summary' COMMENT '报告类型',
    send_time_morning VARCHAR(10) DEFAULT '09:30' COMMENT '上午发送时间',
    send_time_evening VARCHAR(10) DEFAULT '15:30' COMMENT '下午发送时间',
    is_active TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户报告配置表';

-- 5. 为现有用户创建默认报告配置
INSERT INTO user_report_config (user_id, report_type, send_time_morning, send_time_evening, is_active)
SELECT user_id, 'daily_summary', '09:30', '15:30', 1
FROM users 
WHERE is_active = 1
ON DUPLICATE KEY UPDATE 
    report_type = VALUES(report_type),
    send_time_morning = VALUES(send_time_morning),
    send_time_evening = VALUES(send_time_evening),
    is_active = VALUES(is_active);
