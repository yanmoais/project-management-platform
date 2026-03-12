from sqlalchemy import String, Integer, BigInteger, DateTime, Date, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from backend_fastapi.db.session import Base
from typing import Optional

class PMProject(Base):
    """
    项目管理表
    """
    __tablename__ = 'pm_project'

    project_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    project_code: Mapped[Optional[str]] = mapped_column(String(50))
    project_type: Mapped[Optional[str]] = mapped_column(String(50), default='Development')
    status: Mapped[Optional[str]] = mapped_column(String(20), default='Planning')
    priority: Mapped[Optional[str]] = mapped_column(String(20), default='Normal')
    owner_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    start_date: Mapped[Optional[datetime]] = mapped_column(Date)
    end_date: Mapped[Optional[datetime]] = mapped_column(Date)
    progress: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[str]] = mapped_column(Text) # JSON string
    
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'project_id': self.project_id,
            'project_name': self.project_name,
            'project_code': self.project_code,
            'project_type': self.project_type,
            'status': self.status,
            'priority': self.priority,
            'owner_id': self.owner_id,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'progress': self.progress,
            'description': self.description,
            'tags': self.tags,
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None
        }

class PMDefect(Base):
    """
    缺陷管理表
    """
    __tablename__ = 'pm_defect'

    defect_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    defect_code: Mapped[Optional[str]] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    project_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    module_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    defect_type: Mapped[Optional[str]] = mapped_column(String(50), default='Functional')
    severity: Mapped[Optional[str]] = mapped_column(String(20), default='Major')
    priority: Mapped[Optional[str]] = mapped_column(String(20), default='Medium')
    status: Mapped[Optional[str]] = mapped_column(String(50), default='New')
    reporter_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    assignee_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    linked_req_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    linked_task_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    case_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    environment: Mapped[Optional[str]] = mapped_column(String(100))
    version: Mapped[Optional[str]] = mapped_column(String(50))
    due_date: Mapped[Optional[datetime]] = mapped_column(Date)
    progress: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    del_flag: Mapped[int] = mapped_column(Integer, default=0)
    attachments: Mapped[Optional[str]] = mapped_column(Text) # JSON string

    def to_dict(self):
        return {
            'defect_id': self.defect_id,
            'defect_code': self.defect_code,
            'title': self.title,
            'description': self.description,
            'project_id': self.project_id,
            'module_id': self.module_id,
            'defect_type': self.defect_type,
            'severity': self.severity,
            'priority': self.priority,
            'status': self.status,
            'reporter_id': self.reporter_id,
            'assignee_id': self.assignee_id,
            'linked_req_id': self.linked_req_id,
            'linked_task_id': self.linked_task_id,
            'case_id': self.case_id,
            'environment': self.environment,
            'version': self.version,
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'progress': self.progress,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None,
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
            'attachments': self.attachments
        }


class PMRequirement(Base):
    """
    需求管理表
    """
    __tablename__ = 'pm_requirement'

    req_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    req_code: Mapped[Optional[str]] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[Optional[str]] = mapped_column(String(20), default='Medium')
    status: Mapped[Optional[str]] = mapped_column(String(50), default='Pending')
    project_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    module_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    parent_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    assignee_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    developer_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    tester_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    accepter_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    start_date: Mapped[Optional[datetime]] = mapped_column(Date)
    end_date: Mapped[Optional[datetime]] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text)
    iteration_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), default='Low')
    tags: Mapped[Optional[str]] = mapped_column(String(500)) # JSON string
    sort_order: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)
    progress: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    attachments: Mapped[Optional[str]] = mapped_column(Text) # JSON string
    del_flag: Mapped[int] = mapped_column(Integer, default=0)

    def to_dict(self):
        return {
            'req_id': self.req_id,
            'req_code': self.req_code,
            'title': self.title,
            'type': self.type,
            'priority': self.priority,
            'status': self.status,
            'project_id': self.project_id,
            'module_id': self.module_id,
            'parent_id': self.parent_id,
            'assignee_id': self.assignee_id,
            'developer_id': self.developer_id,
            'tester_id': self.tester_id,
            'accepter_id': self.accepter_id,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None,
            'progress': self.progress,
            'description': self.description,
            'iteration_id': self.iteration_id,
            'risk_level': self.risk_level,
            'tags': self.tags,
            'attachments': self.attachments,
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None
        }

class PMRequirementFollow(Base):
    """
    需求关注表
    """
    __tablename__ = 'pm_requirement_follow'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    requirement_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'requirement_id': self.requirement_id,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }

class PMSubRequirementFollow(Base):
    """
    子需求关注表
    """
    __tablename__ = 'pm_sub_requirement_follow'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sub_requirement_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sub_requirement_id': self.sub_requirement_id,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }

class PMTask(Base):
    """
    需求子任务表
    """
    __tablename__ = 'pm_task'

    task_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_code: Mapped[Optional[str]] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    estimate_time: Mapped[Optional[float]] = mapped_column(Integer, default=0) # 使用 Integer 或 Numeric
    assignee_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    developer_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    tester_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    status: Mapped[Optional[str]] = mapped_column(String(50), default='Pending')
    
    # New fields
    priority: Mapped[Optional[str]] = mapped_column(String(20), default='Medium')
    start_date: Mapped[Optional[datetime]] = mapped_column(Date)
    end_date: Mapped[Optional[datetime]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    sort_order: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    
    requirement_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    sub_requirement_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    del_flag: Mapped[int] = mapped_column(Integer, default=0)

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'task_code': self.task_code,
            'title': self.title,
            'estimate_time': self.estimate_time,
            'assignee_id': self.assignee_id,
            'status': self.status,
            'priority': self.priority,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'sort_order': self.sort_order,
            'requirement_id': self.requirement_id,
            'sub_requirement_id': self.sub_requirement_id,
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None
        }

class PMModule(Base):
    """
    项目模块表
    """
    __tablename__ = 'pm_module'

    module_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    module_name: Mapped[str] = mapped_column(String(100), nullable=False)
    project_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'module_id': self.module_id,
            'module_name': self.module_name,
            'project_id': self.project_id,
            'description': self.description,
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None
        }

class PMSubRequirement(Base):
    """
    子需求表
    """
    __tablename__ = 'pm_sub_requirement'

    sub_req_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sub_req_code: Mapped[Optional[str]] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50), default='product')
    priority: Mapped[Optional[str]] = mapped_column(String(20), default='Medium')
    status: Mapped[Optional[str]] = mapped_column(String(50), default='not_started')
    requirement_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    parent_sub_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    assignee_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    developer_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    tester_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    accepter_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    start_date: Mapped[Optional[datetime]] = mapped_column(Date)
    end_date: Mapped[Optional[datetime]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), default='Low')
    sort_order: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    attachments: Mapped[Optional[str]] = mapped_column(Text) # JSON string
    
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    del_flag: Mapped[int] = mapped_column(Integer, default=0)

    def to_dict(self):
        return {
            'sub_req_id': self.sub_req_id,
            'sub_req_code': self.sub_req_code,
            'title': self.title,
            'type': self.type,
            'priority': self.priority,
            'status': self.status,
            'requirement_id': self.requirement_id,
            'parent_sub_id': self.parent_sub_id,
            'assignee_id': self.assignee_id,
            'developer_id': self.developer_id,
            'tester_id': self.tester_id,
            'accepter_id': self.accepter_id,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'risk_level': self.risk_level,
            'sort_order': self.sort_order,
            'attachments': self.attachments,
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None
        }

