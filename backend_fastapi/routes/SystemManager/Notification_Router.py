
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, update
from backend_fastapi.db.session import get_db
from backend_fastapi.core.deps import get_current_user
from backend_fastapi.models.sys_models import SysUser, SysNotification
from typing import List, Optional
from datetime import datetime

router = APIRouter(tags=["站内信/通知"])

@router.get("/list")
async def get_notifications(
    page: int = 1,
    page_size: int = 10,
    is_read: Optional[int] = None, # 0: unread, 1: read, None: all
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(SysNotification).where(SysNotification.user_id == current_user.user_id)
    
    if is_read is not None:
        stmt = stmt.where(SysNotification.is_read == is_read)
        
    # Count total
    stmt_count = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(stmt_count)).scalar() or 0
    
    # Pagination
    stmt = stmt.order_by(desc(SysNotification.create_time)).offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(stmt)
    notifications = result.scalars().all()
    
    return {
        'code': 200,
        'msg': 'success',
        'data': {
            'items': [n.to_dict() for n in notifications],
            'total': total,
            'page': page,
            'page_size': page_size
        }
    }

@router.put("/{notification_id}/read")
async def read_notification(
    notification_id: int,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(SysNotification).where(
        SysNotification.notification_id == notification_id,
        SysNotification.user_id == current_user.user_id
    )
    notification = (await db.execute(stmt)).scalar_one_or_none()
    
    if not notification:
        return {'code': 404, 'msg': '通知不存在', 'data': None}
        
    notification.is_read = 1
    notification.read_time = datetime.now()
    await db.commit()
    
    return {'code': 200, 'msg': 'success', 'data': None}

@router.put("/read-all")
async def read_all_notifications(
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = update(SysNotification).where(
        SysNotification.user_id == current_user.user_id,
        SysNotification.is_read == 0
    ).values(
        is_read=1,
        read_time=datetime.now()
    )
    
    await db.execute(stmt)
    await db.commit()
    
    return {'code': 200, 'msg': 'success', 'data': None}

@router.get("/unread-count")
async def get_unread_count(
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(func.count()).where(
        SysNotification.user_id == current_user.user_id,
        SysNotification.is_read == 0
    )
    count = (await db.execute(stmt)).scalar() or 0
    
    return {'code': 200, 'msg': 'success', 'data': count}
