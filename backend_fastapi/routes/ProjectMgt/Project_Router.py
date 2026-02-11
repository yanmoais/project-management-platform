from fastapi import APIRouter

router = APIRouter(tags=["项目管理"])

@router.get("/")
async def index():
    return {'code': 200, 'msg': 'success', 'data': 'Hello from 项目管理'}
