from sqlalchemy import String, Integer, BigInteger, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from backend_fastapi.db.session import Base
from typing import Optional

class Project(Base):
    """
    产品表 (projects)
    用于存储产品基本信息
    """
    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    product_package_name: Mapped[str] = mapped_column(String(255), nullable=False, comment='产品包名')
    product_address: Mapped[str] = mapped_column(Text, nullable=False, comment='产品地址')
    product_id: Mapped[Optional[str]] = mapped_column(String(255), comment='产品ID')
    is_automated: Mapped[str] = mapped_column(String(10), nullable=False, comment='是否自动化(已接入/待接入)')
    version_number: Mapped[Optional[str]] = mapped_column(String(100), comment='版本号')
    product_image: Mapped[Optional[str]] = mapped_column(Text, comment='产品图片URL')
    system_type: Mapped[Optional[str]] = mapped_column(String(100), comment='系统类型')
    product_type: Mapped[Optional[str]] = mapped_column(String(100), comment='产品类型')
    environment: Mapped[Optional[str]] = mapped_column(String(100), comment='环境')
    remarks: Mapped[Optional[str]] = mapped_column(Text, comment='备注')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

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

class AutomationProject(Base):
    """
    自动化测试案例表 (automation_projects)
    用于存储自动化测试流程、步骤等信息
    """
    __tablename__ = 'automation_projects'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    process_name: Mapped[str] = mapped_column(String(255), nullable=False, comment='流程名称')
    product_ids: Mapped[str] = mapped_column(Text, nullable=False, comment='关联产品ID集合')
    system: Mapped[Optional[str]] = mapped_column(String(100), comment='系统')
    product_type: Mapped[Optional[str]] = mapped_column(String(100), comment='产品类型')
    environment: Mapped[Optional[str]] = mapped_column(String(100), comment='环境')
    product_address: Mapped[Optional[str]] = mapped_column(Text, comment='产品地址')
    project_id: Mapped[Optional[int]] = mapped_column(Integer, comment='关联Project表ID')
    product_package_names: Mapped[Optional[str]] = mapped_column(Text, comment='产品包名集合')
    test_steps: Mapped[Optional[str]] = mapped_column(Text, comment='测试步骤配置')
    tab_switch_config: Mapped[Optional[str]] = mapped_column(Text, comment='Tab切换配置')
    assertion_config: Mapped[Optional[str]] = mapped_column(Text, comment='断言配置')
    screenshot_config: Mapped[Optional[str]] = mapped_column(Text, comment='截图配置')
    status: Mapped[Optional[str]] = mapped_column(String(50), default='待执行', comment='执行状态')
    created_by: Mapped[Optional[str]] = mapped_column(String(100), default='admin', comment='创建人')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

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

class ProjectFile(Base):
    """
    自动化测试文件表 (project_files)
    用于存储自动化测试Python文件路径
    """
    __tablename__ = 'project_files'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    project_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='关联ProjectID')
    project_name: Mapped[str] = mapped_column(String(255), nullable=False, comment='项目名称')
    file_name: Mapped[str] = mapped_column(String(255), nullable=False, comment='文件名')
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, comment='文件路径')
    file_type: Mapped[Optional[str]] = mapped_column(String(20), default='py', comment='文件类型')
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True, comment='是否激活')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

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

class AutomationExecution(Base):
    """
    自动化测试执行记录表 (automation_executions)
    """
    __tablename__ = 'automation_executions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('automation_projects.id'), comment='关联项目ID')
    process_name: Mapped[str] = mapped_column(String(255), nullable=False, comment='流程名称')
    product_ids: Mapped[str] = mapped_column(Text, nullable=False, comment='关联产品ID集合')
    system: Mapped[Optional[str]] = mapped_column(String(100), comment='系统')
    product_type: Mapped[Optional[str]] = mapped_column(String(100), comment='产品类型')
    environment: Mapped[Optional[str]] = mapped_column(String(100), comment='环境')
    product_address: Mapped[Optional[str]] = mapped_column(Text, comment='产品地址')
    status: Mapped[str] = mapped_column(String(50), nullable=False, comment='执行状态')
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, comment='开始时间')
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, comment='结束时间')
    log_message: Mapped[Optional[str]] = mapped_column(Text, comment='日志消息')
    detailed_log: Mapped[Optional[str]] = mapped_column(Text, comment='详细日志')
    executed_by: Mapped[Optional[str]] = mapped_column(String(100), default='admin', comment='执行人')
    cancel_type: Mapped[Optional[str]] = mapped_column(String(50), comment='取消类型')
    task_id: Mapped[Optional[str]] = mapped_column(String(50), comment='Celery任务ID')

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

class AutomationExecutMethodLog(Base):
    """
    自动化测试方法级日志表 (automation_execut_method_logs)
    用于存储每个测试方法的独立日志
    """
    __tablename__ = 'automation_execut_method_logs'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    execution_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='关联automation_executions表ID')
    method_name: Mapped[str] = mapped_column(String(100), nullable=False, comment='测试方法名称')
    log_content: Mapped[Optional[str]] = mapped_column(Text, comment='日志内容')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'method_name': self.method_name,
            'log_content': self.log_content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class EnumValue(Base):
    """
    枚举值表 (enum_values)
    用于存储系统类型、产品类型、环境类型等动态枚举值
    """
    __tablename__ = 'enum_values'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    field_name: Mapped[str] = mapped_column(String(100), nullable=False, comment='字段名称')
    field_value: Mapped[str] = mapped_column(String(100), nullable=False, comment='字段值')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        return {
            'id': self.id,
            'field_name': self.field_name,
            'field_value': self.field_value,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class ProjectLog(Base):
    """
    产品操作日志表 (projects_log)
    用于记录产品新增/编辑操作记录
    """
    __tablename__ = 'projects_log'
    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment='日志ID')
    project_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='关联产品ID')
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='操作用户ID')
    username: Mapped[str] = mapped_column(String(30), nullable=False, comment='操作用户名')
    operation_type: Mapped[str] = mapped_column(String(20), nullable=False, comment='操作类型(新增/编辑)')
    change_content: Mapped[str] = mapped_column(Text, nullable=False, comment='变更内容')
    operation_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='操作时间')
    operation_ip: Mapped[Optional[str]] = mapped_column(String(50), comment='操作IP')

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'project_id': self.project_id,
            'username': self.username,
            'operation_type': self.operation_type,
            'change_content': self.change_content,
            'operation_time': self.operation_time.strftime('%Y-%m-%d %H:%M:%S') if self.operation_time else None
        }
