from pydantic import BaseModel
from typing import Optional

class TestEnvironmentCreate(BaseModel):
    project_name: str
    env_name: str
    env_type: str
    env_url: str
    db_type: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    account: Optional[str] = None
    password: Optional[str] = None
    status: Optional[str] = "Active"
    create_by: Optional[str] = None

class TestEnvironmentUpdate(BaseModel):
    env_id: int
    project_name: Optional[str] = None
    env_name: Optional[str] = None
    env_type: Optional[str] = None
    env_url: Optional[str] = None
    db_type: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    account: Optional[str] = None
    password: Optional[str] = None
    status: Optional[str] = None
    update_by: Optional[str] = None
