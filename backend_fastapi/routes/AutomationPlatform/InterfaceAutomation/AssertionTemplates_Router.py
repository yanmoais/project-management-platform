from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend_fastapi.db.session import get_db
from backend_fastapi.models.interface_automation_models import InterfaceAssertionTemplate

router = APIRouter()

@router.get("/assertion/list")
def get_assertion_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    templates = db.query(InterfaceAssertionTemplate).offset(skip).limit(limit).all()
    return {"code": 200, "data": [t.to_dict() for t in templates], "msg": "success"}
