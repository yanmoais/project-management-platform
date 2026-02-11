from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, distinct
from backend_fastapi.db.session import get_automation_db, get_db
from backend_fastapi.models.automation_models import Project, EnumValue, ProjectLog
from backend_fastapi.models.sys_models import SysUser
from backend_fastapi.core.deps import get_current_user
from backend_fastapi.utils.LogManeger import log_info
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import uuid
import shutil

router = APIRouter(tags=["产品管理"])


# Configuration
# backend_fastapi/routes/AutomationPlatform/WebAutomation
# 1. WebAutomation
# 2. AutomationPlatform
# 3. routes
# 4. backend_fastapi
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_FOLDER = os.path.join(BACKEND_DIR, 'static', 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

from .schemas import (
    ProjectCreate,
    ProjectUpdate,
    EnumCreate
)

# Routes

@router.get('/projects')
async def get_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    product_ids: Optional[str] = None,
    product_names: Optional[str] = None,
    environment: Optional[str] = None,
    product_address: Optional[str] = None,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        stmt = select(Project)
        
        if product_ids:
            id_list = product_ids.split(',')
            stmt = stmt.where(Project.product_id.in_(id_list))
        if product_names:
            name_list = product_names.split(',')
            stmt = stmt.where(Project.product_package_name.in_(name_list))
        if environment:
            stmt = stmt.where(Project.environment == environment)
        if product_address:
            stmt = stmt.where(Project.product_address.like(f'%{product_address}%'))
            
        stmt = stmt.order_by(desc(Project.id))
        
        # Pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        projects = result.scalars().all()
        
        return {
            'code': 200,
            'message': 'Success',
            'data': {
                'list': [p.to_dict() for p in projects],
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }
    except Exception as e:
        return {'code': 500, 'message': str(e)}

@router.get('/projects/options')
async def get_project_options(db: AsyncSession = Depends(get_automation_db)):
    try:
        stmt_ids = select(distinct(Project.product_id))
        res_ids = await db.execute(stmt_ids)
        ids = res_ids.scalars().all()
        
        stmt_names = select(distinct(Project.product_package_name))
        res_names = await db.execute(stmt_names)
        names = res_names.scalars().all()
        
        return {
            'code': 200,
            'message': 'Success',
            'data': {
                'product_ids': [i for i in ids if i],
                'product_names': [n for n in names if n]
            }
        }
    except Exception as e:
        return {'code': 500, 'message': str(e)}

@router.post('/projects')
async def create_project(
    project_in: ProjectCreate,
    request: Request,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        new_project = Project(
            product_package_name=project_in.product_package_name,
            product_id=project_in.product_id,
            system_type=project_in.system_type,
            product_type=project_in.product_type,
            environment=project_in.environment,
            product_address=project_in.product_address,
            is_automated=project_in.is_automated,
            version_number=project_in.version_number,
            product_image=project_in.product_image,
            remarks=project_in.remarks
        )
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        
        # Log
        try:
            log = ProjectLog(
                project_id=new_project.id,
                user_id=current_user.user_id,
                username=current_user.nickname or current_user.username,
                operation_type='新增',
                change_content=f"新增产品: {new_project.product_package_name}",
                operation_ip=request.client.host
            )
            db.add(log)
            await db.commit()
        except Exception as log_e:
            log_info(f"Failed to create log: {str(log_e)}")
            
        return {'code': 200, 'message': 'Project created successfully', 'data': new_project.to_dict()}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'message': str(e)}

@router.put('/projects/{id}')
async def update_project(
    id: int,
    project_in: ProjectUpdate,
    request: Request,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        stmt = select(Project).where(Project.id == id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        
        if not project:
            return {'code': 404, 'message': 'Project not found'}
            
        updated_fields = []
        
        if project_in.product_package_name is not None and project_in.product_package_name != project.product_package_name:
            project.product_package_name = project_in.product_package_name
            updated_fields.append('产品包名')
        if project_in.product_id is not None and project_in.product_id != project.product_id:
            project.product_id = project_in.product_id
            updated_fields.append('产品ID')
        if project_in.system_type is not None and project_in.system_type != project.system_type:
            project.system_type = project_in.system_type
            updated_fields.append('系统类型')
        if project_in.product_type is not None and project_in.product_type != project.product_type:
            project.product_type = project_in.product_type
            updated_fields.append('产品类型')
        if project_in.environment is not None and project_in.environment != project.environment:
            project.environment = project_in.environment
            updated_fields.append('环境')
        if project_in.product_address is not None and project_in.product_address != project.product_address:
            project.product_address = project_in.product_address
            updated_fields.append('产品地址')
        if project_in.is_automated is not None and project_in.is_automated != project.is_automated:
            project.is_automated = project_in.is_automated
            updated_fields.append('是否自动化')
        if project_in.version_number is not None and project_in.version_number != project.version_number:
            project.version_number = project_in.version_number
            updated_fields.append('版本号')
        if project_in.product_image is not None and project_in.product_image != project.product_image:
            project.product_image = project_in.product_image
            updated_fields.append('产品图片')
        if project_in.remarks is not None and project_in.remarks != project.remarks:
            project.remarks = project_in.remarks
            updated_fields.append('备注')
            
        await db.commit()
        
        if updated_fields:
            try:
                log = ProjectLog(
                    project_id=project.id,
                    user_id=current_user.user_id,
                    username=current_user.nickname or current_user.username,
                    operation_type='编辑',
                    change_content=f"修改字段: {', '.join(updated_fields)}",
                    operation_ip=request.client.host
                )
                db.add(log)
                await db.commit()
            except Exception as log_e:
                log_info(f"Failed to create log: {str(log_e)}")
                
        return {'code': 200, 'message': 'Project updated successfully', 'data': project.to_dict()}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'message': str(e)}

@router.delete('/projects/{id}')
async def delete_project(
    id: int,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        stmt = select(Project).where(Project.id == id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        
        if not project:
            return {'code': 404, 'message': 'Project not found'}
            
        await db.delete(project)
        await db.commit()
        return {'code': 200, 'message': 'Project deleted successfully'}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'message': str(e)}

@router.get('/enums/{field_name}')
async def get_enums(
    field_name: str,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        stmt = select(EnumValue).where(EnumValue.field_name == field_name)
        result = await db.execute(stmt)
        enums = result.scalars().all()
        return {'code': 200, 'message': 'Success', 'data': [e.field_value for e in enums]}
    except Exception as e:
        return {'code': 500, 'message': str(e)}

@router.post('/enums')
async def add_enum(
    enum_in: EnumCreate,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        stmt = select(EnumValue).where(EnumValue.field_name == enum_in.field_name, EnumValue.field_value == enum_in.field_value)
        result = await db.execute(stmt)
        exists = result.scalar_one_or_none()
        
        if exists:
            return {'code': 200, 'message': 'Enum value already exists'}
            
        new_enum = EnumValue(field_name=enum_in.field_name, field_value=enum_in.field_value)
        db.add(new_enum)
        await db.commit()
        return {'code': 200, 'message': 'Enum value added', 'data': new_enum.to_dict()}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'message': str(e)}

@router.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    if not file:
        return {'code': 400, 'message': 'No file part'}
    if not file.filename:
        return {'code': 400, 'message': 'No selected file'}
        
    try:
        filename = str(uuid.uuid4()) + "_" + file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_url = f"/static/uploads/{filename}"
        return {'code': 200, 'message': 'Success', 'data': {'url': file_url}}
    except Exception as e:
        return {'code': 500, 'message': str(e)}

@router.get('/projects/{id}/logs')
async def get_project_logs(
    id: int,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        stmt = select(ProjectLog).where(ProjectLog.project_id == id).order_by(desc(ProjectLog.operation_time))
        result = await db.execute(stmt)
        logs = result.scalars().all()
        return {'code': 200, 'message': 'Success', 'data': [log.to_dict() for log in logs]}
    except Exception as e:
        return {'code': 500, 'message': str(e)}
