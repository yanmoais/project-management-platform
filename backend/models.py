from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SysUser(db.Model):
    __tablename__ = 'sys_user'
    user_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    nickname = db.Column(db.String(30))
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(50))
    mobile = db.Column(db.String(11))
    avatar = db.Column(db.String(100))
    gender = db.Column(db.Integer, default=0) # 0:unknown, 1:male, 2:female
    birthday = db.Column(db.Date)
    status = db.Column(db.Integer, default=1) # 0:disabled, 1:enabled
    login_ip = db.Column(db.String(50))
    login_date = db.Column(db.DateTime)
    create_by = db.Column(db.String(64))
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_by = db.Column(db.String(64))
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    remark = db.Column(db.String(500))

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'nickname': self.nickname,
            'email': self.email,
            'mobile': self.mobile,
            'avatar': self.avatar,
            'gender': self.gender,
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None
        }

class AppUserLog(db.Model):
    __tablename__ = 'app_user_log'
    log_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    username = db.Column(db.String(30))
    login_ip = db.Column(db.String(50))
    login_location = db.Column(db.String(255))
    browser = db.Column(db.String(50))
    os = db.Column(db.String(50))
    device = db.Column(db.String(50))
    login_type = db.Column(db.Integer, default=1) # 1:password, 2:mobile, 3:scan, 4:third-party
    login_status = db.Column(db.Integer, default=1) # 0:fail, 1:success
    error_msg = db.Column(db.String(255))
    login_time = db.Column(db.DateTime, default=datetime.now)
    logout_time = db.Column(db.DateTime)
    online_duration = db.Column(db.Integer, default=0)

class TestEnvironment(db.Model):
    __tablename__ = 'test_environment'
    env_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String(100), nullable=False)
    env_name = db.Column(db.String(50), nullable=False)
    env_type = db.Column(db.String(20), nullable=False)
    env_url = db.Column(db.String(255), nullable=False)
    db_type = db.Column(db.String(20))
    db_host = db.Column(db.String(100))
    db_port = db.Column(db.String(10))
    db_user = db.Column(db.String(50))
    db_password = db.Column(db.String(100))
    account = db.Column(db.String(50))
    password = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Active')
    create_by = db.Column(db.String(64))

    def to_dict(self):
        return {
            'env_id': self.env_id,
            'project_name': self.project_name,
            'env_name': self.env_name,
            'env_type': self.env_type,
            'env_url': self.env_url,
            'db_type': self.db_type,
            'db_host': self.db_host,
            'db_port': self.db_port,
            'db_user': self.db_user,
            'db_password': self.db_password,
            'account': self.account,
            'password': self.password,
            'status': self.status,
            'create_by': self.create_by
        }

class TestEnvironmentLog(db.Model):
    """
    测试环境操作日志表 (test_environment_log)
    用于记录测试环境新增/编辑操作记录
    """
    __tablename__ = 'test_environment_log'
    log_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='日志ID')
    env_id = db.Column(db.BigInteger, nullable=False, comment='关联测试环境ID')
    username = db.Column(db.String(30), nullable=False, comment='操作用户名')
    operation_type = db.Column(db.String(20), nullable=False, comment='操作类型(新增/编辑)')
    change_content = db.Column(db.Text, nullable=False, comment='变更内容')
    operation_time = db.Column(db.DateTime, default=datetime.now, comment='操作时间')

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'env_id': self.env_id,
            'username': self.username,
            'operation_type': self.operation_type,
            'change_content': self.change_content,
            'operation_time': self.operation_time.strftime('%Y-%m-%d %H:%M:%S') if self.operation_time else None
        }

