from fastapi import APIRouter

router = APIRouter(tags=["我的空间"])

@router.get("/")
async def index():
    return {'code': 200, 'msg': 'success', 'data': 'Hello from 我的空间'}
