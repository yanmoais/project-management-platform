from fastapi import APIRouter

router = APIRouter(tags=["生产问题"])

@router.get("/")
async def index():
    return {'code': 200, 'msg': 'success', 'data': 'Hello from 生产问题'}
