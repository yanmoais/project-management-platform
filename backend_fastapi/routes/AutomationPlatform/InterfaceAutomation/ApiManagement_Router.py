from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend_fastapi.db.session import get_db
from backend_fastapi.models.interface_automation_models import InterfaceDefinition

router = APIRouter(tags=["API接口管理"])

@router.get("/list")
def get_api_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    apis = db.query(InterfaceDefinition).offset(skip).limit(limit).all()
    return {"code": 200, "data": [a.to_dict() for a in apis], "msg": "success"}
