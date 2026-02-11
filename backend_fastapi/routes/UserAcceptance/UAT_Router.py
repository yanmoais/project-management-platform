from fastapi import APIRouter

router = APIRouter(tags=["用户验收"])

@router.get("/")
async def index():
    return {'code': 200, 'msg': 'success', 'data': 'Hello from 用户验收'}
