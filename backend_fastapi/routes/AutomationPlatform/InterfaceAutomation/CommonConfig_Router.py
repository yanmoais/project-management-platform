from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend_fastapi.db.session import get_db
from backend_fastapi.models.interface_automation_models import InterfaceCommonConfig

router = APIRouter(tags=["公共配置管理"])

@router.get("/list")
def get_config_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    configs = db.query(InterfaceCommonConfig).offset(skip).limit(limit).all()
    return {"code": 200, "data": [c.to_dict() for c in configs], "msg": "success"}
