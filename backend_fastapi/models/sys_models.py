from sqlalchemy import String, Integer, BigInteger, DateTime, Date, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from backend_fastapi.db.session import Base
from typing import Optional

class SysUser(Base):
    """
    系统用户表
    """
    __tablename__ = 'sys_user'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    nickname: Mapped[Optional[str]] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(50))
    mobile: Mapped[Optional[str]] = mapped_column(String(11))
    avatar: Mapped[Optional[str]] = mapped_column(String(100))
    gender: Mapped[Optional[int]] = mapped_column(Integer, default=0) # 0:unknown, 1:male, 2:female
    birthday: Mapped[Optional[datetime]] = mapped_column(Date)
    status: Mapped[Optional[int]] = mapped_column(Integer, default=1) # 0:disabled, 1:enabled
    login_ip: Mapped[Optional[str]] = mapped_column(String(50))
    login_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    remark: Mapped[Optional[str]] = mapped_column(String(500))

    def to_dict(self):
        """转为字典格式"""
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

class SysRole(Base):
    """
    角色信息表
    """
    __tablename__ = 'sys_role'

    role_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(30), nullable=False)
    role_key: Mapped[str] = mapped_column(String(100), nullable=False)
    role_sort: Mapped[int] = mapped_column(Integer, default=0)
    data_scope: Mapped[int] = mapped_column(Integer, default=1) # 1:全部, 2:自定义, 3:本部门, 4:本部门及以下, 5:仅本人
    status: Mapped[int] = mapped_column(Integer, default=1) # 0:禁用, 1:启用
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    remark: Mapped[Optional[str]] = mapped_column(String(500))

    def to_dict(self):
        return {
            'role_id': self.role_id,
            'role_name': self.role_name,
            'role_key': self.role_key,
            'role_sort': self.role_sort,
            'data_scope': self.data_scope,
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'remark': self.remark
        }

class SysPost(Base):
    """
    岗位信息表
    """
    __tablename__ = 'sys_post'

    post_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_code: Mapped[str] = mapped_column(String(64), nullable=False)
    post_name: Mapped[str] = mapped_column(String(50), nullable=False)
    post_sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1) # 0:禁用, 1:启用
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    remark: Mapped[Optional[str]] = mapped_column(String(500))

    def to_dict(self):
        return {
            'post_id': self.post_id,
            'post_code': self.post_code,
            'post_name': self.post_name,
            'post_sort': self.post_sort,
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'remark': self.remark
        }

class SysDept(Base):
    """
    部门表
    """
    __tablename__ = 'sys_dept'

    dept_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(BigInteger, default=0)
    dept_name: Mapped[str] = mapped_column(String(30), nullable=False)
    dept_code: Mapped[Optional[str]] = mapped_column(String(64))
    leader: Mapped[Optional[str]] = mapped_column(String(20))
    phone: Mapped[Optional[str]] = mapped_column(String(11))
    email: Mapped[Optional[str]] = mapped_column(String(50))
    dept_sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    remark: Mapped[Optional[str]] = mapped_column(String(500))

    def to_dict(self):
        return {
            'dept_id': self.dept_id,
            'parent_id': self.parent_id,
            'dept_name': self.dept_name,
            'dept_code': self.dept_code,
            'leader': self.leader,
            'phone': self.phone,
            'email': self.email,
            'dept_sort': self.dept_sort,
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None
        }

