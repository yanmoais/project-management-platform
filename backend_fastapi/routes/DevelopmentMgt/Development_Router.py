from fastapi import APIRouter

router = APIRouter(tags=["研发管理"])

@router.get("/")
async def index():
    return {'code': 200, 'msg': 'success', 'data': 'Hello from 研发管理'}
