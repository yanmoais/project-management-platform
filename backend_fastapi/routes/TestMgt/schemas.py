from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime, date

class TestPlanBase(BaseModel):
    plan_name: str
    version: Optional[str] = None
    status: Optional[int] = 1
    project_id: Optional[int] = None
    owner_id: Optional[int] = None
    start_time: Optional[date] = None
    end_time: Optional[date] = None
    remark: Optional[str] = None
    associated_case_ids: Optional[List[int]] = None

class TestPlanCreate(TestPlanBase):
    pass

class TestPlanUpdate(BaseModel):
    plan_id: int
    plan_name: Optional[str] = None
    version: Optional[str] = None
    status: Optional[int] = None
    project_id: Optional[int] = None
    owner_id: Optional[int] = None
    start_time: Optional[date] = None
    end_time: Optional[date] = None
    remark: Optional[str] = None
    associated_case_ids: Optional[List[int]] = None

class TestPlanResponse(TestPlanBase):
    plan_id: int
    create_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    project_name: Optional[str] = None
    owner_name: Optional[str] = None
    progress: Optional[float] = 0.0
    
    class Config:
        from_attributes = True

from typing import List, Optional, Union

class TestCaseBase(BaseModel):
    case_name: str
    case_type: Optional[int] = 1
    case_level: Optional[str] = 'P1'
    project_id: Optional[int] = None
    module_id: Optional[Union[int, str]] = None
    req_id: Optional[int] = None
    plan_id: Optional[int] = None
    remark: Optional[str] = None
    comments: Optional[List[dict]] = None
    pre_condition: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None

class TestCaseCreate(TestCaseBase):
    pass

class TestCaseUpdate(BaseModel):
    case_id: int
    case_name: Optional[str] = None
    case_type: Optional[int] = None
    case_status: Optional[int] = None
    case_level: Optional[str] = None
    project_id: Optional[int] = None
    module_id: Optional[Union[int, str]] = None
    req_id: Optional[int] = None
    plan_id: Optional[int] = None
    remark: Optional[str] = None
    pre_condition: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    comments: Optional[List[dict]] = None

class TestCaseResponse(TestCaseBase):
    case_id: int
    case_code: str
    case_status: Optional[int] = 4
    create_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    project_name: Optional[str] = None
    module_name: Optional[str] = None
    req_code: Optional[str] = None
    plan_name: Optional[str] = None

    class Config:
        from_attributes = True
