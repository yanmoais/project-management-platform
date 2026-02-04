
USE automation;

CREATE TABLE IF NOT EXISTS automation_execut_method_logs (
    id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    execution_id INT(11) NOT NULL COMMENT '关联automation_executions表ID',
    method_name VARCHAR(100) NOT NULL COMMENT '测试方法名称',
    log_content LONGTEXT COMMENT '日志内容',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_execution_method (execution_id, method_name),
    KEY idx_execution_id (execution_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='自动化测试方法级日志表';
