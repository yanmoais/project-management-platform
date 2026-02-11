from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    gender: Optional[int] = 0
    status: Optional[int] = 1
    remark: Optional[str] = None
    role_ids: Optional[List[int]] = []
    post_ids: Optional[List[int]] = []
    dept_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    user_id: int
    password: Optional[str] = None

class UserResponse(UserBase):
    user_id: int
    avatar: Optional[str] = None
    create_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# --- Role Schemas ---
class RoleBase(BaseModel):
    role_name: str
    role_key: str
    role_sort: Optional[int] = 0
    data_scope: Optional[int] = 1
    status: Optional[int] = 1
    remark: Optional[str] = None
    menu_ids: Optional[List[int]] = []

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    role_id: int

class RoleResponse(RoleBase):
    role_id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Menu Schemas ---
class MenuBase(BaseModel):
    parent_id: Optional[int] = 0
    menu_name: str
    menu_type: str # M, C, F
    path: Optional[str] = None
    component: Optional[str] = None
    query: Optional[str] = None
    is_frame: Optional[int] = 1
    is_cache: Optional[int] = 0
    menu_icon: Optional[str] = None
    menu_key: Optional[str] = None
    menu_sort: Optional[int] = 0
    status: Optional[int] = 1
    remark: Optional[str] = None

class MenuCreate(MenuBase):
    pass

class MenuUpdate(MenuBase):
    menu_id: int

class MenuResponse(MenuBase):
    menu_id: int
    children: Optional[List['MenuResponse']] = []
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Dept Schemas ---
class DeptBase(BaseModel):
    parent_id: Optional[int] = 0
    dept_name: str
    dept_code: Optional[str] = None
    leader: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    dept_sort: Optional[int] = 0
    status: Optional[int] = 1
    remark: Optional[str] = None

class DeptCreate(DeptBase):
    pass

class DeptUpdate(DeptBase):
    dept_id: int

class DeptResponse(DeptBase):
    dept_id: int
    children: Optional[List['DeptResponse']] = []
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Post Schemas ---
class PostBase(BaseModel):
    post_code: str
    post_name: str
    post_sort: Optional[int] = 0
    status: Optional[int] = 1
    remark: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    post_id: int

class PostResponse(PostBase):
    post_id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True
