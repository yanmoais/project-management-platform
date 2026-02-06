CREATE TABLE IF NOT EXISTS `test_environment_log` (
  `log_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `env_id` bigint(20) NOT NULL COMMENT '关联测试环境ID',
  `username` varchar(30) NOT NULL COMMENT '操作用户名',
  `operation_type` varchar(20) NOT NULL COMMENT '操作类型(新增/编辑)',
  `change_content` text NOT NULL COMMENT '变更内容',
  `operation_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试环境操作日志表';
