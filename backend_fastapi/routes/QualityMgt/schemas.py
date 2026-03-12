from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import date, datetime

class DefectBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    module_id: Optional[Union[int, str]] = None
    defect_type: Optional[str] = 'Functional'
    severity: Optional[str] = 'Major'
    priority: Optional[str] = 'Medium'
    status: Optional[str] = 'New'
    reporter_id: Optional[int] = None
    assignee_id: Optional[int] = None
    linked_req_id: Optional[int] = None
    linked_task_id: Optional[int] = None
    case_id: Optional[int] = None
    environment: Optional[str] = None
    version: Optional[str] = None
    due_date: Optional[date] = None
    progress: Optional[int] = 0
    completed_at: Optional[datetime] = None
    attachments: Optional[str] = None

class DefectCreate(DefectBase):
    pass

class DefectUpdate(BaseModel):
    defect_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    module_id: Optional[Union[int, str]] = None
    defect_type: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    reporter_id: Optional[int] = None
    assignee_id: Optional[int] = None
    linked_req_id: Optional[int] = None
    linked_task_id: Optional[int] = None
    case_id: Optional[int] = None
    environment: Optional[str] = None
    version: Optional[str] = None
    due_date: Optional[date] = None
    attachments: Optional[str] = None

class DefectResponse(DefectBase):
    defect_id: int
    defect_code: Optional[str] = None
    create_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True
