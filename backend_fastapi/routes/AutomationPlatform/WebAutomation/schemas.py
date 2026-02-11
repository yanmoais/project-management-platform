from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union, Any

# ==========================================
# Automation Management Models
# ==========================================

class GenerateAccountsRequest(BaseModel):
    urls: List[str]

class GetLoginAccountsRequest(BaseModel):
    urls: List[str]

class CreateProjectRequest(BaseModel):
    process_name: str
    product_ids: Optional[Union[List[Union[str, Dict]], str]] = None
    system: Optional[str] = None
    product_type: Optional[str] = None
    environment: Optional[str] = None
    product_address: Optional[str] = None
    project_id: Optional[int] = None
    product_package_names: Optional[Union[List[str], str]] = None
    test_steps: Optional[List[Dict]] = None
    tab_switch_config: Optional[Union[Dict, List]] = None
    assertion_config: Optional[Union[Dict, List]] = None
    screenshot_config: Optional[Union[Dict, List]] = None
    created_by: Optional[str] = "admin"

class UpdateProjectRequest(BaseModel):
    process_name: Optional[str] = None
    product_ids: Optional[Union[List[Union[str, Dict]], str]] = None
    system: Optional[str] = None
    product_type: Optional[str] = None
    environment: Optional[str] = None
    product_address: Optional[str] = None
    project_id: Optional[int] = None
    product_package_names: Optional[Union[List[str], str]] = None
    test_steps: Optional[Union[List[Dict], Dict]] = None
    tab_switch_config: Optional[Union[Dict, List]] = None
    assertion_config: Optional[Union[Dict, List]] = None
    screenshot_config: Optional[Union[Dict, List]] = None
    update_by: Optional[str] = None

class ExecuteProjectRequest(BaseModel):
    executed_by: Optional[str] = "admin"

class TestConnectionRequest(BaseModel):
    urls: List[str]

class SaveCodeRequest(BaseModel):
    project_id: int
    content: str
    file_path: Optional[str] = None

# ==========================================
# Product Management Models
# ==========================================

class ProjectCreate(BaseModel):
    product_package_name: Optional[str] = None
    product_id: Optional[str] = None
    system_type: Optional[str] = None
    product_type: Optional[str] = None
    environment: Optional[str] = None
    product_address: Optional[str] = None
    is_automated: Optional[str] = '待接入'
    version_number: Optional[str] = None
    product_image: Optional[str] = None
    remarks: Optional[str] = None

class ProjectUpdate(BaseModel):
    product_package_name: Optional[str] = None
    product_id: Optional[str] = None
    system_type: Optional[str] = None
    product_type: Optional[str] = None
    environment: Optional[str] = None
    product_address: Optional[str] = None
    is_automated: Optional[str] = None
    version_number: Optional[str] = None
    product_image: Optional[str] = None
    remarks: Optional[str] = None

class EnumCreate(BaseModel):
    field_name: str
    field_value: str
