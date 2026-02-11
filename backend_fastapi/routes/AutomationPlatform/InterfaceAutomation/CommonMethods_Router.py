from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend_fastapi.db.session import get_db
from backend_fastapi.models.interface_automation_models import InterfaceCommonMethod

router = APIRouter()

@router.get("/method/list")
def get_method_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    methods = db.query(InterfaceCommonMethod).offset(skip).limit(limit).all()
    return {"code": 200, "data": [m.to_dict() for m in methods], "msg": "success"}
