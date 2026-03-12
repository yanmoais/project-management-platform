from sqlalchemy import String, Integer, BigInteger, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from backend_fastapi.db.session import Base
from typing import Optional

class SysAutomationRule(Base):
    """
    自动化规则表
    """
    __tablename__ = 'sys_automation_rule'

    rule_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    rule_name: Mapped[str] = mapped_column(String(100), nullable=False, comment='规则名称')
    rule_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment='规则编码')
    description: Mapped[Optional[str]] = mapped_column(Text, comment='规则描述')
    
    trigger_event: Mapped[str] = mapped_column(String(50), nullable=False, comment='触发事件')
    
    # 使用 JSON 存储条件和动作配置
    conditions: Mapped[Optional[dict]] = mapped_column(JSON, comment='触发条件配置')
    actions: Mapped[Optional[list]] = mapped_column(JSON, comment='执行动作配置')
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否启用')
    priority: Mapped[int] = mapped_column(Integer, default=0, comment='优先级')
    
    # 定时任务相关字段
    rule_type: Mapped[str] = mapped_column(String(20), default='event', comment='规则类型: event(事件触发)/schedule(定时任务)')
    cron_expression: Mapped[Optional[str]] = mapped_column(String(50), comment='Cron表达式')
    query_config: Mapped[Optional[dict]] = mapped_column(JSON, comment='查询配置(用于定时扫描)')
    
    create_by: Mapped[Optional[str]] = mapped_column(String(64))
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    update_by: Mapped[Optional[str]] = mapped_column(String(64))
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

class SysAutomationLog(Base):
    """
    自动化执行日志表
    """
    __tablename__ = 'sys_automation_log'

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    rule_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='关联规则ID')
    rule_name: Mapped[str] = mapped_column(String(100), comment='规则名称快照')
    
    trigger_event: Mapped[str] = mapped_column(String(50), comment='触发事件')
    target_id: Mapped[Optional[str]] = mapped_column(String(50), comment='目标对象ID')
    
    execution_status: Mapped[str] = mapped_column(String(20), default='success', comment='执行状态: success/failed')
    execution_result: Mapped[Optional[str]] = mapped_column(Text, comment='执行结果/错误信息')
    
    execution_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment='执行时间')
