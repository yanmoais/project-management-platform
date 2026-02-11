from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from backend_fastapi.core.deps import get_db, get_current_user
from backend_fastapi.models.sys_models import SysDept, SysUser, SysUserDept
from backend_fastapi.routes.SystemManager.schemas import DeptCreate, DeptUpdate, DeptResponse
from typing import List, Optional

router = APIRouter(tags=["部门管理"])

@router.get("/list")
async def list_depts(
    dept_name: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysDept).order_by(SysDept.dept_sort)
        
        if dept_name:
            stmt = stmt.where(SysDept.dept_name.like(f"%{dept_name}%"))
        if status is not None:
            stmt = stmt.where(SysDept.status == status)
            
        result = await db.execute(stmt)
        depts = result.scalars().all()
        
        # Return flat list
        return {'code': 200, 'msg': 'Success', 'data': [d.to_dict() for d in depts]}
    except Exception as e:
        return {'code': 500, 'msg': str(e)}

@router.get("/{dept_id}")
async def get_dept(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysDept).where(SysDept.dept_id == dept_id)
        result = await db.execute(stmt)
        dept = result.scalar_one_or_none()
        
        if not dept:
            return {'code': 404, 'msg': 'Dept not found'}
            
        return {'code': 200, 'msg': 'Success', 'data': dept.to_dict()}
    except Exception as e:
        return {'code': 500, 'msg': str(e)}

@router.post("/")
async def create_dept(
    dept_in: DeptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        new_dept = SysDept(
            parent_id=dept_in.parent_id,
            dept_name=dept_in.dept_name,
            dept_code=dept_in.dept_code,
            leader=dept_in.leader,
            phone=dept_in.phone,
            email=dept_in.email,
            dept_sort=dept_in.dept_sort,
            status=dept_in.status,
            remark=dept_in.remark,
            create_by=current_user.username
        )
        db.add(new_dept)
        await db.commit()
        await db.refresh(new_dept)
        return {'code': 200, 'msg': 'Dept created successfully', 'data': new_dept.to_dict()}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}

@router.put("/")
async def update_dept(
    dept_in: DeptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysDept).where(SysDept.dept_id == dept_in.dept_id)
        result = await db.execute(stmt)
        dept = result.scalar_one_or_none()
        
        if not dept:
            return {'code': 404, 'msg': 'Dept not found'}
            
        if dept_in.parent_id is not None: dept.parent_id = dept_in.parent_id
        if dept_in.dept_name: dept.dept_name = dept_in.dept_name
        if dept_in.dept_code is not None: dept.dept_code = dept_in.dept_code
        if dept_in.leader is not None: dept.leader = dept_in.leader
        if dept_in.phone is not None: dept.phone = dept_in.phone
        if dept_in.email is not None: dept.email = dept_in.email
        if dept_in.dept_sort is not None: dept.dept_sort = dept_in.dept_sort
        if dept_in.status is not None: dept.status = dept_in.status
        if dept_in.remark is not None: dept.remark = dept_in.remark
        
        dept.update_by = current_user.username
        
        await db.commit()
        return {'code': 200, 'msg': 'Dept updated successfully'}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}

@router.delete("/{dept_id}")
async def delete_dept(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        # Check children
        stmt_child = select(SysDept).where(SysDept.parent_id == dept_id)
        res_child = await db.execute(stmt_child)
        if res_child.first():
            return {'code': 400, 'msg': 'Exist child dept, cannot delete'}
            
        # Check user assignment
        stmt_user = select(SysUserDept).where(SysUserDept.dept_id == dept_id)
        res_user = await db.execute(stmt_user)
        if res_user.first():
             return {'code': 400, 'msg': 'Dept contains users, cannot delete'}

        stmt = select(SysDept).where(SysDept.dept_id == dept_id)
        result = await db.execute(stmt)
        dept = result.scalar_one_or_none()
        
        if not dept:
            return {'code': 404, 'msg': 'Dept not found'}
            
        await db.delete(dept)
        await db.commit()
        return {'code': 200, 'msg': 'Dept deleted successfully'}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}
