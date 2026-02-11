from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from backend_fastapi.core.deps import get_db, get_current_user
from backend_fastapi.models.sys_models import SysMenu, SysUser, SysRoleMenu
from backend_fastapi.routes.SystemManager.schemas import MenuCreate, MenuUpdate, MenuResponse
from typing import List, Optional

router = APIRouter(tags=["菜单管理"])

def build_menu_tree(menus, parent_id=0):
    tree = []
    for menu in menus:
        if menu.parent_id == parent_id:
            children = build_menu_tree(menus, menu.menu_id)
            menu_dict = menu.to_dict()
            if children:
                menu_dict['children'] = children
            tree.append(menu_dict)
    return tree

@router.get("/list")
async def list_menus(
    menu_name: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysMenu).order_by(SysMenu.menu_sort)
        
        if menu_name:
            stmt = stmt.where(SysMenu.menu_name.like(f"%{menu_name}%"))
        if status is not None:
            stmt = stmt.where(SysMenu.status == status)
            
        result = await db.execute(stmt)
        menus = result.scalars().all()
        
        # If searching, return flat list; otherwise tree?
        # Typically management table shows tree.
        # But if search criteria is present, tree might be broken.
        # Let's return flat list for now, frontend often handles tree transformation or expects flat list with parent_id.
        # But wait, Element Plus Table tree props.
        
        if menu_name:
             return {'code': 200, 'msg': 'Success', 'data': [m.to_dict() for m in menus]}
        
        # Build tree
        # tree = build_menu_tree(menus)
        # return {'code': 200, 'msg': 'Success', 'data': tree}
        
        # Return flat list, easier for frontend to handle if it supports it, or let frontend build tree
        return {'code': 200, 'msg': 'Success', 'data': [m.to_dict() for m in menus]}
    except Exception as e:
        return {'code': 500, 'msg': str(e)}

@router.get("/{menu_id}")
async def get_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysMenu).where(SysMenu.menu_id == menu_id)
        result = await db.execute(stmt)
        menu = result.scalar_one_or_none()
        
        if not menu:
            return {'code': 404, 'msg': 'Menu not found'}
            
        return {'code': 200, 'msg': 'Success', 'data': menu.to_dict()}
    except Exception as e:
        return {'code': 500, 'msg': str(e)}

@router.post("/")
async def create_menu(
    menu_in: MenuCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        new_menu = SysMenu(
            parent_id=menu_in.parent_id,
            menu_name=menu_in.menu_name,
            menu_type=menu_in.menu_type,
            path=menu_in.path,
            component=menu_in.component,
            query=menu_in.query,
            is_frame=menu_in.is_frame,
            is_cache=menu_in.is_cache,
            menu_icon=menu_in.menu_icon,
            menu_key=menu_in.menu_key,
            menu_sort=menu_in.menu_sort,
            status=menu_in.status,
            remark=menu_in.remark,
            create_by=current_user.username
        )
        db.add(new_menu)
        await db.commit()
        await db.refresh(new_menu)
        return {'code': 200, 'msg': 'Menu created successfully', 'data': new_menu.to_dict()}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}

@router.put("/")
async def update_menu(
    menu_in: MenuUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysMenu).where(SysMenu.menu_id == menu_in.menu_id)
        result = await db.execute(stmt)
        menu = result.scalar_one_or_none()
        
        if not menu:
            return {'code': 404, 'msg': 'Menu not found'}
            
        if menu_in.parent_id is not None: menu.parent_id = menu_in.parent_id
        if menu_in.menu_name: menu.menu_name = menu_in.menu_name
        if menu_in.menu_type: menu.menu_type = menu_in.menu_type
        if menu_in.path is not None: menu.path = menu_in.path
        if menu_in.component is not None: menu.component = menu_in.component
        if menu_in.query is not None: menu.query = menu_in.query
        if menu_in.is_frame is not None: menu.is_frame = menu_in.is_frame
        if menu_in.is_cache is not None: menu.is_cache = menu_in.is_cache
        if menu_in.menu_icon is not None: menu.menu_icon = menu_in.menu_icon
        if menu_in.menu_key is not None: menu.menu_key = menu_in.menu_key
        if menu_in.menu_sort is not None: menu.menu_sort = menu_in.menu_sort
        if menu_in.status is not None: menu.status = menu_in.status
        if menu_in.remark is not None: menu.remark = menu_in.remark
        
        menu.update_by = current_user.username
        
        await db.commit()
        return {'code': 200, 'msg': 'Menu updated successfully'}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}

@router.delete("/{menu_id}")
async def delete_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        # Check children
        stmt_child = select(SysMenu).where(SysMenu.parent_id == menu_id)
        res_child = await db.execute(stmt_child)
        if res_child.first():
            return {'code': 400, 'msg': 'Exist child menu, cannot delete'}
            
        stmt = select(SysMenu).where(SysMenu.menu_id == menu_id)
        result = await db.execute(stmt)
        menu = result.scalar_one_or_none()
        
        if not menu:
            return {'code': 404, 'msg': 'Menu not found'}
            
        # Delete associations
        from sqlalchemy import delete
        await db.execute(delete(SysRoleMenu).where(SysRoleMenu.menu_id == menu_id))
        
        await db.delete(menu)
        await db.commit()
        return {'code': 200, 'msg': 'Menu deleted successfully'}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}
