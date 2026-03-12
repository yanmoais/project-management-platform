from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update, delete
from sqlalchemy.orm import joinedload
from typing import List, Optional, Union
from datetime import datetime

from backend_fastapi.db.session import get_db
from backend_fastapi.core.deps import get_current_user
from backend_fastapi.models.sys_models import SysUser
from backend_fastapi.models.test_mgt_models import TestCase, PMTestCaseModule
from backend_fastapi.routes.TestMgt.schemas import TestCaseCreate, TestCaseUpdate, TestCaseResponse

router = APIRouter(tags=["测试用例管理"])

@router.get("/list")
async def get_test_case_list(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
    case_name: Optional[str] = None,
    plan_id: Optional[int] = None,
    project_id: Optional[int] = None,
    create_by: Optional[str] = None,
    case_level: Optional[str] = None,
    req_id: Optional[int] = None,
    case_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    case_status: Optional[int] = None,
    case_type: Optional[int] = None
):
    stmt = select(TestCase).order_by(desc(TestCase.create_time))
    
    if case_name:
        stmt = stmt.where(TestCase.case_name.like(f"%{case_name}%"))
        
    if plan_id:
        stmt = stmt.where(TestCase.plan_id == plan_id)
        
    if project_id:
        stmt = stmt.where(TestCase.project_id == project_id)

    if case_level:
        stmt = stmt.where(TestCase.case_level == case_level)

    if case_status is not None:
        stmt = stmt.where(TestCase.case_status == case_status)

    if case_type is not None:
        stmt = stmt.where(TestCase.case_type == case_type)
    
    if req_id:
        stmt = stmt.where(TestCase.req_id == req_id)

    if case_id:
        stmt = stmt.where(TestCase.case_id == case_id)
        
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            stmt = stmt.where(TestCase.create_time >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            stmt = stmt.where(TestCase.create_time <= end_dt)
        except ValueError:
            pass

    if create_by:
        # Check against nickname or username as create_by stores display name
        # If create_by is passed as "me", we check current user
        if create_by == "me":
             stmt = stmt.where(
                 (TestCase.create_by == current_user.nickname) | 
                 (TestCase.create_by == current_user.username)
             )
        else:
             stmt = stmt.where(TestCase.create_by == create_by)
        
    stmt = stmt.options(
        joinedload(TestCase.plan), 
        joinedload(TestCase.project),
        joinedload(TestCase.module),
        joinedload(TestCase.requirement)
    )
    result = await db.execute(stmt)
    cases = result.scalars().all()
    
    return {"code": 200, "msg": "success", "data": [c.to_dict() for c in cases]}

@router.get("/statistics", response_model=dict)
async def get_test_case_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取测试用例统计信息"""
    from sqlalchemy import func, or_
    from backend_fastapi.models.pm_models import PMProject
    
    # 1. 按类型统计
    stmt_type = select(TestCase.case_type, func.count(TestCase.case_id)).group_by(TestCase.case_type)
    result_type = await db.execute(stmt_type)
    type_stats = result_type.all()
    type_data = {t[0]: t[1] for t in type_stats}
    
    # 2. 按项目统计
    stmt_project = select(
        PMProject.project_id,
        PMProject.project_name,
        func.count(TestCase.case_id)
    ).join(
        TestCase, 
        PMProject.project_id == TestCase.project_id
    ).group_by(
        PMProject.project_id, 
        PMProject.project_name
    )
    result_project = await db.execute(stmt_project)
    project_stats = result_project.all()
    projects_data = [{"project_id": p[0], "project_name": p[1], "count": p[2]} for p in project_stats]
    
    # 3. 统计我的用例
    stmt_my = select(func.count(TestCase.case_id)).where(
        or_(
            TestCase.create_by == current_user.nickname,
            TestCase.create_by == current_user.username
        )
    )
    result_my = await db.execute(stmt_my)
    my_count = result_my.scalar() or 0
    
    # 4. 汇总
    total_count = sum(type_data.values())
    
    data = {
        "all": total_count,
        "type_1": type_data.get(1, 0), # 功能
        "type_2": type_data.get(2, 0), # 性能
        "type_3": type_data.get(3, 0), # 安全
        "type_4": type_data.get(4, 0), # 回归
        "my": my_count,
        "projects": projects_data
    }
    
    return {"code": 200, "msg": "success", "data": data}

@router.get("/directory/list")
async def get_test_case_directory_list(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取测试用例目录列表"""
    stmt = select(PMTestCaseModule).order_by(PMTestCaseModule.module_id)
    result = await db.execute(stmt)
    modules = result.scalars().all()
    
    data = [{"value": m.module_id, "label": m.module_name} for m in modules]
    
    return {"code": 200, "msg": "success", "data": data}

# Helper function to handle module creation
async def handle_module_creation(db: AsyncSession, module_val: Optional[Union[int, str]], project_id: Optional[int]) -> Optional[int]:
    if module_val is None:
        return None
    
    if isinstance(module_val, int):
        return module_val
        
    if isinstance(module_val, str):
        # Check if module exists
        stmt = select(PMTestCaseModule).where(PMTestCaseModule.module_name == module_val)
        if project_id:
            stmt = stmt.where(PMTestCaseModule.project_id == project_id)
            
        result = await db.execute(stmt)
        existing_module = result.scalar_one_or_none()
        
        if existing_module:
            return existing_module.module_id
            
        # Create new module
        new_module = PMTestCaseModule(
            module_name=module_val,
            project_id=project_id
        )
        db.add(new_module)
        await db.commit()
        await db.refresh(new_module)
        return new_module.module_id
        
    return None

@router.post("/create")
async def create_test_case(
    case_in: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    # Handle module_id (create if string)
    module_id = await handle_module_creation(db, case_in.module_id, case_in.project_id)

    # Logic to generate case_code
    stmt = select(TestCase.case_code).order_by(desc(TestCase.case_code)).limit(1)
    result = await db.execute(stmt)
    last_case_code = result.scalar_one_or_none()
    
    if last_case_code and last_case_code.isdigit():
        new_case_code = str(int(last_case_code) + 1)
    else:
        new_case_code = "100000001"
        
    new_case = TestCase(
        case_code=new_case_code,
        case_name=case_in.case_name,
        case_type=case_in.case_type,
        case_level=case_in.case_level,
        project_id=case_in.project_id,
        module_id=module_id,
        req_id=case_in.req_id,
        plan_id=case_in.plan_id,
        remark=case_in.remark,
        pre_condition=case_in.pre_condition,
        steps=case_in.steps,
        expected_result=case_in.expected_result,
        create_by=current_user.nickname or current_user.username
    )
    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)
    
    stmt = select(TestCase).options(
        joinedload(TestCase.plan), 
        joinedload(TestCase.project),
        joinedload(TestCase.module),
        joinedload(TestCase.requirement)
    ).where(TestCase.case_id == new_case.case_id)
    result = await db.execute(stmt)
    new_case = result.scalar_one()
    
    return {"code": 200, "msg": "创建成功", "data": new_case.to_dict()}

@router.put("/update")
async def update_test_case(
    case_in: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    stmt = select(TestCase).where(TestCase.case_id == case_in.case_id)
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    
    # Handle module_id if present
    if case_in.module_id is not None:
        case_in.module_id = await handle_module_creation(db, case_in.module_id, case_in.project_id or case.project_id)
        
    update_data = case_in.dict(exclude_unset=True)
    if 'case_id' in update_data:
        del update_data['case_id']
        
    stmt = update(TestCase).where(TestCase.case_id == case_in.case_id).values(**update_data)
    await db.execute(stmt)
    await db.commit()
    
    stmt = select(TestCase).options(
        joinedload(TestCase.plan), 
        joinedload(TestCase.project),
        joinedload(TestCase.module),
        joinedload(TestCase.requirement)
    ).where(TestCase.case_id == case_in.case_id)
    result = await db.execute(stmt)
    updated_case = result.scalar_one()
    
    return {"code": 200, "msg": "更新成功", "data": updated_case.to_dict()}

@router.delete("/delete/{case_id}")
async def delete_test_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    stmt = select(TestCase).where(TestCase.case_id == case_id)
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
        
    await db.delete(case)
    await db.commit()
    return {"code": 200, "msg": "删除成功"}
