from sqlalchemy import String, Integer, BigInteger, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from backend_fastapi.db.session import Base
from typing import Optional

class InterfaceProject(Base):
    """
    接口自动化-项目管理表
    """
    __tablename__ = 'interface_projects'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='项目名称')
    description: Mapped[Optional[str]] = mapped_column(Text, comment='项目描述')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class InterfaceCase(Base):
    """
    接口自动化-用例管理表
    """
    __tablename__ = 'interface_cases'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    project_id: Mapped[int] = mapped_column(Integer, comment='关联项目ID')
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='用例名称')
    description: Mapped[Optional[str]] = mapped_column(Text, comment='用例描述')
    request_data: Mapped[Optional[str]] = mapped_column(Text, comment='请求数据(JSON)')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'request_data': self.request_data,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class InterfaceTestPlan(Base):
    """
    接口自动化-测试计划/管理表
    """
    __tablename__ = 'interface_test_plans'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='计划名称')
    status: Mapped[Optional[str]] = mapped_column(String(50), default='draft', comment='状态')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class InterfaceDefinition(Base):
    """
    接口自动化-API接口定义表
    """
    __tablename__ = 'interface_definitions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='接口名称')
    url: Mapped[str] = mapped_column(String(500), nullable=False, comment='接口路径')
    method: Mapped[str] = mapped_column(String(20), nullable=False, comment='请求方法')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'method': self.method,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class InterfaceReport(Base):
    """
    接口自动化-测试报告表
    """
    __tablename__ = 'interface_reports'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='报告名称')
    result: Mapped[Optional[str]] = mapped_column(Text, comment='测试结果(JSON)')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'result': self.result,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class InterfaceDocument(Base):
    """
    接口自动化-文档管理表
    """
    __tablename__ = 'interface_documents'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment='文档标题')
    content: Mapped[Optional[str]] = mapped_column(Text, comment='文档内容')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class InterfaceCommonMethod(Base):
    """
    接口自动化-公用方法表
    """
    __tablename__ = 'interface_common_methods'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='方法名称')
    code: Mapped[Optional[str]] = mapped_column(Text, comment='方法代码')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class InterfaceAssertionTemplate(Base):
    """
    接口自动化-断言模板表
    """
    __tablename__ = 'interface_assertion_templates'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='模板名称')
    content: Mapped[Optional[str]] = mapped_column(Text, comment='断言内容')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class InterfaceCommonConfig(Base):
    """
    接口自动化-公共配置表
    """
    __tablename__ = 'interface_common_configs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    key: Mapped[str] = mapped_column(String(255), nullable=False, comment='配置键')
    value: Mapped[Optional[str]] = mapped_column(Text, comment='配置值')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
