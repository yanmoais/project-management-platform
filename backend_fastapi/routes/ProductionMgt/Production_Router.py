from fastapi import APIRouter

router = APIRouter(tags=["投产管理"])

@router.get("/")
async def index():
    return {'code': 200, 'msg': 'success', 'data': 'Hello from 投产管理'}
