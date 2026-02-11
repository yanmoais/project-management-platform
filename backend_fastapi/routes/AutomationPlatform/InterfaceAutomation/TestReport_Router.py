from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend_fastapi.db.session import get_db
from backend_fastapi.models.interface_automation_models import InterfaceReport

router = APIRouter()

@router.get("/report/list")
def get_report_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reports = db.query(InterfaceReport).offset(skip).limit(limit).all()
    return {"code": 200, "data": [r.to_dict() for r in reports], "msg": "success"}
