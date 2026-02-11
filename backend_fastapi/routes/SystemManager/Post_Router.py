from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from backend_fastapi.core.deps import get_db, get_current_user
from backend_fastapi.models.sys_models import SysPost, SysUser, SysUserPost
from backend_fastapi.routes.SystemManager.schemas import PostCreate, PostUpdate, PostResponse
from typing import List, Optional

router = APIRouter(tags=["岗位管理"])

@router.get("/list")
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    post_code: Optional[str] = None,
    post_name: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysPost).order_by(SysPost.post_sort)
        
        if post_code:
            stmt = stmt.where(SysPost.post_code.like(f"%{post_code}%"))
        if post_name:
            stmt = stmt.where(SysPost.post_name.like(f"%{post_name}%"))
        if status is not None:
            stmt = stmt.where(SysPost.status == status)
            
        # Pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        posts = result.scalars().all()
        
        return {
            'code': 200,
            'msg': 'Success',
            'data': {
                'list': [p.to_dict() for p in posts],
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }
    except Exception as e:
        return {'code': 500, 'msg': str(e)}

@router.get("/{post_id}")
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysPost).where(SysPost.post_id == post_id)
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()
        
        if not post:
            return {'code': 404, 'msg': 'Post not found'}
            
        return {'code': 200, 'msg': 'Success', 'data': post.to_dict()}
    except Exception as e:
        return {'code': 500, 'msg': str(e)}

@router.post("/")
async def create_post(
    post_in: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        # Check code/name unique
        stmt = select(SysPost).where((SysPost.post_code == post_in.post_code) | (SysPost.post_name == post_in.post_name))
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
             return {'code': 400, 'msg': 'Post code or name already exists'}

        new_post = SysPost(
            post_code=post_in.post_code,
            post_name=post_in.post_name,
            post_sort=post_in.post_sort,
            status=post_in.status,
            remark=post_in.remark,
            create_by=current_user.username
        )
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)
        return {'code': 200, 'msg': 'Post created successfully', 'data': new_post.to_dict()}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}

@router.put("/")
async def update_post(
    post_in: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        stmt = select(SysPost).where(SysPost.post_id == post_in.post_id)
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()
        
        if not post:
            return {'code': 404, 'msg': 'Post not found'}
            
        if post_in.post_code: post.post_code = post_in.post_code
        if post_in.post_name: post.post_name = post_in.post_name
        if post_in.post_sort is not None: post.post_sort = post_in.post_sort
        if post_in.status is not None: post.status = post_in.status
        if post_in.remark is not None: post.remark = post_in.remark
        
        post.update_by = current_user.username
        
        await db.commit()
        return {'code': 200, 'msg': 'Post updated successfully'}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}

@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    try:
        # Check assignment
        stmt_check = select(SysUserPost).where(SysUserPost.post_id == post_id)
        res_check = await db.execute(stmt_check)
        if res_check.first():
            return {'code': 400, 'msg': 'Post is assigned to users'}
            
        stmt = select(SysPost).where(SysPost.post_id == post_id)
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()
        
        if not post:
            return {'code': 404, 'msg': 'Post not found'}
            
        await db.delete(post)
        await db.commit()
        return {'code': 200, 'msg': 'Post deleted successfully'}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'msg': str(e)}
