from fastapi import APIRouter

router = APIRouter(tags=["通知管理"])

@router.get("/list")
async def list_notices():
    return {'code': 200, 'msg': 'Success', 'data': []}
