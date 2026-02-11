from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from backend_fastapi.db.session import get_db
from backend_fastapi.models.sys_models import TestEnvironment, TestEnvironmentLog
from backend_fastapi.utils.LogManeger import log_info
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

router = APIRouter(tags=["测试环境管理"])

from .schemas import TestEnvironmentCreate, TestEnvironmentUpdate

# Routes

@router.get("/list")
async def get_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    projectName: Optional[str] = None,
    envType: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Build query
        stmt = select(TestEnvironment)
        
        if projectName:
            stmt = stmt.where(TestEnvironment.project_name.like(f'%{projectName}%'))
        if envType:
            stmt = stmt.where(TestEnvironment.env_type == envType)
            
        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Pagination
        stmt = stmt.offset((page - 1) * pageSize).limit(pageSize)
        result = await db.execute(stmt)
        rows = result.scalars().all()
        
        data = {
            'total': total,
            'rows': [item.to_dict() for item in rows]
        }
        
        return {'code': 200, 'msg': 'success', 'data': data}
        
    except Exception as e:
        log_info(f"Get environment list error: {str(e)}")
        return {'code': 500, 'msg': str(e), 'data': None}

@router.post("/add")
async def add_env(
    env_data: TestEnvironmentCreate,
    db: AsyncSession = Depends(get_db)
):
    log_info(f"添加测试环境数据为: {env_data.dict()}")
    
    try:
        new_env = TestEnvironment(
            project_name=env_data.project_name,
            env_name=env_data.env_name,
            env_type=env_data.env_type,
            env_url=env_data.env_url,
            db_type=env_data.db_type,
            db_host=env_data.db_host,
            db_port=env_data.db_port,
            db_user=env_data.db_user,
            db_password=env_data.db_password,
            account=env_data.account,
            password=env_data.password,
            status=env_data.status,
            create_by=env_data.create_by
        )
        db.add(new_env)
        await db.flush() # Get ID before commit
        
        # Record log
        log = TestEnvironmentLog(
            env_id=new_env.env_id,
            username=env_data.create_by or 'Unknown',
            operation_type='新增',
            change_content=f"新增测试环境: {new_env.env_name} (Project: {new_env.project_name})",
            operation_time=datetime.now()
        )
        db.add(log)
        
        await db.commit()
        return {'code': 200, 'msg': '操作成功', 'data': None}
        
    except Exception as e:
        await db.rollback()
        log_info(f"Add environment error: {str(e)}")
        return {'code': 500, 'msg': str(e), 'data': None}

@router.put("/update")
async def update_env(
    env_data: TestEnvironmentUpdate,
    db: AsyncSession = Depends(get_db)
):
    if not env_data.env_id:
        return {'code': 400, 'msg': 'Missing env_id', 'data': None}
        
    try:
        stmt = select(TestEnvironment).where(TestEnvironment.env_id == env_data.env_id)
        result = await db.execute(stmt)
        env = result.scalar_one_or_none()
        
        if not env:
            return {'code': 404, 'msg': 'Environment not found', 'data': None}
            
        # Prepare change content
        changes = []
        if env_data.project_name is not None and env_data.project_name != env.project_name:
            changes.append(f"项目名称: {env.project_name} -> {env_data.project_name}")
            env.project_name = env_data.project_name
            
        if env_data.env_name is not None and env_data.env_name != env.env_name:
            changes.append(f"环境名称: {env.env_name} -> {env_data.env_name}")
            env.env_name = env_data.env_name
            
        if env_data.env_url is not None and env_data.env_url != env.env_url:
            changes.append(f"环境地址: {env.env_url} -> {env_data.env_url}")
            env.env_url = env_data.env_url
            
        if env_data.status is not None and env_data.status != env.status:
            changes.append(f"状态: {env.status} -> {env_data.status}")
            env.status = env_data.status
            
        # Update other fields
        if env_data.env_type is not None: env.env_type = env_data.env_type
        if env_data.db_type is not None: env.db_type = env_data.db_type
        if env_data.db_host is not None: env.db_host = env_data.db_host
        if env_data.db_port is not None: env.db_port = env_data.db_port
        if env_data.db_user is not None: env.db_user = env_data.db_user
        if env_data.db_password is not None: env.db_password = env_data.db_password
        if env_data.account is not None: env.account = env_data.account
        if env_data.password is not None: env.password = env_data.password
        if env_data.update_by is not None: env.update_by = env_data.update_by
        
        change_content = "编辑环境: " + "; ".join(changes) if changes else "编辑环境 (无关键字段变更)"
        
        # Record log
        log = TestEnvironmentLog(
            env_id=env.env_id,
            username=env_data.update_by or 'Unknown',
            operation_type='编辑',
            change_content=change_content,
            operation_time=datetime.now()
        )
        db.add(log)
        
        await db.commit()
        return {'code': 200, 'msg': '操作成功', 'data': None}
        
    except Exception as e:
        await db.rollback()
        log_info(f"Update environment error: {str(e)}")
        return {'code': 500, 'msg': str(e), 'data': None}

@router.delete("/delete/{env_id}")
async def delete_env(
    env_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(TestEnvironment).where(TestEnvironment.env_id == env_id)
        result = await db.execute(stmt)
        env = result.scalar_one_or_none()
        
        if not env:
            return {'code': 404, 'msg': 'Environment not found', 'data': None}
            
        await db.delete(env)
        await db.commit()
        return {'code': 200, 'msg': '操作成功', 'data': None}
        
    except Exception as e:
        await db.rollback()
        log_info(f"Delete environment error: {str(e)}")
        return {'code': 500, 'msg': str(e), 'data': None}

@router.get("/logs/{env_id}")
async def get_logs(
    env_id: int,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = select(TestEnvironmentLog).where(TestEnvironmentLog.env_id == env_id).order_by(desc(TestEnvironmentLog.operation_time)).limit(limit)
        result = await db.execute(stmt)
        logs = result.scalars().all()
        
        return {
            'code': 200, 
            'msg': 'success', 
            'data': [log.to_dict() for log in logs]
        }
    except Exception as e:
        log_info(f"Get logs error: {str(e)}")
        return {'code': 500, 'msg': str(e), 'data': None}
