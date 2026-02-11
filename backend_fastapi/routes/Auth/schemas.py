from pydantic import BaseModel, EmailStr
from typing import Optional, List

class Token(BaseModel):
    """
    Token 响应模型
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Token 数据模型
    """
    username: Optional[str] = None
    user_id: Optional[int] = None

class UserLogin(BaseModel):
    """
    用户登录请求模型
    """
    email: str # 前端可能传 email 或 username
    password: str

class UserRegister(BaseModel):
    """
    用户注册请求模型
    """
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """
    用户基本信息响应模型
    """
    user_id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[int] = None
    status: Optional[int] = None
    create_time: Optional[str] = None

class LoginResponse(BaseModel):
    """
    登录接口统一响应
    """
    code: int
    msg: str
    data: Optional[UserResponse] = None
    # token: str # 放到 header 中
