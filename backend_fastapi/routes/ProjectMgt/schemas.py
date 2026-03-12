from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class ProjectBase(BaseModel):
    project_name: str
    project_code: Optional[str] = None
    project_type: Optional[str] = 'Development'
    status: Optional[str] = 'Planning'
    priority: Optional[str] = 'Normal'
    owner_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    progress: Optional[int] = 0
    description: Optional[str] = None
    tags: Optional[str] = None # JSON string

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    project_name: Optional[str] = None

class ProjectResponse(ProjectBase):
    project_id: int
    create_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None
    owner_name: Optional[str] = None # Added for display
    delayed_req_count: int = 0 # Mock: 延期/过期需求数
    suspended_req_count: int = 0 # Mock: 暂停需求数

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    total: int
    rows: List[ProjectResponse]
