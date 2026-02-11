from fastapi import APIRouter

router = APIRouter(tags=["工作台"])

@router.get("/")
async def index():
    return {'code': 200, 'msg': 'success', 'data': 'Hello from 工作台'}
