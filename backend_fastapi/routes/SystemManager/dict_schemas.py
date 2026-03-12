from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DictTypeBase(BaseModel):
    dict_name: str
    dict_type: str
    status: Optional[int] = 1
    remark: Optional[str] = None

class DictTypeCreate(DictTypeBase):
    pass

class DictTypeUpdate(DictTypeBase):
    dict_id: int

class DictTypeResponse(DictTypeBase):
    dict_id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class DictDataBase(BaseModel):
    dict_type: str # Use dict_type string for easier API usage, backend will resolve to id
    dict_label: str
    dict_value: str
    dict_sort: Optional[int] = 0
    status: Optional[int] = 1
    remark: Optional[str] = None

class DictDataCreate(DictDataBase):
    pass

class DictDataUpdate(DictDataBase):
    dict_data_id: int

class DictDataResponse(DictDataBase):
    dict_data_id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True
