-- 工作流管理系统数据库设计 (V2.0 - 增强版)
-- 日期: 2026-02-19
-- 描述: 统一管理需求、缺陷、任务、CI/CD、投产等业务模块的工作流转，增加钩子、条件判断、超时处理

USE project_management_platform;

-- ==========================================
-- 1. 工作流核心表结构
-- ==========================================

-- 1.1 工作流定义表
CREATE TABLE IF NOT EXISTS wf_workflow (
    workflow_id INT NOT NULL AUTO_INCREMENT COMMENT '工作流ID',
    workflow_name VARCHAR(100) NOT NULL COMMENT '工作流名称',
    description VARCHAR(500) DEFAULT NULL COMMENT '描述',
    business_type VARCHAR(50) NOT NULL COMMENT '业务类型(requirement/defect/task/cicd/release)',
    is_active TINYINT(1) DEFAULT 1 COMMENT '是否激活(0:否,1:是)',
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (workflow_id),
    UNIQUE KEY uk_business_type (business_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工作流定义表';

-- 1.2 状态定义表 (增加超时和编辑控制)
CREATE TABLE IF NOT EXISTS wf_state (
    state_id INT NOT NULL AUTO_INCREMENT COMMENT '状态ID',
    workflow_id INT NOT NULL COMMENT '关联工作流ID',
    state_name VARCHAR(50) NOT NULL COMMENT '状态名称',
    state_type VARCHAR(20) DEFAULT 'intermediate' COMMENT '状态类型(initial:初始, intermediate:中间, final:结束)',
    sort_order INT DEFAULT 0 COMMENT '排序',
    allow_edit TINYINT(1) DEFAULT 1 COMMENT '是否允许编辑业务数据',
    timeout_hours INT DEFAULT 0 COMMENT '超时时间(小时, 0表示不超时)',
    timeout_transition_id INT DEFAULT NULL COMMENT '超时后自动触发的流转ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (state_id),
    KEY idx_workflow_id (workflow_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工作流状态表';

-- 1.3 流转规则表 (增加条件和钩子)
CREATE TABLE IF NOT EXISTS wf_transition (
    transition_id INT NOT NULL AUTO_INCREMENT COMMENT '流转ID',
    workflow_id INT NOT NULL COMMENT '关联工作流ID',
    src_state_id INT NOT NULL COMMENT '源状态ID',
    dst_state_id INT NOT NULL COMMENT '目标状态ID',
    action_name VARCHAR(50) NOT NULL COMMENT '动作名称(如:审核通过,驳回)',
    roles_allowed JSON DEFAULT NULL COMMENT '允许执行角色的ID列表(JSON数组)',
    condition_expression JSON DEFAULT NULL COMMENT '流转条件表达式(JSON)',
    hooks_config JSON DEFAULT NULL COMMENT '钩子配置(JSON, pre_hooks/post_hooks)',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (transition_id),
    KEY idx_workflow_id (workflow_id),
    KEY idx_src_state (src_state_id),
    KEY idx_dst_state (dst_state_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工作流流转规则表';

-- 1.4 工作流实例表
CREATE TABLE IF NOT EXISTS wf_instance (
    instance_id INT NOT NULL AUTO_INCREMENT COMMENT '实例ID',
    workflow_id INT NOT NULL COMMENT '关联工作流ID',
    business_id BIGINT NOT NULL COMMENT '关联业务记录ID',
    current_state_id INT NOT NULL COMMENT '当前状态ID',
    status VARCHAR(20) DEFAULT 'active' COMMENT '实例状态(active:进行中, completed:已完成, cancelled:已取消)',
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (instance_id),
    KEY idx_business (workflow_id, business_id),
    KEY idx_current_state (current_state_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工作流实例表';

-- 1.5 流转历史表 (增加钩子日志)
CREATE TABLE IF NOT EXISTS wf_history (
    history_id INT NOT NULL AUTO_INCREMENT COMMENT '历史ID',
    instance_id INT NOT NULL COMMENT '关联实例ID',
    src_state_id INT DEFAULT NULL COMMENT '源状态ID(NULL表示初始创建)',
    dst_state_id INT NOT NULL COMMENT '目标状态ID',
    action_name VARCHAR(50) DEFAULT NULL COMMENT '执行动作',
    operator_id BIGINT DEFAULT NULL COMMENT '操作人ID',
    operator_name VARCHAR(50) DEFAULT NULL COMMENT '操作人姓名',
    comment TEXT DEFAULT NULL COMMENT '备注/意见',
    hook_execution_log JSON DEFAULT NULL COMMENT '钩子执行日志',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    PRIMARY KEY (history_id),
    KEY idx_instance_id (instance_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工作流流转历史表';


-- ==========================================
-- 2. 业务模块表结构
-- ==========================================

-- 2.1 需求管理表
CREATE TABLE IF NOT EXISTS pm_requirement (
    requirement_id BIGINT NOT NULL AUTO_INCREMENT COMMENT '需求ID',
    title VARCHAR(200) NOT NULL COMMENT '需求标题',
    description TEXT DEFAULT NULL COMMENT '详细描述',
    priority VARCHAR(20) DEFAULT 'P1' COMMENT '优先级(P0, P1, P2)',
    type VARCHAR(50) DEFAULT 'Feature' COMMENT '类型(Feature, Improvement)',
    instance_id INT DEFAULT NULL COMMENT '关联工作流实例ID',
    current_state VARCHAR(50) DEFAULT NULL COMMENT '当前状态名称(冗余字段,便于查询)',
    
    -- 审计字段
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (requirement_id),
    KEY idx_instance_id (instance_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='需求管理表';

-- 2.2 缺陷管理表
CREATE TABLE IF NOT EXISTS pm_defect (
    defect_id BIGINT NOT NULL AUTO_INCREMENT COMMENT '缺陷ID',
    title VARCHAR(200) NOT NULL COMMENT '缺陷标题',
    description TEXT DEFAULT NULL COMMENT '详细描述',
    severity VARCHAR(20) DEFAULT 'Major' COMMENT '严重程度(Critical, Major, Minor, Trivial)',
    priority VARCHAR(20) DEFAULT 'P1' COMMENT '优先级',
    assignee_id BIGINT DEFAULT NULL COMMENT '指派给(用户ID)',
    case_id BIGINT DEFAULT NULL COMMENT '关联测试用例ID',
    instance_id INT DEFAULT NULL COMMENT '关联工作流实例ID',
    current_state VARCHAR(50) DEFAULT NULL COMMENT '当前状态名称(冗余字段)',
    
    -- 审计字段
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (defect_id),
    KEY idx_instance_id (instance_id),
    KEY idx_assignee (assignee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='缺陷管理表';

-- 2.3 任务管理表
CREATE TABLE IF NOT EXISTS pm_task (
    task_id BIGINT NOT NULL AUTO_INCREMENT COMMENT '任务ID',
    parent_id BIGINT DEFAULT NULL COMMENT '父任务ID',
    title VARCHAR(200) NOT NULL COMMENT '任务标题',
    description TEXT DEFAULT NULL COMMENT '详细描述',
    start_date DATE DEFAULT NULL COMMENT '计划开始日期',
    due_date DATE DEFAULT NULL COMMENT '计划结束日期',
    assignee_id BIGINT DEFAULT NULL COMMENT '执行人ID',
    instance_id INT DEFAULT NULL COMMENT '关联工作流实例ID',
    current_state VARCHAR(50) DEFAULT NULL COMMENT '当前状态名称(冗余字段)',
    
    -- 审计字段
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (task_id),
    KEY idx_instance_id (instance_id),
    KEY idx_assignee (assignee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务管理表';

-- 2.4 CI/CD流水线记录表
CREATE TABLE IF NOT EXISTS pm_cicd (
    cicd_id BIGINT NOT NULL AUTO_INCREMENT COMMENT '流水线ID',
    pipeline_name VARCHAR(100) NOT NULL COMMENT '流水线名称',
    repo_url VARCHAR(255) DEFAULT NULL COMMENT '代码仓库地址',
    branch VARCHAR(50) DEFAULT 'main' COMMENT '分支',
    commit_id VARCHAR(64) DEFAULT NULL COMMENT '提交ID',
    build_number INT DEFAULT NULL COMMENT '构建编号',
    log_url VARCHAR(255) DEFAULT NULL COMMENT '日志链接',
    instance_id INT DEFAULT NULL COMMENT '关联工作流实例ID',
    current_state VARCHAR(50) DEFAULT NULL COMMENT '当前状态名称(冗余字段)',
    
    -- 审计字段
    create_by VARCHAR(64) DEFAULT NULL COMMENT '触发者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '触发时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (cicd_id),
    KEY idx_instance_id (instance_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='CI/CD流水线记录表';

-- 2.5 投产发布管理表
CREATE TABLE IF NOT EXISTS pm_release (
    release_id BIGINT NOT NULL AUTO_INCREMENT COMMENT '发布ID',
    version VARCHAR(50) NOT NULL COMMENT '版本号',
    title VARCHAR(200) NOT NULL COMMENT '发布标题',
    description TEXT DEFAULT NULL COMMENT '发布内容描述',
    release_date DATETIME DEFAULT NULL COMMENT '计划发布时间',
    instance_id INT DEFAULT NULL COMMENT '关联工作流实例ID',
    current_state VARCHAR(50) DEFAULT NULL COMMENT '当前状态名称(冗余字段)',
    
    -- 审计字段
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (release_id),
    KEY idx_instance_id (instance_id),
    KEY idx_version (version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='投产发布管理表';

-- ==========================================
-- 3. 初始化数据 (工作流模板)
-- ==========================================

-- 3.1 插入工作流定义
INSERT INTO wf_workflow (workflow_id, workflow_name, description, business_type) VALUES
(1, '缺陷处理流程', '标准的Bug生命周期管理', 'defect'),
(2, '需求评审流程', '需求从提出到上线的全过程', 'requirement'),
(3, '任务开发流程', '开发任务的分配与执行', 'task'),
(4, 'CI/CD发布流程', '代码构建与部署流程', 'cicd'),
(5, '投产发布流程', '版本发布与上线流程', 'release');

-- 3.2 插入状态定义 (以缺陷流程为例)
-- Defect Workflow States
INSERT INTO wf_state (workflow_id, state_name, state_type, sort_order, allow_edit, timeout_hours) VALUES
(1, '新建', 'initial', 10, 1, 0),      -- ID: 1
(1, '待分配', 'intermediate', 20, 1, 24), -- ID: 2 (超过24小时未分配可配置自动提醒)
(1, '开发中', 'intermediate', 30, 1, 0), -- ID: 3
(1, '已修复', 'intermediate', 40, 0, 48), -- ID: 4 (不允许编辑，48小时未验证自动流转?)
(1, '待验证', 'intermediate', 50, 0, 0), -- ID: 5
(1, '已关闭', 'final', 60, 0, 0),        -- ID: 6
(1, '重新打开', 'intermediate', 70, 1, 0); -- ID: 7

-- 3.3 插入流转规则 (以缺陷流程为例)
-- Defect Transitions
-- 假设角色ID: 1=Admin, 2=Frontend, 3=Backend, 4=PM, 5=QA
INSERT INTO wf_transition (workflow_id, src_state_id, dst_state_id, action_name, roles_allowed, hooks_config) VALUES
(1, 1, 2, '提交', '[1, 4, 5]', '{"post_hooks": [{"type": "notification", "template": "bug_created"}]}'),       -- 新建 -> 待分配
(1, 2, 3, '分配', '[1, 4]', NULL),          -- 待分配 -> 开发中
(1, 3, 4, '完成修复', '[1, 2, 3]', '{"post_hooks": [{"type": "notification", "template": "bug_fixed"}]}'),   -- 开发中 -> 已修复
(1, 4, 5, '提交验证', '[1, 2, 3]', NULL),   -- 已修复 -> 待验证
(1, 5, 6, '验证通过', '[1, 5]', '{"post_hooks": [{"type": "notification", "template": "bug_closed"}]}'),      -- 待验证 -> 已关闭
(1, 5, 7, '验证失败', '[1, 5]', NULL),      -- 待验证 -> 重新打开
(1, 7, 3, '再次修复', '[1, 2, 3]', NULL);   -- 重新打开 -> 开发中