class SysMenu(Base):
    """
    菜单权限表
    """
    __tablename__ = 'sys_menu'

    menu_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(BigInteger, default=0)
    menu_name: Mapped[str] = mapped_column(String(50), nullable=False)
    menu_type: Mapped[Optional[str]] = mapped_column(String(1)) # M:目录, C:菜单, F:按钮
    path: Mapped[Optional[str]] = mapped_column(String(200))
    component: Mapped[Optional[str]] = mapped_column(String(255))
    query: Mapped[Optional[str]] = mapped_column(String(255))
    is_frame: Mapped[int] = mapped_column(Integer, default=1) # 0:否, 1:是
    is_cache: Mapped[int] = mapped_column(Integer, default=0) # 0:否, 1:是
    menu_icon: Mapped[Optional[str]] = mapped_column(String(50))
    menu_key: Mapped[Optional[str]] = mapped_column(String(100))
    menu_sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    remark: Mapped[Optional[str]] = mapped_column(String(500))

    def to_dict(self):
        return {
            'menu_id': self.menu_id,
            'parent_id': self.parent_id,
            'menu_name': self.menu_name,
            'menu_type': self.menu_type,
            'path': self.path,
            'component': self.component,
            'is_frame': self.is_frame,
            'menu_icon': self.menu_icon,
            'menu_key': self.menu_key,
            'menu_sort': self.menu_sort,
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None
        }

class SysUserRole(Base):
    """
    用户角色关联表
    """
    __tablename__ = 'sys_user_role'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    role_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)

class SysRoleMenu(Base):
    """
    角色菜单关联表
    """
    __tablename__ = 'sys_role_menu'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    menu_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)

class SysUserDept(Base):
    """
    用户部门关联表
    """
    __tablename__ = 'sys_user_dept'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    dept_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_primary: Mapped[int] = mapped_column(Integer, default=0)
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)

class SysUserPost(Base):
    """
    用户岗位关联表
    """
    __tablename__ = 'sys_user_post'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    post_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_primary: Mapped[int] = mapped_column(Integer, default=0)
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)

class AppUserLog(Base):
    """
    用户登录日志表
    """
    __tablename__ = 'app_user_log'

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(30))
    login_ip: Mapped[Optional[str]] = mapped_column(String(50))
    login_location: Mapped[Optional[str]] = mapped_column(String(255))
    browser: Mapped[Optional[str]] = mapped_column(String(50))
    os: Mapped[Optional[str]] = mapped_column(String(50))
    device: Mapped[Optional[str]] = mapped_column(String(50))
    login_type: Mapped[Optional[int]] = mapped_column(Integer, default=1) # 1:password, 2:mobile, 3:scan, 4:third-party
    login_status: Mapped[Optional[int]] = mapped_column(Integer, default=1) # 0:fail, 1:success
    error_msg: Mapped[Optional[str]] = mapped_column(String(255))
    login_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    logout_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    online_duration: Mapped[Optional[int]] = mapped_column(Integer, default=0)

class TestEnvironment(Base):
    """
    测试环境表
    """
    __tablename__ = 'test_environment'
    
    env_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(100), nullable=False)
    env_name: Mapped[str] = mapped_column(String(50), nullable=False)
    env_type: Mapped[str] = mapped_column(String(20), nullable=False)
    env_url: Mapped[str] = mapped_column(String(255), nullable=False)
    db_type: Mapped[Optional[str]] = mapped_column(String(20))
    db_host: Mapped[Optional[str]] = mapped_column(String(100))
    db_port: Mapped[Optional[str]] = mapped_column(String(10))
    db_user: Mapped[Optional[str]] = mapped_column(String(50))
    db_password: Mapped[Optional[str]] = mapped_column(String(100))
    account: Mapped[Optional[str]] = mapped_column(String(50))
    password: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[Optional[str]] = mapped_column(String(20), default='Active')
    create_by: Mapped[Optional[str]] = mapped_column(String(64))

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

class TestEnvironmentLog(Base):
    """
    测试环境操作日志表
    """
    __tablename__ = 'test_environment_log'
    
    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment='日志ID')
    env_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='关联测试环境ID')
    username: Mapped[str] = mapped_column(String(30), nullable=False, comment='操作用户名')
    operation_type: Mapped[str] = mapped_column(String(20), nullable=False, comment='操作类型(新增/编辑)')
    change_content: Mapped[str] = mapped_column(Text, nullable=False, comment='变更内容')
    operation_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, comment='操作时间')

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'env_id': self.env_id,
            'username': self.username,
            'operation_type': self.operation_type,
            'change_content': self.change_content,
            'operation_time': self.operation_time.strftime('%Y-%m-%d %H:%M:%S') if self.operation_time else None
        }
