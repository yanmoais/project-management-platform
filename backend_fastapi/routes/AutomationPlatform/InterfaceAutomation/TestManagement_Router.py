from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend_fastapi.db.session import get_db
from backend_fastapi.models.interface_automation_models import InterfaceTestPlan

router = APIRouter(tags=["测试计划管理"])

@router.get("/list")
def get_test_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    plans = db.query(InterfaceTestPlan).offset(skip).limit(limit).all()
    return {"code": 200, "data": [p.to_dict() for p in plans], "msg": "success"}