class Project(db.Model):
    """
    产品表 (projects)
    用于存储产品基本信息
    """
    __bind_key__ = 'automation'
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    product_package_name = db.Column(db.String(255), nullable=False, comment='产品包名')
    product_address = db.Column(db.Text, nullable=False, comment='产品地址')
    product_id = db.Column(db.String(255), comment='产品ID')
    is_automated = db.Column(db.String(10), nullable=False, comment='是否自动化(已接入/待接入)')
    version_number = db.Column(db.String(100), comment='版本号')
    product_image = db.Column(db.Text, comment='产品图片URL')
    system_type = db.Column(db.String(100), comment='系统类型')
    product_type = db.Column(db.String(100), comment='产品类型')
    environment = db.Column(db.String(100), comment='环境')
    remarks = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'product_package_name': self.product_package_name,
            'product_address': self.product_address,
            'product_id': self.product_id,
            'is_automated': self.is_automated,
            'version_number': self.version_number,
            'product_image': self.product_image,
            'system_type': self.system_type,
            'product_type': self.product_type,
            'environment': self.environment,
            'remarks': self.remarks,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class AutomationProject(db.Model):
    """
    自动化测试案例表 (automation_projects)
    用于存储自动化测试流程、步骤等信息
    """
    __bind_key__ = 'automation'
    __tablename__ = 'automation_projects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    process_name = db.Column(db.String(255), nullable=False, comment='流程名称')
    product_ids = db.Column(db.Text, nullable=False, comment='关联产品ID集合')
    system = db.Column(db.String(100), comment='系统')
    product_type = db.Column(db.String(100), comment='产品类型')
    environment = db.Column(db.String(100), comment='环境')
    product_address = db.Column(db.Text, comment='产品地址')
    project_id = db.Column(db.Integer, comment='关联Project表ID')
    product_package_names = db.Column(db.Text, comment='产品包名集合')
    test_steps = db.Column(db.Text, comment='测试步骤配置')
    tab_switch_config = db.Column(db.Text, comment='Tab切换配置')
    assertion_config = db.Column(db.Text, comment='断言配置')
    screenshot_config = db.Column(db.Text, comment='截图配置')
    status = db.Column(db.String(50), default='待执行', comment='执行状态')
    created_by = db.Column(db.String(100), default='admin', comment='创建人')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'process_name': self.process_name,
            'product_ids': self.product_ids,
            'system': self.system,
            'product_type': self.product_type,
            'environment': self.environment,
            'product_address': self.product_address,
            'project_id': self.project_id,
            'product_package_names': self.product_package_names,
            'test_steps': self.test_steps,
            'tab_switch_config': self.tab_switch_config,
            'assertion_config': self.assertion_config,
            'screenshot_config': self.screenshot_config,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class ProjectFile(db.Model):
    """
    自动化测试文件表 (project_files)
    用于存储自动化测试Python文件路径
    """
    __bind_key__ = 'automation'
    __tablename__ = 'project_files'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    project_id = db.Column(db.Integer, nullable=False, comment='关联ProjectID')
    project_name = db.Column(db.String(255), nullable=False, comment='项目名称')
    file_name = db.Column(db.String(255), nullable=False, comment='文件名')
    file_path = db.Column(db.String(500), nullable=False, comment='文件路径')
    file_type = db.Column(db.String(20), default='py', comment='文件类型')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_name': self.project_name,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class AutomationExecution(db.Model):
    """
    自动化测试执行记录表 (automation_executions)
    """
    __bind_key__ = 'automation'
    __tablename__ = 'automation_executions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('automation_projects.id'), comment='关联项目ID')
    process_name = db.Column(db.String(255), nullable=False, comment='流程名称')
    product_ids = db.Column(db.Text, nullable=False, comment='关联产品ID集合')
    system = db.Column(db.String(100), comment='系统')
    product_type = db.Column(db.String(100), comment='产品类型')
    environment = db.Column(db.String(100), comment='环境')
    product_address = db.Column(db.Text, comment='产品地址')
    status = db.Column(db.String(50), nullable=False, comment='执行状态')
    start_time = db.Column(db.DateTime, comment='开始时间')
    end_time = db.Column(db.DateTime, comment='结束时间')
    log_message = db.Column(db.Text, comment='日志消息')
    detailed_log = db.Column(db.Text, comment='详细日志')
    executed_by = db.Column(db.String(100), default='admin', comment='执行人')
    cancel_type = db.Column(db.String(50), comment='取消类型')
    task_id = db.Column(db.String(50), comment='Celery任务ID')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'process_name': self.process_name,
            'status': self.status,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'executed_by': self.executed_by,
            'log_message': self.log_message,
            'detailed_log': self.detailed_log,
            'task_id': self.task_id
        }

class AutomationExecutMethodLog(db.Model):
    """
    自动化测试方法级日志表 (automation_execut_method_logs)
    用于存储每个测试方法的独立日志
    """
    __bind_key__ = 'automation'
    __tablename__ = 'automation_execut_method_logs'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    execution_id = db.Column(db.Integer, nullable=False, comment='关联automation_executions表ID')
    method_name = db.Column(db.String(100), nullable=False, comment='测试方法名称')
    log_content = db.Column(db.Text, comment='日志内容')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'method_name': self.method_name,
            'log_content': self.log_content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class EnumValue(db.Model):
    """
    枚举值表 (enum_values)
    用于存储系统类型、产品类型、环境类型等动态枚举值
    """
    __bind_key__ = 'automation'
    __tablename__ = 'enum_values'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    field_name = db.Column(db.String(100), nullable=False, comment='字段名称')
    field_value = db.Column(db.String(100), nullable=False, comment='字段值')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        return {
            'id': self.id,
            'field_name': self.field_name,
            'field_value': self.field_value,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class ProjectLog(db.Model):
    """
    产品操作日志表 (projects_log)
    用于记录产品新增/编辑操作记录
    """
    __bind_key__ = 'automation'
    __tablename__ = 'projects_log'
    log_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='日志ID')
    project_id = db.Column(db.Integer, nullable=False, comment='关联产品ID')
    user_id = db.Column(db.BigInteger, nullable=False, comment='操作用户ID')
    username = db.Column(db.String(30), nullable=False, comment='操作用户名')
    operation_type = db.Column(db.String(20), nullable=False, comment='操作类型(新增/编辑)')
    change_content = db.Column(db.Text, nullable=False, comment='变更内容')
    operation_time = db.Column(db.DateTime, default=datetime.now, comment='操作时间')
    operation_ip = db.Column(db.String(50), comment='操作IP')

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'project_id': self.project_id,
            'username': self.username,
            'operation_type': self.operation_type,
            'change_content': self.change_content,
            'operation_time': self.operation_time.strftime('%Y-%m-%d %H:%M:%S') if self.operation_time else None
        }
