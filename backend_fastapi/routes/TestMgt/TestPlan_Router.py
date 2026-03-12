from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update, delete, func, case, distinct
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime

from backend_fastapi.db.session import get_db
from backend_fastapi.core.deps import get_current_user
from backend_fastapi.models.sys_models import SysUser
from backend_fastapi.models.test_mgt_models import TestPlan, TestCase
from backend_fastapi.models.pm_models import PMDefect
from backend_fastapi.routes.TestMgt.schemas import TestPlanCreate, TestPlanUpdate, TestPlanResponse

router = APIRouter(tags=["测试计划管理"])

@router.get("/list", response_model=List[TestPlanResponse])
async def get_test_plan_list(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
    status: Optional[int] = None,
    plan_name: Optional[str] = None,
    project_id: Optional[int] = None,
    owner_id: Optional[int] = None,
    version: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    stmt = select(TestPlan).order_by(desc(TestPlan.create_time))
    
    if status is not None:
        stmt = stmt.where(TestPlan.status == status)
    
    if plan_name:
        stmt = stmt.where(TestPlan.plan_name.like(f"%{plan_name}%"))
        
    if project_id:
        stmt = stmt.where(TestPlan.project_id == project_id)
        
    if owner_id:
        stmt = stmt.where(TestPlan.owner_id == owner_id)

    if version:
        stmt = stmt.where(TestPlan.version == version)

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            stmt = stmt.where(TestPlan.create_time >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            stmt = stmt.where(TestPlan.create_time <= end_dt)
        except ValueError:
            pass
        
    stmt = stmt.options(joinedload(TestPlan.owner)).options(joinedload(TestPlan.project))
    result = await db.execute(stmt)
    plans = result.scalars().all()
    
    if not plans:
        return []

    plan_ids = [p.plan_id for p in plans]
    
    # 统计用例数据
    stmt_cases = select(
        TestCase.plan_id,
        func.count(TestCase.case_id).label('total'),
        func.sum(case((TestCase.case_status == 1, 1), else_=0)).label('passed'),
        func.sum(case((TestCase.case_status == 4, 1), else_=0)).label('leftover')
    ).where(TestCase.plan_id.in_(plan_ids)).group_by(TestCase.plan_id)
    
    result_cases = await db.execute(stmt_cases)
    case_stats = {row.plan_id: row for row in result_cases}
    
    # 统计缺陷数据
    stmt_defects = select(
        TestCase.plan_id,
        func.count(PMDefect.defect_id).label('total'),
        func.sum(case((PMDefect.status.in_(['Closed', 'Rejected']), 1), else_=0)).label('closed')
    ).join(TestCase, PMDefect.case_id == TestCase.case_id)\
     .where(TestCase.plan_id.in_(plan_ids))\
     .group_by(TestCase.plan_id)
     
    result_defects = await db.execute(stmt_defects)
    defect_stats = {row.plan_id: row for row in result_defects}
    
    response = []
    for p in plans:
        p_dict = p.to_dict()
        c_stat = case_stats.get(p.plan_id, None)
        d_stat = defect_stats.get(p.plan_id, None)
        
        total_cases = c_stat.total if c_stat else 0
        passed = c_stat.passed if c_stat else 0
        leftover = c_stat.leftover if c_stat else 0
        
        total_defects = d_stat.total if d_stat else 0
        closed_defects = d_stat.closed if d_stat else 0
        
        denominator = total_cases + total_defects
        numerator = passed + leftover + closed_defects
        
        p_dict['progress'] = round((numerator / denominator * 100), 2) if denominator > 0 else 0
        response.append(p_dict)
        
    return response

@router.get("/versions", response_model=dict)
async def get_test_plan_versions(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取所有测试计划的版本列表"""
    stmt = select(distinct(TestPlan.version)).where(TestPlan.version.is_not(None))
    result = await db.execute(stmt)
    versions = result.scalars().all()
    # Filter out empty strings if any
    version_list = [v for v in versions if v]
    return {"code": 200, "data": version_list, "msg": "success"}

@router.get("/statistics", response_model=dict)
async def get_test_plan_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取测试计划统计信息"""
    from sqlalchemy import func
    from backend_fastapi.models.pm_models import PMProject
    
    # 1. 按状态统计
    stmt_status = select(TestPlan.status, func.count(TestPlan.plan_id)).group_by(TestPlan.status)
    result_status = await db.execute(stmt_status)
    status_stats = result_status.all()
    status_data = {s[0]: s[1] for s in status_stats}
    
    # 2. 按项目统计
    stmt_project = select(
        PMProject.project_id,
        PMProject.project_name,
        func.count(TestPlan.plan_id)
    ).join(
        TestPlan, 
        PMProject.project_id == TestPlan.project_id
    ).group_by(
        PMProject.project_id, 
        PMProject.project_name
    )
    result_project = await db.execute(stmt_project)
    project_stats = result_project.all()
    projects_data = [{"project_id": p[0], "project_name": p[1], "count": p[2]} for p in project_stats]
    
    # 3. 统计我的计划
    stmt_my = select(func.count(TestPlan.plan_id)).where(TestPlan.owner_id == current_user.user_id)
    result_my = await db.execute(stmt_my)
    my_count = result_my.scalar() or 0
    
    # 4. 汇总
    total_count = sum(status_data.values())
    
    data = {
        "all": total_count,
        "running": status_data.get(1, 0),
        "closed": status_data.get(0, 0),
        "my": my_count,
        "projects": projects_data
    }
    
    return {"code": 200, "msg": "success", "data": data}

@router.post("/create", response_model=TestPlanResponse)
async def create_test_plan(
    plan_in: TestPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    new_plan = TestPlan(
        plan_name=plan_in.plan_name,
        version=plan_in.version,
        status=plan_in.status,
        project_id=plan_in.project_id,
        owner_id=plan_in.owner_id,
        start_time=plan_in.start_time,
        end_time=plan_in.end_time,
        remark=plan_in.remark,
        create_by=current_user.nickname or current_user.username,
        associated_case_ids=plan_in.associated_case_ids
    )
    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)
    
    # Update TestCase.plan_id if associated_case_ids is provided
    if plan_in.associated_case_ids:
        stmt = update(TestCase).where(TestCase.case_id.in_(plan_in.associated_case_ids)).values(plan_id=new_plan.plan_id)
        await db.execute(stmt)
        await db.commit()
    
    stmt = select(TestPlan).options(joinedload(TestPlan.owner)).options(joinedload(TestPlan.project)).where(TestPlan.plan_id == new_plan.plan_id)
    result = await db.execute(stmt)
    new_plan = result.scalar_one()
    
    return new_plan.to_dict()

@router.put("/update", response_model=TestPlanResponse)
async def update_test_plan(
    plan_in: TestPlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    stmt = select(TestPlan).where(TestPlan.plan_id == plan_in.plan_id)
    result = await db.execute(stmt)
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=404, detail="测试计划不存在")
        
    update_data = plan_in.dict(exclude_unset=True)
    if 'plan_id' in update_data:
        del update_data['plan_id']
        
    stmt = update(TestPlan).where(TestPlan.plan_id == plan_in.plan_id).values(**update_data)
    await db.execute(stmt)
    
    # Update TestCase.plan_id if associated_case_ids is in update_data
    if 'associated_case_ids' in update_data:
        case_ids = update_data['associated_case_ids'] or []
        
        # Set plan_id for new cases
        if case_ids:
            stmt = update(TestCase).where(TestCase.case_id.in_(case_ids)).values(plan_id=plan.plan_id)
            await db.execute(stmt)
        
        # Set plan_id to NULL for removed cases
        if case_ids:
             stmt = update(TestCase).where(TestCase.plan_id == plan.plan_id).where(TestCase.case_id.notin_(case_ids)).values(plan_id=None)
        else:
             stmt = update(TestCase).where(TestCase.plan_id == plan.plan_id).values(plan_id=None)
        await db.execute(stmt)
        
    await db.commit()
    
    stmt = select(TestPlan).options(joinedload(TestPlan.owner)).options(joinedload(TestPlan.project)).where(TestPlan.plan_id == plan_in.plan_id)
    result = await db.execute(stmt)
    updated_plan = result.scalar_one()
    
    return updated_plan.to_dict()

@router.delete("/delete/{plan_id}")
async def delete_test_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    stmt = select(TestPlan).where(TestPlan.plan_id == plan_id)
    result = await db.execute(stmt)
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=404, detail="测试计划不存在")
        
    await db.delete(plan)
    await db.commit()
    return {"code": 200, "msg": "删除成功"}
