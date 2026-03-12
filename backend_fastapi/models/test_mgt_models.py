from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from backend_fastapi.db.session import Base

class TestPlan(Base):
    """测试计划表"""
    __tablename__ = "test_plan"

    plan_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="计划ID")
    plan_name = Column(String(100), nullable=False, comment="计划名称")
    version = Column(String(50), nullable=True, comment="版本")
    status = Column(Integer, default=1, comment="状态(0:关闭,1:开启)")
    project_id = Column(Integer, ForeignKey("pm_project.project_id"), nullable=True, comment="所属项目ID")
    owner_id = Column(Integer, ForeignKey("sys_user.user_id"), nullable=True, comment="测试负责人ID")
    start_time = Column(Date, nullable=True, comment="开始时间")
    end_time = Column(Date, nullable=True, comment="结束时间")
    create_by = Column(String(64), nullable=True, comment="创建人(昵称)")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    remark = Column(String(500), nullable=True, comment="备注")
    associated_case_ids = Column(JSON, nullable=True, comment="关联测试用例ID列表")

    # Relationships
    project = relationship("PMProject", foreign_keys=[project_id])
    owner = relationship("SysUser", foreign_keys=[owner_id])
    test_cases = relationship("TestCase", back_populates="plan")

    def to_dict(self):
        return {
            "plan_id": self.plan_id,
            "plan_name": self.plan_name,
            "version": self.version,
            "status": self.status,
            "project_id": self.project_id,
            "project_name": self.project.project_name if self.project else None,
            "owner_id": self.owner_id,
            "owner_name": self.owner.nickname if self.owner else None,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "create_by": self.create_by,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "remark": self.remark,
            "associated_case_ids": self.associated_case_ids
        }

class PMTestCaseModule(Base):
    """测试用例模块表"""
    __tablename__ = "pm_test_case_module"

    module_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="模块ID")
    module_name = Column(String(100), nullable=False, comment="模块名称")
    parent_id = Column(Integer, nullable=True, comment="父模块ID")
    project_id = Column(Integer, ForeignKey("pm_project.project_id"), nullable=True, comment="所属项目ID")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")

class TestCase(Base):
    """测试用例表"""
    __tablename__ = "test_case"

    case_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="用例ID")
    case_code = Column(String(50), unique=True, nullable=False, comment="用例编号")
    case_name = Column(String(200), nullable=False, comment="用例名称")
    case_type = Column(Integer, default=1, comment="用例类型(1:功能测试,2:性能测试,3:安全性测试,4:回归测试,5:其他)")
    case_status = Column(Integer, default=0, comment="用例状态(0:未执行,1:通过,2:阻塞,3:失败,4:遗留)") 
    case_level = Column(String(20), default='P1', comment="用例等级(P0, P1, P2, P3)")
    module_id = Column(Integer, ForeignKey("pm_test_case_module.module_id"), nullable=True, comment="所属模块ID")
    req_id = Column(Integer, ForeignKey("pm_requirement.req_id"), nullable=True, comment="关联需求ID")
    project_id = Column(Integer, ForeignKey("pm_project.project_id"), nullable=True, comment="所属项目ID")
    plan_id = Column(Integer, ForeignKey("test_plan.plan_id"), nullable=True, comment="所属计划ID")
    create_by = Column(String(64), nullable=True, comment="创建人(昵称)")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    remark = Column(String(500), nullable=True, comment="备注")
    comments = Column(JSON, nullable=True, comment="评论列表")
    pre_condition = Column(Text, nullable=True, comment="前置条件")
    steps = Column(Text, nullable=True, comment="执行步骤")
    expected_result = Column(Text, nullable=True, comment="预期结果")
    module = relationship("PMTestCaseModule", foreign_keys=[module_id])
    requirement = relationship("PMRequirement", foreign_keys=[req_id])
    project = relationship("PMProject", foreign_keys=[project_id])
    plan = relationship("TestPlan", back_populates="test_cases")

    def to_dict(self):
        return {
            "case_id": self.case_id,
            "case_code": self.case_code,
            "case_name": self.case_name,
            "case_type": self.case_type,
            "case_status": self.case_status,
            "case_level": self.case_level,
            "project_id": self.project_id,
            "project_name": self.project.project_name if self.project else None,
            "module_id": self.module_id,
            "module_name": self.module.module_name if self.module else None,
            "req_id": self.req_id,
            "req_code": self.requirement.req_code if self.requirement else None,
            "plan_id": self.plan_id,
            "plan_name": self.plan.plan_name if self.plan else None,
            "create_by": self.create_by,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "remark": self.remark,
            "comments": self.comments,
            "pre_condition": self.pre_condition,
            "steps": self.steps,
            "expected_result": self.expected_result
        }
