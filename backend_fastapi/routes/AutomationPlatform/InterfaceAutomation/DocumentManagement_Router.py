from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend_fastapi.db.session import get_db
from backend_fastapi.models.interface_automation_models import InterfaceDocument

router = APIRouter()

@router.get("/document/list")
def get_document_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    docs = db.query(InterfaceDocument).offset(skip).limit(limit).all()
    return {"code": 200, "data": [d.to_dict() for d in docs], "msg": "success"}
