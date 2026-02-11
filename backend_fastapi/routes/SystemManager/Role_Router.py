from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from backend_fastapi.core.deps import get_db, get_current_user
from backend_fastapi.models.sys_models import SysRole, SysUser, SysRoleMenu, SysUserRole
from backend_fastapi.routes.SystemManager.schemas import RoleCreate, RoleUpdate, RoleResponse
from backend_fastapi.utils.LogManeger import log_info
from typing import List, Optional

router = APIRouter(tags=["角色管理"])

@router.get("/list")
async def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    role_name: Optional[str] = None,
    role_key: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysRole)
        
        if role_name:
            stmt = stmt.where(SysRole.role_name.like(f"%{role_name}%"))
        if role_key:
            stmt = stmt.where(SysRole.role_key.like(f"%{role_key}%"))
        if status is not None:
            stmt = stmt.where(SysRole.status == status)
            
        stmt = stmt.order_by(SysRole.role_sort)
        
        # Pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        roles = result.scalars().all()
        
        return {
            'code': 200,
            'msg': 'Success',
            'data': {
                'list': [r.to_dict() for r in roles],
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }
    except Exception as e:
        return {'code': 500, 'msg': str(e)}

@router.get("/{role_id}")
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysRole).where(SysRole.role_id == role_id)
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not role:
            return {'code': 404, 'msg': 'Role not found'}
            
        data = role.to_dict()
        
        # Get Menu IDs
        stmt_menu = select(SysRoleMenu.menu_id).where(SysRoleMenu.role_id == role_id)
        res_menu = await db.execute(stmt_menu)
        data['menu_ids'] = res_menu.scalars().all()
        
        return {'code': 200, 'msg': 'Success', 'data': data}
    except Exception as e:
        return {'code': 500, 'msg': str(e)}

@router.post("/")
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        # Check name/key unique
        stmt = select(SysRole).where((SysRole.role_name == role_in.role_name) | (SysRole.role_key == role_in.role_key))
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
            return {'code': 400, 'msg': "Role name or key already exists"}
            
        new_role = SysRole(
            role_name=role_in.role_name,
            role_key=role_in.role_key,
            role_sort=role_in.role_sort,
            data_scope=role_in.data_scope,
            status=role_in.status,
            remark=role_in.remark,
            create_by=current_user.username
        )
        db.add(new_role)
        await db.commit()
        await db.refresh(new_role)
        
        # Add Menus
        if role_in.menu_ids:
            for mid in role_in.menu_ids:
                rm = SysRoleMenu(role_id=new_role.role_id, menu_id=mid)
                db.add(rm)
                
        await db.commit()
        return {'code': 200, 'msg': 'Role created successfully', 'data': new_role.to_dict()}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}

@router.put("/")
async def update_role(
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysRole).where(SysRole.role_id == role_in.role_id)
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not role:
            return {'code': 404, 'msg': 'Role not found'}
            
        if role_in.role_name: role.role_name = role_in.role_name
        if role_in.role_key: role.role_key = role_in.role_key
        if role_in.role_sort is not None: role.role_sort = role_in.role_sort
        if role_in.data_scope is not None: role.data_scope = role_in.data_scope
        if role_in.status is not None: role.status = role_in.status
        if role_in.remark is not None: role.remark = role_in.remark
        
        role.update_by = current_user.username
        
        # Update Menus
        if role_in.menu_ids is not None:
            from sqlalchemy import delete
            await db.execute(delete(SysRoleMenu).where(SysRoleMenu.role_id == role.role_id))
            for mid in role_in.menu_ids:
                rm = SysRoleMenu(role_id=role.role_id, menu_id=mid)
                db.add(rm)
                
        await db.commit()
        return {'code': 200, 'msg': 'Role updated successfully'}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}

@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysRole).where(SysRole.role_id == role_id)
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not role:
            return {'code': 404, 'msg': 'Role not found'}
            
        if role.role_key == 'admin':
             return {'code': 403, 'msg': 'Cannot delete admin role'}
             
        # Check assignment
        stmt_check = select(SysUserRole).where(SysUserRole.role_id == role_id)
        res_check = await db.execute(stmt_check)
        if res_check.first():
            return {'code': 400, 'msg': 'Role is assigned to users'}
            
        # Delete associations
        from sqlalchemy import delete
        await db.execute(delete(SysRoleMenu).where(SysRoleMenu.role_id == role_id))
        
        await db.delete(role)
        await db.commit()
        return {'code': 200, 'msg': 'Role deleted successfully'}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}
