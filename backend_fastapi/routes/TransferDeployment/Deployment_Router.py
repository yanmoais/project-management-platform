from fastapi import APIRouter

router = APIRouter(tags=["移交部署"])

@router.get("/")
async def index():
    return {'code': 200, 'msg': 'success', 'data': 'Hello from 移交部署'}
