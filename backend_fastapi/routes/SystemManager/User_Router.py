from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from backend_fastapi.core.deps import get_db, get_current_user
from backend_fastapi.models.sys_models import SysUser, SysUserRole, SysRole, SysUserPost, SysPost, SysUserDept, SysDept
from backend_fastapi.routes.SystemManager.schemas import UserCreate, UserUpdate, UserResponse
from backend_fastapi.utils.LogManeger import log_info
from typing import List, Optional
from werkzeug.security import generate_password_hash

router = APIRouter(tags=["用户管理"])

@router.get("/list")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    username: Optional[str] = None,
    mobile: Optional[str] = None,
    status: Optional[int] = None,
    dept_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysUser)
        
        if username:
            stmt = stmt.where(SysUser.username.like(f"%{username}%"))
        if mobile:
            stmt = stmt.where(SysUser.mobile.like(f"%{mobile}%"))
        if status is not None:
            stmt = stmt.where(SysUser.status == status)
        if dept_id:
            # Subquery to find users in this dept
            sub_stmt = select(SysUserDept.user_id).where(SysUserDept.dept_id == dept_id)
            stmt = stmt.where(SysUser.user_id.in_(sub_stmt))
            
        stmt = stmt.order_by(desc(SysUser.create_time))
        
        # Pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        user_list = []
        for u in users:
            u_dict = u.to_dict()
            # Fetch dept
            dept_stmt = select(SysDept).join(SysUserDept, SysUserDept.dept_id == SysDept.dept_id).where(SysUserDept.user_id == u.user_id)
            dept_res = await db.execute(dept_stmt)
            dept = dept_res.scalar_one_or_none()
            if dept:
                u_dict['dept'] = dept.to_dict()
                u_dict['dept_id'] = dept.dept_id
            user_list.append(u_dict)
            
        return {
            'code': 200,
            'msg': 'Success',
            'data': {
                'list': user_list,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }
    except Exception as e:
        log_info(f"List users error: {str(e)}")
        return {'code': 500, 'msg': str(e)}

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysUser).where(SysUser.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return {'code': 404, 'msg': 'User not found'}
            
        data = user.to_dict()
        
        # Get Roles
        stmt_roles = select(SysRole.role_id).join(SysUserRole).where(SysUserRole.user_id == user_id)
        res_roles = await db.execute(stmt_roles)
        data['role_ids'] = res_roles.scalars().all()
        
        # Get Posts
        stmt_posts = select(SysPost.post_id).join(SysUserPost).where(SysUserPost.user_id == user_id)
        res_posts = await db.execute(stmt_posts)
        data['post_ids'] = res_posts.scalars().all()
        
        # Get Dept
        stmt_dept = select(SysUserDept.dept_id).where(SysUserDept.user_id == user_id)
        res_dept = await db.execute(stmt_dept)
        dept_id = res_dept.scalar_one_or_none()
        data['dept_id'] = dept_id
        
        return {'code': 200, 'msg': 'Success', 'data': data}
    except Exception as e:
        return {'code': 500, 'msg': str(e)}

@router.post("/")
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        # Check username exists
        stmt = select(SysUser).where(SysUser.username == user_in.username)
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
            return {'code': 400, 'msg': f"Username {user_in.username} already exists"}
            
        hashed_password = generate_password_hash(user_in.password)
        
        new_user = SysUser(
            username=user_in.username,
            password=hashed_password,
            nickname=user_in.nickname,
            email=user_in.email,
            mobile=user_in.mobile,
            gender=user_in.gender,
            status=user_in.status,
            remark=user_in.remark,
            create_by=current_user.username
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Add Roles
        if user_in.role_ids:
            for rid in user_in.role_ids:
                ur = SysUserRole(user_id=new_user.user_id, role_id=rid)
                db.add(ur)
                
        # Add Posts
        if user_in.post_ids:
            for pid in user_in.post_ids:
                up = SysUserPost(user_id=new_user.user_id, post_id=pid)
                db.add(up)
                
        # Add Dept
        if user_in.dept_id:
            ud = SysUserDept(user_id=new_user.user_id, dept_id=user_in.dept_id)
            db.add(ud)
            
        await db.commit()
        
        return {'code': 200, 'msg': 'User created successfully', 'data': new_user.to_dict()}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}

@router.put("/")
async def update_user(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysUser).where(SysUser.user_id == user_in.user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return {'code': 404, 'msg': 'User not found'}
            
        if user_in.nickname is not None: user.nickname = user_in.nickname
        if user_in.email is not None: user.email = user_in.email
        if user_in.mobile is not None: user.mobile = user_in.mobile
        if user_in.gender is not None: user.gender = user_in.gender
        if user_in.status is not None: user.status = user_in.status
        if user_in.remark is not None: user.remark = user_in.remark
        if user_in.password:
             user.password = generate_password_hash(user_in.password)
             
        user.update_by = current_user.username
        
        # Update Roles
        if user_in.role_ids is not None:
            # Delete old
            await db.execute(select(SysUserRole).where(SysUserRole.user_id == user.user_id).execution_options(synchronize_session=False))
            # Delete logic in async sqlalchemy is tricky if not using delete(), let's use explicit delete stmt
            from sqlalchemy import delete
            await db.execute(delete(SysUserRole).where(SysUserRole.user_id == user.user_id))
            
            for rid in user_in.role_ids:
                ur = SysUserRole(user_id=user.user_id, role_id=rid)
                db.add(ur)

        # Update Posts
        if user_in.post_ids is not None:
            from sqlalchemy import delete
            await db.execute(delete(SysUserPost).where(SysUserPost.user_id == user.user_id))
            for pid in user_in.post_ids:
                up = SysUserPost(user_id=user.user_id, post_id=pid)
                db.add(up)

        # Update Dept
        if user_in.dept_id is not None:
            from sqlalchemy import delete
            await db.execute(delete(SysUserDept).where(SysUserDept.user_id == user.user_id))
            ud = SysUserDept(user_id=user.user_id, dept_id=user_in.dept_id)
            db.add(ud)
            
        await db.commit()
        return {'code': 200, 'msg': 'User updated successfully'}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysUser).where(SysUser.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return {'code': 404, 'msg': 'User not found'}
            
        if user.user_id == 1:
             return {'code': 403, 'msg': 'Cannot delete admin user'}
             
        # Delete associations
        from sqlalchemy import delete
        await db.execute(delete(SysUserRole).where(SysUserRole.user_id == user_id))
        await db.execute(delete(SysUserPost).where(SysUserPost.user_id == user_id))
        await db.execute(delete(SysUserDept).where(SysUserDept.user_id == user_id))
        
        await db.delete(user)
        await db.commit()
        return {'code': 200, 'msg': 'User deleted successfully'}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}
