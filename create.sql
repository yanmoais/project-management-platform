-- 项目管理平台数据库设计（优化版）
-- 版本: 2.1
-- 日期: 2026-01-19
-- 优化内容: 
-- 1. 更新部门架构（前端开发、后端开发、产品、测试）
-- 2. 完善RBAC权限模型，增加按钮级权限
-- 3. 修正表结构与数据不一致的问题
-- 4. 优化索引和关联关系

-- 创建数据库
CREATE DATABASE IF NOT EXISTS project_management_platform DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE project_management_platform;

-- 用户信息表（核心表）
CREATE TABLE IF NOT EXISTS sys_user (
    user_id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(30) NOT NULL COMMENT '用户名',
    nickname VARCHAR(30) DEFAULT NULL COMMENT '昵称',
    password VARCHAR(255) NOT NULL COMMENT '密码',
    email VARCHAR(50) DEFAULT NULL COMMENT '邮箱',
    mobile VARCHAR(11) DEFAULT NULL COMMENT '手机号',
    avatar VARCHAR(100) DEFAULT NULL COMMENT '头像',
    gender TINYINT(1) DEFAULT 0 COMMENT '性别(0:未知,1:男,2:女)',
    birthday DATE DEFAULT NULL COMMENT '生日',
    status TINYINT(1) DEFAULT 1 COMMENT '状态(0:禁用,1:启用)',
    login_ip VARCHAR(50) DEFAULT NULL COMMENT '最后登录IP',
    login_date DATETIME DEFAULT NULL COMMENT '最后登录时间',
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark VARCHAR(500) DEFAULT NULL COMMENT '备注',
    PRIMARY KEY (user_id),
    UNIQUE KEY uk_username (username),
    KEY idx_status (status),
    KEY idx_create_time (create_time)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';

-- 角色信息表（核心表）
CREATE TABLE IF NOT EXISTS sys_role (
    role_id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '角色ID',
    role_name VARCHAR(30) NOT NULL COMMENT '角色名称',
    role_key VARCHAR(100) NOT NULL COMMENT '角色权限字符串',
    role_sort INT(4) DEFAULT 0 COMMENT '显示顺序',
    data_scope TINYINT(1) DEFAULT 1 COMMENT '数据范围(1:全部,2:自定义,3:本部门,4:本部门及以下,5:仅本人)',
    status TINYINT(1) DEFAULT 1 COMMENT '状态(0:禁用,1:启用)',
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark VARCHAR(500) DEFAULT NULL COMMENT '备注',
    PRIMARY KEY (role_id),
    UNIQUE KEY uk_role_name (role_name),
    UNIQUE KEY uk_role_key (role_key),
    KEY idx_status (status)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COMMENT='角色信息表';

-- 岗位信息表（独立表）
CREATE TABLE IF NOT EXISTS sys_post (
    post_id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '岗位ID',
    post_code VARCHAR(64) NOT NULL COMMENT '岗位编码',
    post_name VARCHAR(50) NOT NULL COMMENT '岗位名称',
    post_sort INT(4) DEFAULT 0 COMMENT '显示顺序',
    status TINYINT(1) DEFAULT 1 COMMENT '状态(0:禁用,1:启用)',
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark VARCHAR(500) DEFAULT NULL COMMENT '备注',
    PRIMARY KEY (post_id),
    UNIQUE KEY uk_post_code (post_code),
    UNIQUE KEY uk_post_name (post_name),
    KEY idx_status (status)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COMMENT='岗位信息表';

-- 部门表（树形结构）
CREATE TABLE IF NOT EXISTS sys_dept (
    dept_id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '部门ID',
    parent_id BIGINT(20) DEFAULT 0 COMMENT '父部门ID',
    dept_name VARCHAR(30) NOT NULL COMMENT '部门名称',
    dept_code VARCHAR(64) DEFAULT NULL COMMENT '部门编码',
    leader VARCHAR(20) DEFAULT NULL COMMENT '负责人',
    phone VARCHAR(11) DEFAULT NULL COMMENT '联系电话',
    email VARCHAR(50) DEFAULT NULL COMMENT '邮箱',
    dept_sort INT(4) DEFAULT 0 COMMENT '显示顺序',
    status TINYINT(1) DEFAULT 1 COMMENT '状态(0:禁用,1:启用)',
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark VARCHAR(500) DEFAULT NULL COMMENT '备注',
    PRIMARY KEY (dept_id),
    KEY idx_parent_id (parent_id),
    KEY idx_dept_sort (dept_sort),
    KEY idx_status (status)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COMMENT='部门表';

-- 菜单权限表（树形结构）
CREATE TABLE IF NOT EXISTS sys_menu (
    menu_id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '菜单ID',
    parent_id BIGINT(20) DEFAULT 0 COMMENT '父菜单ID',
    menu_name VARCHAR(50) NOT NULL COMMENT '菜单名称',
    menu_type CHAR(1) DEFAULT NULL COMMENT '菜单类型(M:目录,C:菜单,F:按钮)',
    path VARCHAR(200) DEFAULT NULL COMMENT '路由路径',
    component VARCHAR(255) DEFAULT NULL COMMENT '组件路径',
    query VARCHAR(255) DEFAULT NULL COMMENT '路由参数',
    is_frame TINYINT(1) DEFAULT 1 COMMENT '是否为外链(0:否,1:是)',
    is_cache TINYINT(1) DEFAULT 0 COMMENT '是否缓存(0:否,1:是)',
    menu_icon VARCHAR(50) DEFAULT NULL COMMENT '菜单图标',
    menu_key VARCHAR(100) DEFAULT NULL COMMENT '权限标识',
    menu_sort INT(4) DEFAULT 0 COMMENT '显示顺序',
    status TINYINT(1) DEFAULT 1 COMMENT '状态(0:禁用,1:启用)',
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark VARCHAR(500) DEFAULT NULL COMMENT '备注',
    PRIMARY KEY (menu_id),
    KEY idx_parent_id (parent_id),
    KEY idx_menu_sort (menu_sort),
    KEY idx_menu_type (menu_type),
    KEY idx_status (status)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COMMENT='菜单权限表';

-- 用户-部门关联表（降低耦合）
CREATE TABLE IF NOT EXISTS sys_user_dept (
    id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT(20) NOT NULL COMMENT '用户ID',
    dept_id BIGINT(20) NOT NULL COMMENT '部门ID',
    is_primary TINYINT(1) DEFAULT 0 COMMENT '是否主部门(0:否,1:是)',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_dept (user_id, dept_id),
    KEY idx_user_id (user_id),
    KEY idx_dept_id (dept_id)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8mb4 COMMENT='用户部门关联表';

-- 用户-岗位关联表（降低耦合）
CREATE TABLE IF NOT EXISTS sys_user_post (
    id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT(20) NOT NULL COMMENT '用户ID',
    post_id BIGINT(20) NOT NULL COMMENT '岗位ID',
    is_primary TINYINT(1) DEFAULT 0 COMMENT '是否主岗位(0:否,1:是)',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_post (user_id, post_id),
    KEY idx_user_id (user_id),
    KEY idx_post_id (post_id)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8mb4 COMMENT='用户岗位关联表';

-- 用户-角色关联表（权限核心）
CREATE TABLE IF NOT EXISTS sys_user_role (
    id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT(20) NOT NULL COMMENT '用户ID',
    role_id BIGINT(20) NOT NULL COMMENT '角色ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_role (user_id, role_id),
    KEY idx_user_id (user_id),
    KEY idx_role_id (role_id)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';

-- 角色-菜单关联表（权限核心）
CREATE TABLE IF NOT EXISTS sys_role_menu (
    id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    role_id BIGINT(20) NOT NULL COMMENT '角色ID',
    menu_id BIGINT(20) NOT NULL COMMENT '菜单ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_role_menu (role_id, menu_id),
    KEY idx_role_id (role_id),
    KEY idx_menu_id (menu_id)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8mb4 COMMENT='角色菜单关联表';

-- 操作日志记录表（独立表，不影响核心业务）
CREATE TABLE IF NOT EXISTS sys_oper_log (
    oper_id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '日志ID',
    title VARCHAR(100) DEFAULT '' COMMENT '操作模块',
    business_type TINYINT(4) DEFAULT 0 COMMENT '业务类型(0:其他,1:新增,2:修改,3:删除,4:查询,5:导入,6:导出)',
    method VARCHAR(100) DEFAULT '' COMMENT '方法名',
    request_method VARCHAR(10) DEFAULT '' COMMENT '请求方式',
    operator_type TINYINT(4) DEFAULT 0 COMMENT '操作类型(0:其他,1:后台用户,2:手机端用户)',
    oper_name VARCHAR(50) DEFAULT '' COMMENT '操作人员',
    dept_name VARCHAR(50) DEFAULT '' COMMENT '部门名称',
    oper_url VARCHAR(255) DEFAULT '' COMMENT '请求URL',
    oper_ip VARCHAR(50) DEFAULT '' COMMENT '操作IP',
    oper_location VARCHAR(255) DEFAULT '' COMMENT '操作地点',
    oper_param VARCHAR(2000) DEFAULT '' COMMENT '请求参数',
    json_result VARCHAR(2000) DEFAULT '' COMMENT '返回参数',
    status TINYINT(4) DEFAULT 0 COMMENT '操作状态(0:失败,1:成功)',
    error_msg VARCHAR(500) DEFAULT '' COMMENT '错误消息',
    oper_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    PRIMARY KEY (oper_id),
    KEY idx_oper_time (oper_time),
    KEY idx_oper_name (oper_name),
    KEY idx_business_type (business_type),
    KEY idx_status (status)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8mb4 COMMENT='操作日志记录表';

-- 用户信息详情表（扩展表，通过user_id关联）
CREATE TABLE IF NOT EXISTS app_user_info (
    user_info_id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '用户详情ID',
    user_id BIGINT(20) NOT NULL COMMENT '用户ID',
    real_name VARCHAR(50) DEFAULT NULL COMMENT '真实姓名',
    id_card VARCHAR(20) DEFAULT NULL COMMENT '身份证号',
    nation VARCHAR(20) DEFAULT NULL COMMENT '民族',
    education VARCHAR(20) DEFAULT NULL COMMENT '学历',
    entry_date DATE DEFAULT NULL COMMENT '入职日期',
    emergency_contact VARCHAR(50) DEFAULT NULL COMMENT '紧急联系人',
    emergency_phone VARCHAR(20) DEFAULT NULL COMMENT '紧急联系电话',
    position VARCHAR(50) DEFAULT NULL COMMENT '职位',
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark VARCHAR(500) DEFAULT NULL COMMENT '备注',
    PRIMARY KEY (user_info_id),
    UNIQUE KEY uk_user_id (user_id),
    KEY idx_user_id (user_id)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8mb4 COMMENT='用户信息详情表';

-- 用户登录记录表（日志表，通过user_id关联）
CREATE TABLE IF NOT EXISTS app_user_log (
    log_id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '日志ID',
    user_id BIGINT(20) NOT NULL COMMENT '用户ID',
    username VARCHAR(30) DEFAULT NULL COMMENT '用户名',
    login_ip VARCHAR(50) DEFAULT NULL COMMENT '登录IP',
    login_location VARCHAR(255) DEFAULT NULL COMMENT '登录地点',
    browser VARCHAR(50) DEFAULT NULL COMMENT '浏览器',
    os VARCHAR(50) DEFAULT NULL COMMENT '操作系统',
    device VARCHAR(50) DEFAULT NULL COMMENT '设备类型',
    login_type TINYINT(4) DEFAULT 1 COMMENT '登录类型(1:密码登录,2:手机登录,3:扫码登录,4:第三方登录)',
    login_status TINYINT(4) DEFAULT 1 COMMENT '登录状态(0:失败,1:成功)',
    error_msg VARCHAR(255) DEFAULT NULL COMMENT '错误信息',
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    logout_time DATETIME DEFAULT NULL COMMENT '登出时间',
    online_duration INT(11) DEFAULT 0 COMMENT '在线时长(秒)',
    PRIMARY KEY (log_id),
    KEY idx_user_id (user_id),
    KEY idx_login_time (login_time),
    KEY idx_login_status (login_status),
    KEY idx_username (username)
) ENGINE=InnoDB AUTO_INCREMENT=10000 DEFAULT CHARSET=utf8mb4 COMMENT='用户登录记录表';

-- 系统配置表（新增，用于存储系统参数）
CREATE TABLE IF NOT EXISTS sys_config (
    config_id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '配置ID',
    config_key VARCHAR(100) NOT NULL COMMENT '配置键',
    config_value VARCHAR(2000) NOT NULL COMMENT '配置值',
    config_type TINYINT(4) DEFAULT 0 COMMENT '配置类型(0:系统,1:业务)',
    status TINYINT(4) DEFAULT 1 COMMENT '状态(0:禁用,1:启用)',
    remark VARCHAR(500) DEFAULT NULL COMMENT '备注',
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (config_id),
    UNIQUE KEY uk_config_key (config_key),
    KEY idx_config_type (config_type),
    KEY idx_status (status)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- 数据字典表（新增，用于存储字典数据）
CREATE TABLE IF NOT EXISTS sys_dict_type (
    dict_id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '字典ID',
    dict_name VARCHAR(100) NOT NULL COMMENT '字典名称',
    dict_type VARCHAR(100) NOT NULL COMMENT '字典类型',
    status TINYINT(4) DEFAULT 1 COMMENT '状态(0:禁用,1:启用)',
    remark VARCHAR(500) DEFAULT NULL COMMENT '备注',
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (dict_id),
    UNIQUE KEY uk_dict_type (dict_type),
    KEY idx_status (status)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COMMENT='数据字典类型表';

CREATE TABLE IF NOT EXISTS sys_dict_data (
    dict_data_id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '字典数据ID',
    dict_id BIGINT(20) NOT NULL COMMENT '字典类型ID',
    dict_label VARCHAR(100) NOT NULL COMMENT '字典标签',
    dict_value VARCHAR(100) NOT NULL COMMENT '字典值',
    dict_sort INT(4) DEFAULT 0 COMMENT '显示顺序',
    status TINYINT(4) DEFAULT 1 COMMENT '状态(0:禁用,1:启用)',
    remark VARCHAR(500) DEFAULT NULL COMMENT '备注',
    create_by VARCHAR(64) DEFAULT NULL COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (dict_data_id),
    KEY idx_dict_id (dict_id),
    KEY idx_dict_value (dict_value),
    KEY idx_status (status)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8mb4 COMMENT='数据字典数据表';

-- 索引优化
CREATE INDEX idx_sys_user_dept_user_id ON sys_user_dept(user_id);
CREATE INDEX idx_sys_user_dept_dept_id ON sys_user_dept(dept_id);
CREATE INDEX idx_sys_user_post_user_id ON sys_user_post(user_id);
CREATE INDEX idx_sys_user_post_post_id ON sys_user_post(post_id);
CREATE INDEX idx_sys_user_role_user_id ON sys_user_role(user_id);
CREATE INDEX idx_sys_user_role_role_id ON sys_user_role(role_id);
CREATE INDEX idx_sys_role_menu_role_id ON sys_role_menu(role_id);
CREATE INDEX idx_sys_role_menu_menu_id ON sys_role_menu(menu_id);
CREATE INDEX idx_app_user_info_user_id ON app_user_info(user_id);
CREATE INDEX idx_app_user_log_user_id ON app_user_log(user_id);
CREATE INDEX idx_app_user_log_login_time ON app_user_log(login_time);

-- 插入初始数据
-- 1. 插入默认角色
INSERT INTO sys_role (role_id, role_name, role_key, role_sort, data_scope, status, remark) 
VALUES 
(1, '超级管理员', 'admin', 1, 1, 1, '系统默认角色'),
(2, '前端工程师', 'frontend', 2, 5, 1, '前端开发人员'),
(3, '后端工程师', 'backend', 3, 5, 1, '后端开发人员'),
(4, '产品经理', 'pm', 4, 3, 1, '产品管理人员'),
(5, '测试工程师', 'qa', 5, 5, 1, '测试人员');

-- 2. 插入默认部门
INSERT INTO sys_dept (dept_id, parent_id, dept_name, dept_code, leader, dept_sort, status, remark) 
VALUES 
(1, 0, '总公司', '001', 'CEO', 1, 1, '系统默认部门'),
(2, 1, '产品部', '001001', '产品主管', 2, 1, '产品设计与规划'),
(3, 1, '研发部', '001002', 'CTO', 3, 1, '技术研发中心'),
(4, 3, '前端开发组', '001002001', '前端主管', 1, 1, 'Web与移动端开发'),
(5, 3, '后端开发组', '001002002', '后端主管', 2, 1, '服务与架构开发'),
(6, 3, '测试组', '001002003', '测试主管', 3, 1, '质量保证');

-- 3. 插入默认岗位
INSERT INTO sys_post (post_id, post_code, post_name, post_sort, status, remark) 
VALUES 
(1, '001', '技术总监', 1, 1, '技术负责人'),
(2, '002', '高级开发工程师', 2, 1, '核心开发人员'),
(3, '003', '中级开发工程师', 3, 1, '业务开发人员'),
(4, '004', '产品经理', 4, 1, '产品规划人员'),
(5, '005', '测试工程师', 5, 1, '软件测试人员');

-- 4. 插入默认用户
INSERT INTO sys_user (user_id, username, nickname, password, email, mobile, status, remark) 
VALUES 
(1, 'admin', '系统管理员', '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2', 'admin@example.com', '13800138000', 1, '超级管理员'),
(2, 'zhangsan', '张三', '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2', 'zhangsan@example.com', '13800138001', 1, '前端开发'),
(3, 'lisi', '李四', '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2', 'lisi@example.com', '13800138002', 1, '后端开发'),
(4, 'wangwu', '王五', '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2', 'wangwu@example.com', '13800138003', 1, '产品经理'),
(5, 'zhaoliu', '赵六', '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2', 'zhaoliu@example.com', '13800138004', 1, '测试工程师');

-- 5. 插入用户部门关联
INSERT INTO sys_user_dept (user_id, dept_id, is_primary) VALUES 
(1, 1, 1),  -- 管理员属于总公司
(2, 4, 1),  -- 张三属于前端开发组
(3, 5, 1),  -- 李四属于后端开发组
(4, 2, 1),  -- 王五属于产品部
(5, 6, 1);  -- 赵六属于测试组

-- 6. 插入用户岗位关联
INSERT INTO sys_user_post (user_id, post_id, is_primary) VALUES 
(1, 1, 1),  -- 管理员是技术总监
(2, 2, 1),  -- 张三是高级开发工程师
(3, 2, 1),  -- 李四是高级开发工程师
(4, 4, 1),  -- 王五是产品经理
(5, 5, 1);  -- 赵六是测试工程师

-- 7. 插入用户角色关联
INSERT INTO sys_user_role (user_id, role_id) VALUES 
(1, 1),  -- 管理员拥有超级管理员角色
(2, 2),  -- 张三拥有前端工程师角色
(3, 3),  -- 李四拥有后端工程师角色
(4, 4),  -- 王五拥有产品经理角色
(5, 5);  -- 赵六拥有测试工程师角色

-- 8. 插入默认菜单 (包含目录、菜单、按钮)
INSERT INTO sys_menu (menu_id, parent_id, menu_name, menu_type, path, component, is_frame, is_cache, menu_icon, menu_key, menu_sort, status, remark) 
VALUES 
-- 系统管理模块
(1, 0, '系统管理', 'M', 'system', '', 0, 0, 'el-icon-setting', '', 1, 1, '系统管理目录'),
-- 用户管理及按钮权限
(2, 1, '用户管理', 'C', 'user', 'system/user/index', 0, 0, 'el-icon-user', 'system:user:list', 1, 1, '用户管理菜单'),

-- 自动化测试相关表结构

-- 产品表
CREATE TABLE IF NOT EXISTS projects (
    id INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    product_package_name VARCHAR(255) NOT NULL COMMENT '产品包名',
    product_address TEXT NOT NULL COMMENT '产品地址',
    product_id VARCHAR(255) DEFAULT NULL COMMENT '产品ID',
    is_automated VARCHAR(10) NOT NULL COMMENT '是否自动化(已接入/待接入)',
    version_number VARCHAR(100) DEFAULT NULL COMMENT '版本号',
    product_image TEXT DEFAULT NULL COMMENT '产品图片URL',
    system_type VARCHAR(100) DEFAULT NULL COMMENT '系统类型',
    product_type VARCHAR(100) DEFAULT NULL COMMENT '产品类型',
    environment VARCHAR(100) DEFAULT NULL COMMENT '环境',
    remarks TEXT DEFAULT NULL COMMENT '备注',
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品表';

-- 自动化测试案例表
CREATE TABLE IF NOT EXISTS automation_projects (
    id INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    process_name VARCHAR(255) NOT NULL COMMENT '流程名称',
    product_ids TEXT NOT NULL COMMENT '关联产品ID集合',
    system VARCHAR(100) DEFAULT NULL COMMENT '系统',
    product_type VARCHAR(100) DEFAULT NULL COMMENT '产品类型',
    environment VARCHAR(100) DEFAULT NULL COMMENT '环境',
    product_address TEXT DEFAULT NULL COMMENT '产品地址',
    project_id INT DEFAULT NULL COMMENT '关联Project表ID',
    product_package_names TEXT DEFAULT NULL COMMENT '产品包名集合',
    test_steps TEXT DEFAULT NULL COMMENT '测试步骤配置',
    tab_switch_config TEXT DEFAULT NULL COMMENT 'Tab切换配置',
    assertion_config TEXT DEFAULT NULL COMMENT '断言配置',
    screenshot_config TEXT DEFAULT NULL COMMENT '截图配置',
    status VARCHAR(50) DEFAULT '待执行' COMMENT '执行状态',
    created_by VARCHAR(100) DEFAULT 'admin' COMMENT '创建人',
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='自动化测试案例表';

-- 自动化测试文件表
CREATE TABLE IF NOT EXISTS project_files (
    id INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    project_id INT NOT NULL COMMENT '关联ProjectID',
    project_name VARCHAR(255) NOT NULL COMMENT '项目名称',
    file_name VARCHAR(255) NOT NULL COMMENT '文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
    file_type VARCHAR(20) DEFAULT 'py' COMMENT '文件类型',
    is_active TINYINT(1) DEFAULT 1 COMMENT '是否激活',
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='自动化测试文件表';

-- 枚举值表
CREATE TABLE IF NOT EXISTS enum_values (
    id INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    field_name VARCHAR(100) NOT NULL COMMENT '字段名称',
    field_value VARCHAR(100) NOT NULL COMMENT '字段值',
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='枚举值表';

(100, 2, '用户查询', 'F', '', '', 0, 0, '', 'system:user:query', 1, 1, '用户查询按钮'),
(101, 2, '用户新增', 'F', '', '', 0, 0, '', 'system:user:add', 2, 1, '用户新增按钮'),
(102, 2, '用户修改', 'F', '', '', 0, 0, '', 'system:user:edit', 3, 1, '用户修改按钮'),
(103, 2, '用户删除', 'F', '', '', 0, 0, '', 'system:user:remove', 4, 1, '用户删除按钮'),
(104, 2, '重置密码', 'F', '', '', 0, 0, '', 'system:user:resetPwd', 5, 1, '重置密码按钮'),
-- 角色管理及按钮权限
(3, 1, '角色管理', 'C', 'role', 'system/role/index', 0, 0, 'el-icon-rank', 'system:role:list', 2, 1, '角色管理菜单'),
(105, 3, '角色查询', 'F', '', '', 0, 0, '', 'system:role:query', 1, 1, '角色查询按钮'),
(106, 3, '角色新增', 'F', '', '', 0, 0, '', 'system:role:add', 2, 1, '角色新增按钮'),
(107, 3, '角色修改', 'F', '', '', 0, 0, '', 'system:role:edit', 3, 1, '角色修改按钮'),
(108, 3, '角色删除', 'F', '', '', 0, 0, '', 'system:role:remove', 4, 1, '角色删除按钮'),
-- 菜单管理及按钮权限
(4, 1, '菜单管理', 'C', 'menu', 'system/menu/index', 0, 0, 'el-icon-menu', 'system:menu:list', 3, 1, '菜单管理菜单'),
(109, 4, '菜单查询', 'F', '', '', 0, 0, '', 'system:menu:query', 1, 1, '菜单查询按钮'),
(110, 4, '菜单新增', 'F', '', '', 0, 0, '', 'system:menu:add', 2, 1, '菜单新增按钮'),
(111, 4, '菜单修改', 'F', '', '', 0, 0, '', 'system:menu:edit', 3, 1, '菜单修改按钮'),
(112, 4, '菜单删除', 'F', '', '', 0, 0, '', 'system:menu:remove', 4, 1, '菜单删除按钮'),
-- 部门管理及按钮权限
(5, 1, '部门管理', 'C', 'dept', 'system/dept/index', 0, 0, 'el-icon-office-building', 'system:dept:list', 4, 1, '部门管理菜单'),
(113, 5, '部门查询', 'F', '', '', 0, 0, '', 'system:dept:query', 1, 1, '部门查询按钮'),
(114, 5, '部门新增', 'F', '', '', 0, 0, '', 'system:dept:add', 2, 1, '部门新增按钮'),
(115, 5, '部门修改', 'F', '', '', 0, 0, '', 'system:dept:edit', 3, 1, '部门修改按钮'),
(116, 5, '部门删除', 'F', '', '', 0, 0, '', 'system:dept:remove', 4, 1, '部门删除按钮'),
-- 岗位管理
(6, 1, '岗位管理', 'C', 'post', 'system/post/index', 0, 0, 'el-icon-position', 'system:post:list', 5, 1, '岗位管理菜单'),

-- 监控中心
(7, 0, '监控中心', 'M', 'monitor', '', 0, 0, 'el-icon-data-line', '', 2, 1, '监控中心目录'),
(8, 7, '操作日志', 'C', 'operlog', 'monitor/operlog/index', 0, 0, 'el-icon-document', 'monitor:operlog:list', 1, 1, '操作日志菜单'),
(9, 7, '登录日志', 'C', 'loginlog', 'monitor/loginlog/index', 0, 0, 'el-icon-finished', 'monitor:loginlog:list', 2, 1, '登录日志菜单');

-- 9. 插入角色菜单关联
INSERT INTO sys_role_menu (role_id, menu_id) VALUES 
-- 超级管理员拥有所有权限（这里仅列出部分示例，实际上超级管理员通常在代码中跳过权限检查）
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9),
-- 插入按钮权限关联...
(1, 100), (1, 101), (1, 102), (1, 103), (1, 104), -- 用户按钮
(1, 105), (1, 106), (1, 107), (1, 108),         -- 角色按钮
(1, 109), (1, 110), (1, 111), (1, 112),         -- 菜单按钮
(1, 113), (1, 114), (1, 115), (1, 116),         -- 部门按钮

-- 前端工程师拥有部分权限（示例）
(2, 7), (2, 8), (2, 9), -- 监控中心
(2, 1), (2, 4),         -- 系统管理、菜单管理（只读）
(2, 109),               -- 菜单查询按钮

-- 后端工程师 (同前端)
(3, 7), (3, 8), (3, 9),
(3, 1), (3, 4),
(3, 109),

-- 产品经理 (查看用户、部门)
(4, 1), (4, 2), (4, 5), -- 系统管理、用户管理、部门管理
(4, 100), (4, 113),     -- 用户查询、部门查询

-- 测试工程师 (查看所有)
(5, 7), (5, 8), (5, 9), -- 监控中心
(5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), -- 系统管理所有菜单
(5, 100), (5, 105), (5, 109), (5, 113); -- 所有查询按钮

-- 10. 插入用户详情信息
INSERT INTO app_user_info (user_id, real_name, id_card, nation, education, entry_date, position, emergency_contact, emergency_phone) 
VALUES 
(1, '系统管理员', '110101199001011234', '汉族', '本科', '2020-01-01', '技术总监', '紧急联系人', '13900139000'),
(2, '张三', '110101199201011234', '汉族', '本科', '2021-03-15', '高级开发工程师', '张父', '13900139001'),
(3, '李四', '110101199301011234', '汉族', '硕士', '2022-06-20', '高级开发工程师', '李母', '13900139002'),
(4, '王五', '110101199401011234', '汉族', '本科', '2023-02-10', '产品经理', '王父', '13900139003'),
(5, '赵六', '110101199501011234', '汉族', '本科', '2023-05-18', '测试工程师', '赵母', '13900139004');

-- 11. 插入系统配置
INSERT INTO sys_config (config_key, config_value, config_type, status, remark) VALUES 
('sys.name', '项目管理平台', 0, 1, '系统名称'),
('sys.version', '1.0.0', 0, 1, '系统版本'),
('sys.copyright', '© 2025 项目管理平台', 0, 1, '版权信息'),
('login.fail.max_count', '5', 0, 1, '登录失败最大次数'),
('login.fail.lock_time', '30', 0, 1, '登录失败锁定时间(分钟)');

-- 12. 插入数据字典
INSERT INTO sys_dict_type (dict_name, dict_type, status, remark) VALUES 
('用户状态', 'sys_user_status', 1, '用户状态字典'),
('菜单类型', 'sys_menu_type', 1, '菜单类型字典'),
('业务类型', 'sys_business_type', 1, '业务操作类型字典'),
('登录类型', 'sys_login_type', 1, '登录方式类型字典');

INSERT INTO sys_dict_data (dict_id, dict_label, dict_value, dict_sort, status) VALUES 
(1, '启用', '1', 1, 1),
(1, '禁用', '0', 2, 1),
(3, '目录', 'M', 1, 1),
(2, '菜单', 'C', 2, 1),
(2, '按钮', 'F', 3, 1),
(3, '新增', '1', 1, 1),
(3, '修改', '2', 2, 1),
(3, '删除', '3', 3, 1),
(3, '查询', '4', 4, 1),
(4, '密码登录', '1', 1, 1),
(4, '手机登录', '2', 2, 1),
(4, '扫码登录', '3', 3, 1);

-- 测试环境管理
CREATE TABLE IF NOT EXISTS test_environment (
                                                env_id BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '环境ID',
                                                project_name VARCHAR(100) NOT NULL COMMENT '所属项目名',
    env_name VARCHAR(50) NOT NULL COMMENT '环境名称(SIT/UAT/PERF)',
    env_type VARCHAR(20) NOT NULL COMMENT '环境类型(SIT/UAT/PERF)',
    env_url VARCHAR(255) NOT NULL COMMENT '测试地址',
    db_host VARCHAR(100) COMMENT '数据库主',
                                                db_port VARCHAR(10) COMMENT '数据库端',
    db_user VARCHAR(50) COMMENT '数据库用户名',
    db_password VARCHAR(100) COMMENT '数据库密',
                                                account VARCHAR(50) COMMENT '测试账号',
                                                password VARCHAR(100) COMMENT '测试密码',
                                                status VARCHAR(20) DEFAULT 'Active' COMMENT '状态',
                                                remark VARCHAR(500) COMMENT '备注',
                                                create_by VARCHAR(64) DEFAULT NULL COMMENT '创建',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(64) DEFAULT NULL COMMENT '更新',
                                                update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                                                PRIMARY KEY (env_id),
                                                KEY idx_project_name (project_name),
                                                KEY idx_env_type (env_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试环境管理';

-- 插入一些测试数
INSERT INTO test_environment (project_name, env_name, env_type, env_url, db_host, db_port, db_user, db_password, account, password, status) VALUES
('电商中台系统', 'SIT-01', 'SIT', 'http://sit-mall.company.com', '192.168.1.101', '3306', 'root', 'root_pwd', 'admin', 'admin123', 'Active'),
('电商中台系统', 'UAT-01', 'UAT', 'http://uat-mall.company.com', '192.168.1.102', '3306', 'admin', 'admin_pwd', 'test_user', 'test1234', 'Active'),
('支付网关', 'PERF-01', 'PERF', 'http://perf-pay.company.com', '192.168.1.201', '5432', 'postgres', 'pg_pwd', 'perf_user', 'perf1234', 'Maintenance');


-- WEB自动化表结构，Database: automation
CREATE TABLE `automation_executions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int DEFAULT NULL,
  `process_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `product_ids` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `system` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `environment` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_address` text COLLATE utf8mb4_unicode_ci,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_time` timestamp NULL DEFAULT NULL,
  `end_time` timestamp NULL DEFAULT NULL,
  `log_message` text COLLATE utf8mb4_unicode_ci,
  `detailed_log` longtext COLLATE utf8mb4_unicode_ci,
  `executed_by` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT 'admin',
  `cancel_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `log_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `task_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Celery任务ID',
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `automation_executions_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `automation_projects` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=105 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `automation_projects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `process_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `product_ids` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `system` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `environment` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_address` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `project_id` int DEFAULT NULL,
  `product_package_names` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `test_steps` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `tab_switch_config` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `assertion_config` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `screenshot_config` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '待执行',
  `created_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'admin',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=140 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `enum_values` (
  `id` int NOT NULL AUTO_INCREMENT,
  `field_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `field_value` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_field_value` (`field_name`,`field_value`)
) ENGINE=InnoDB AUTO_INCREMENT=6891 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_file_mappings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `process_name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_id` (`project_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_files` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL,
  `project_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_path` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'py',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_project_file` (`project_id`,`file_name`)
) ENGINE=InnoDB AUTO_INCREMENT=94 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `projects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_package_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `product_address` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `product_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_automated` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `version_number` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_image` text COLLATE utf8mb4_unicode_ci,
  `system_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `environment` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `remarks` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 产品操作日志表
CREATE TABLE IF NOT EXISTS `projects_log` (
  `log_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `project_id` int(11) NOT NULL COMMENT '关联产品ID',
  `user_id` bigint(20) NOT NULL COMMENT '操作用户ID',
  `username` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '操作用户名',
  `operation_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '操作类型(新增/编辑)',
  `change_content` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '变更内容',
  `operation_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  `operation_ip` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '操作IP',
  PRIMARY KEY (`log_id`),
  KEY `idx_project_id` (`project_id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品操作日志表';

