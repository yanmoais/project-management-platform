from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import date, datetime

class RequirementBase(BaseModel):
    title: str
    type: str
    priority: Optional[str] = 'Medium'
    status: Optional[str] = 'Pending'
    project_id: Optional[int] = None
    module_id: Optional[Union[int, str]] = None # 允许传ID或名称
    parent_id: Optional[int] = None
    assignee_id: Optional[int] = None
    developer_id: Optional[int] = None
    tester_id: Optional[int] = None
    accepter_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    iteration_id: Optional[int] = None
    risk_level: Optional[str] = 'Low'
    tags: Optional[str] = None # JSON string
    attachments: Optional[str] = None # JSON string
    progress: Optional[int] = 0
    
    create_by: Optional[str] = None
    update_by: Optional[str] = None

class RequirementCreate(RequirementBase):
    pass

class RequirementUpdate(BaseModel):
    req_id: int
    title: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    project_id: Optional[int] = None
    module_id: Optional[Union[int, str]] = None
    parent_id: Optional[int] = None
    assignee_id: Optional[int] = None
    developer_id: Optional[int] = None
    tester_id: Optional[int] = None
    accepter_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    iteration_id: Optional[int] = None
    risk_level: Optional[str] = None
    tags: Optional[str] = None
    attachments: Optional[str] = None
    progress: Optional[int] = None
    update_by: Optional[str] = None

class RequirementResponse(RequirementBase):
    req_id: int
    req_code: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    del_flag: int

    class Config:
        from_attributes = True

class SubRequirementBase(BaseModel):
    title: str
    type: Optional[str] = 'product'
    priority: Optional[str] = 'Medium'
    status: Optional[str] = 'not_started'
    requirement_id: Optional[int] = None
    parent_sub_id: Optional[int] = None
    assignee_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    risk_level: Optional[str] = 'Low'
    sort_order: Optional[int] = 0
    attachments: Optional[str] = None # JSON string

class SubRequirementCreate(SubRequirementBase):
    pass

class SubRequirementUpdate(BaseModel):
    sub_req_id: int
    title: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assignee_id: Optional[int] = None
    developer_id: Optional[int] = None
    tester_id: Optional[int] = None
    accepter_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    risk_level: Optional[str] = None
    sort_order: Optional[int] = None
    attachments: Optional[str] = None # JSON string

class SubRequirementResponse(SubRequirementBase):
    sub_req_id: int
    sub_req_code: Optional[str] = None
    create_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ModuleBase(BaseModel):
    module_name: str
    project_id: Optional[int] = None
    description: Optional[str] = None
    create_by: Optional[str] = None

class ModuleCreate(ModuleBase):
    pass

class ModuleResponse(ModuleBase):
    module_id: int
    create_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    estimate_time: Optional[float] = 0
    assignee_id: Optional[int] = None
    status: Optional[str] = 'Pending'
    priority: Optional[str] = 'Medium'
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    sort_order: Optional[int] = 0
    requirement_id: Optional[int] = None
    sub_requirement_id: Optional[int] = None
    
class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    task_id: int
    title: Optional[str] = None
    estimate_time: Optional[float] = None
    assignee_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    sort_order: Optional[int] = None
    requirement_id: Optional[int] = None
    sub_requirement_id: Optional[int] = None

class TaskResponse(TaskBase):
    task_id: int
    create_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True
