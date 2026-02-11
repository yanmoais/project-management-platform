from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend_fastapi.db.session import get_db
from backend_fastapi.models.interface_automation_models import InterfaceProject
from backend_fastapi.core.deps import get_current_user
from typing import List

router = APIRouter()

@router.get("/project/list")
def get_project_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(InterfaceProject).offset(skip).limit(limit).all()
    return {"code": 200, "data": [p.to_dict() for p in projects], "msg": "success"}

@router.post("/project")
def create_project(name: str, description: str = None, db: Session = Depends(get_db)):
    project = InterfaceProject(name=name, description=description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"code": 200, "data": project.to_dict(), "msg": "success"}

@router.put("/project")
def update_project(id: int, name: str, description: str = None, db: Session = Depends(get_db)):
    project = db.query(InterfaceProject).filter(InterfaceProject.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.name = name
    project.description = description
    db.commit()
    return {"code": 200, "data": project.to_dict(), "msg": "success"}

@router.delete("/project/{id}")
def delete_project(id: int, db: Session = Depends(get_db)):
    project = db.query(InterfaceProject).filter(InterfaceProject.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"code": 200, "msg": "success"}
