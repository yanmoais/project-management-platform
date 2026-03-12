from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, desc, func
from typing import Optional
import io
import csv
from backend_fastapi.db.session import get_db
from backend_fastapi.models.pm_models import PMProject
from backend_fastapi.models.sys_models import SysUser
from backend_fastapi.core.deps import get_current_user
from .schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from datetime import datetime

router = APIRouter(tags=["项目管理"])

@router.get("/list", response_model=None)
async def list_projects(
    page: int = 1,
    page_size: int = 10,
    project_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    project_type: Optional[str] = Query(None),
    owner_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    export: Optional[bool] = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取项目列表
    """
    query = select(PMProject, SysUser.nickname.label("owner_name")).outerjoin(SysUser, PMProject.owner_id == SysUser.user_id)
    
    if project_name:
        query = query.where(PMProject.project_name.like(f"%{project_name}%"))
    if status:
        query = query.where(PMProject.status == status)
    if project_type:
        query = query.where(PMProject.project_type == project_type)
    if owner_id:
        query = query.where(PMProject.owner_id == owner_id)
    if start_date:
        query = query.where(PMProject.create_time >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.where(PMProject.create_time <= datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59))

    # Export logic
    if export:
        query = query.order_by(desc(PMProject.create_time))
        result = await db.execute(query)
        projects = result.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['项目代码', '项目名称', '类型', '状态', '负责人', '创建时间'])
        for project, owner_name in projects:
            writer.writerow([
                project.project_code, 
                project.project_name, 
                project.project_type, 
                project.status, 
                owner_name, 
                project.create_time.strftime('%Y-%m-%d %H:%M:%S') if project.create_time else ''
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]), 
            media_type="text/csv", 
            headers={"Content-Disposition": "attachment; filename=projects.csv"}
        )

    # Calculate total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size).order_by(desc(PMProject.create_time))
    result = await db.execute(query)
    projects = result.all()

    rows = []
    import random
    for project, owner_name in projects:
        project_dict = project.__dict__
        project_dict['owner_name'] = owner_name
        # Mock data for demonstration
        project_dict['delayed_req_count'] = random.choice([0, 0, 0, 2, 5]) if project.project_id % 2 == 0 else 0
        project_dict['suspended_req_count'] = random.choice([0, 1, 3]) if project.project_id % 3 == 0 else 0
        rows.append(ProjectResponse(**project_dict))

    return {"total": total, "rows": rows}

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    创建项目
    """
    # Check if project name exists
    query = select(PMProject).where(PMProject.project_name == project_in.project_name)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="项目名称已存在")

    # Generate project_code: P-YYYYMMDD-SEQUENCE
    today_str = datetime.now().strftime('%Y%m%d')
    prefix = f"P-{today_str}-"
    
    # Find the max sequence for today
    query_code = select(PMProject.project_code).where(PMProject.project_code.like(f"{prefix}%")).order_by(desc(PMProject.project_code)).limit(1)
    result_code = await db.execute(query_code)
    last_code = result_code.scalar_one_or_none()
    
    if last_code:
        try:
            last_seq = int(last_code.split('-')[-1])
            new_seq = last_seq + 1
        except ValueError:
            new_seq = 0
    else:
        new_seq = 0
        
    project_code = f"{prefix}{new_seq}"

    project_data = project_in.model_dump()
    project_data['project_code'] = project_code

    new_project = PMProject(**project_data)
    new_project.create_by = current_user.username
    new_project.create_time = datetime.now()
    new_project.update_by = current_user.username
    new_project.update_time = datetime.now()

    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    return new_project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    更新项目
    """
    query = select(PMProject).where(PMProject.project_id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    project.update_by = current_user.username
    project.update_time = datetime.now()

    await db.commit()
    await db.refresh(project)
    return project

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    删除项目
    """
    query = select(PMProject).where(PMProject.project_id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    await db.delete(project)
    await db.commit()
    return {"code": 200, "msg": "删除成功"}

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取项目详情
    """
    query = select(PMProject, SysUser.nickname.label("owner_name")).outerjoin(SysUser, PMProject.owner_id == SysUser.user_id).where(PMProject.project_id == project_id)
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="项目不存在")

    project, owner_name = row
    project_dict = project.__dict__
    project_dict['owner_name'] = owner_name
    return ProjectResponse(**project_dict)
