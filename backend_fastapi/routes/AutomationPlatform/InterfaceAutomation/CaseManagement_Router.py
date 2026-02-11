from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend_fastapi.db.session import get_db
from backend_fastapi.models.interface_automation_models import InterfaceCase
from typing import List

router = APIRouter(tags=["用例管理"])

@router.get("/list")
def get_case_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cases = db.query(InterfaceCase).offset(skip).limit(limit).all()
    return {"code": 200, "data": [c.to_dict() for c in cases], "msg": "success"}
