from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime

from backend_fastapi.core.deps import get_db, get_current_user
from backend_fastapi.core.security import verify_password, get_password_hash, create_access_token
from backend_fastapi.models.sys_models import SysUser, AppUserLog
from backend_fastapi.routes.Auth.schemas import UserLogin, UserRegister, LoginResponse
from backend_fastapi.core.config import settings

router = APIRouter(tags=["鉴权"])

@router.post("/login", response_model=LoginResponse)
async def login(
    response: Response,
    request: Request,
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录接口
    - 验证邮箱或用户名
    - 验证密码
    - 生成 JWT Token 并放入 Header
    - 记录登录日志
    """
    email = login_data.email
    password = login_data.password
    
    # 查询用户 (邮箱或用户名)
    # 对应原逻辑：SysUser.query.filter_by(email=email).first() or filter_by(username=email).first()
    stmt = select(SysUser).where(
        or_(SysUser.email == email, SysUser.username == email)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        # 这里的 return 格式是为了保持与原前端兼容，FastAPI 默认抛异常会返回 standard error response
        # 但为了 code: 401 这种格式，我们可以直接返回 JSONResponse，或者让 response_model 处理
        # 这里为了简单，如果失败直接抛出 HTTPException 可能更符合 FastAPI 风格，
        # 但为了兼容前端 {code: 401, msg: ...}，我们可能需要自定义 Exception Handler。
        # 暂时先用 JSONResponse 返回错误，这会绕过 response_model 校验。
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=401,
            content={'code': 401, 'msg': '用户不存在'}
        )

    # 验证密码
    if not verify_password(password, user.password):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=401,
            content={'code': 401, 'msg': '密码错误'}
        )

    if user.status == 0:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=403,
            content={'code': 403, 'msg': '账号已禁用'}
        )

    # 生成 Token
    access_token = create_access_token(
        subject=user.username,
        user_id=user.user_id
    )

    # 更新登录信息
    user.login_ip = request.client.host
    user.login_date = datetime.now()
    
    # 记录登录日志
    # 获取 User-Agent
    user_agent_str = request.headers.get('user-agent', '')
    # 简单的解析，实际可能需要 user-agents 库，这里简化处理
    
    login_log = AppUserLog(
        user_id=user.user_id,
        username=user.username,
        login_ip=request.client.host,
        login_type=1,
        login_status=1,
        login_time=datetime.now(),
        device=user_agent_str[:50] # 截断
    )
    db.add(login_log)
    await db.commit()
    await db.refresh(user)

    # 设置 Header
    response.headers['Authorization'] = f'Bearer {access_token}'
    response.headers['Access-Control-Expose-Headers'] = 'Authorization'
    
    return {
        'code': 200,
        'msg': 'Login successful',
        'data': user.to_dict()
    }

@router.post("/register")
async def register(
    register_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册接口
    """
    username = register_data.name
    email = register_data.email
    password = register_data.password

    # 检查用户名
    stmt = select(SysUser).where(SysUser.username == username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=400, content={'code': 400, 'msg': '用户名已存在'})
    
    # 检查邮箱
    stmt = select(SysUser).where(SysUser.email == email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=400, content={'code': 400, 'msg': '邮箱已注册'})

    hashed_password = get_password_hash(password)
    
    new_user = SysUser(
        username=username,
        nickname=username,
        email=email,
        password=hashed_password,
        status=1,
        create_time=datetime.now()
    )
    
    db.add(new_user)
    await db.commit()
    
    return {'code': 200, 'msg': '注册成功'}

@router.get("/user/info")
async def get_user_info(
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取用户信息接口
    """
    # 模拟角色逻辑，与原代码一致
    roles = ['admin'] if current_user.username == 'admin' else ['common']
    
    return {
        'code': 200,
        'data': {
            'name': current_user.nickname,
            'avatar': current_user.avatar,
            'roles': roles,
            'permissions': ['*:*:*'] if 'admin' in roles else []
        }
    }

@router.post("/logout")
async def logout(
    request: Request,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登出接口
    """
    # 查找最近一次未登出的日志
    stmt = select(AppUserLog).where(
        AppUserLog.user_id == current_user.user_id,
        AppUserLog.login_status == 1,
        AppUserLog.logout_time == None
    ).order_by(AppUserLog.login_time.desc()).limit(1)
    
    result = await db.execute(stmt)
    last_login_log = result.scalar_one_or_none()
    
    if last_login_log:
        now = datetime.now()
        last_login_log.logout_time = now
        if last_login_log.login_time:
            duration = (now - last_login_log.login_time).total_seconds()
            last_login_log.online_duration = int(duration)
        await db.commit()
        
    return {'code': 200, 'msg': '登出成功'}
