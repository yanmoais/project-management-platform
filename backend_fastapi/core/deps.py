from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from backend_fastapi.db.session import AsyncSessionLocal
from backend_fastapi.core.config import settings
from backend_fastapi.models.sys_models import SysUser
from sqlalchemy import select

async def get_db() -> Generator:
    """
    获取数据库会话依赖
    """
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> SysUser:
    """
    获取当前登录用户
    解析 Authorization Header (Bearer <token>)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not authorization:
        raise credentials_exception
        
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise credentials_exception
            
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValueError):
        raise credentials_exception
        
    # 查询用户
    result = await db.execute(select(SysUser).where(SysUser.user_id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user
