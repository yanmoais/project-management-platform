from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func, or_
from typing import List, Optional
from datetime import datetime
import io
import csv
import logging

from backend_fastapi.db.session import get_db
from backend_fastapi.core.deps import get_current_user
from backend_fastapi.models.sys_models import SysUser
from backend_fastapi.models.pm_models import PMDefect, PMProject, PMModule, PMRequirement
from backend_fastapi.models.test_mgt_models import TestCase
from backend_fastapi.routes.QualityMgt.schemas import DefectCreate, DefectUpdate, DefectResponse
from backend_fastapi.services.automation_service import AutomationService
from backend_fastapi.core.constants import DEFECT_STATUS_PROGRESS_MAP

logger = logging.getLogger(__name__)

router = APIRouter(tags=["缺陷管理"])

@router.get("/list", response_model=None)
async def get_defect_list(
    project_id: Optional[int] = None,
    defect_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    reporter_id: Optional[int] = None,
    case_id: Optional[int] = None,
    plan_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search_term: Optional[str] = None,
    export: Optional[bool] = False,
    severity: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    获取缺陷列表
    """
    stmt = select(PMDefect, TestCase.case_name, PMRequirement.title.label("req_title")).outerjoin(TestCase, PMDefect.case_id == TestCase.case_id).outerjoin(PMRequirement, PMDefect.linked_req_id == PMRequirement.req_id).where(PMDefect.del_flag == 0)
    
    if project_id:
        stmt = stmt.where(PMDefect.project_id == project_id)
    if defect_type:
        stmt = stmt.where(PMDefect.defect_type == defect_type)
    if status:
        stmt = stmt.where(PMDefect.status == status)
    if priority:
        stmt = stmt.where(PMDefect.priority == priority)
    if assignee_id:
        stmt = stmt.where(PMDefect.assignee_id == assignee_id)
    if reporter_id:
        stmt = stmt.where(PMDefect.reporter_id == reporter_id)
    
    # Enhanced case_id logic: Find defects linked to this case OR linked to the requirement of this case
    if case_id:
        stmt = stmt.where(PMDefect.case_id == case_id)
        
    if plan_id:
        stmt = stmt.where(TestCase.plan_id == plan_id)

    if severity:
        stmt = stmt.where(PMDefect.severity == severity)
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            stmt = stmt.where(PMDefect.create_time >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            stmt = stmt.where(PMDefect.create_time <= end_dt)
        except ValueError:
            pass

    if search_term:
        stmt = stmt.where(or_(
            PMDefect.title.like(f"%{search_term}%"),
            PMDefect.defect_code.like(f"%{search_term}%")
        ))
    
    # Export logic
    if export:
        stmt = stmt.order_by(desc(PMDefect.create_time))
        result = await db.execute(stmt)
        defects = result.scalars().all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', '标题', '类型', '状态', '优先级', '严重程度', '创建人', '创建时间'])
        for d in defects:
            writer.writerow([
                d.defect_code, 
                d.title, 
                d.defect_type, 
                d.status, 
                d.priority, 
                d.severity,
                d.create_by, 
                d.create_time.strftime('%Y-%m-%d %H:%M:%S') if d.create_time else ''
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]), 
            media_type="text/csv", 
            headers={"Content-Disposition": "attachment; filename=defects.csv"}
        )

    # 计算总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()
    
    # 排序和分页
    stmt = stmt.order_by(desc(PMDefect.create_time))
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(stmt)
    defects_with_data = result.all()
    
    items = []
    for defect, case_name, req_title in defects_with_data:
        d_dict = defect.to_dict()
        d_dict['case_name'] = case_name
        d_dict['req_title'] = req_title
        items.append(d_dict)

    return {
        'code': 200, 
        'msg': 'success', 
        'data': {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    }

@router.post("/create", response_model=dict)
async def create_defect(
    defect_in: DefectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    创建缺陷
    """
    # 处理模块即时创建
    final_module_id = None
    if defect_in.module_id is not None:
        if isinstance(defect_in.module_id, int):
            final_module_id = defect_in.module_id
        elif isinstance(defect_in.module_id, str):
            if defect_in.module_id.isdigit():
                final_module_id = int(defect_in.module_id)
            else:
                # 尝试查找是否存在同名模块
                stmt = select(PMModule).where(
                    PMModule.module_name == defect_in.module_id,
                    PMModule.project_id == defect_in.project_id
                )
                result = await db.execute(stmt)
                existing_module = result.scalar_one_or_none()
                
                if existing_module:
                    final_module_id = existing_module.module_id
                else:
                    # 创建新模块
                    new_module = PMModule(
                        module_name=defect_in.module_id,
                        project_id=defect_in.project_id,
                        description=f"Auto created for defect",
                        create_by=current_user.username
                    )
                    db.add(new_module)
                    await db.flush() # 获取 ID 但不提交事务
                    final_module_id = new_module.module_id

    new_defect = PMDefect(
        title=defect_in.title,
        description=defect_in.description,
        project_id=defect_in.project_id,
        module_id=final_module_id,
        defect_type=defect_in.defect_type,
        severity=defect_in.severity,
        priority=defect_in.priority,
        status=defect_in.status,
        reporter_id=defect_in.reporter_id or current_user.user_id, # Default to current user if not provided
        assignee_id=defect_in.assignee_id,
        linked_req_id=defect_in.linked_req_id,
        linked_task_id=defect_in.linked_task_id,
        case_id=defect_in.case_id,
        environment=defect_in.environment,
        version=defect_in.version,
        due_date=defect_in.due_date,
        progress=defect_in.progress if defect_in.progress is not None else DEFECT_STATUS_PROGRESS_MAP.get(defect_in.status, 0),
        completed_at=defect_in.completed_at,
        create_by=current_user.nickname or current_user.username
    )
    db.add(new_defect)
    await db.commit()
    await db.refresh(new_defect)
    
    # 生成 defect_code (e.g. BUG-10001)
    new_defect.defect_code = f"BUG-{10000 + new_defect.defect_id}"
    db.add(new_defect)
    await db.commit()
    await db.refresh(new_defect)
    
    # 触发自动化助手 - 缺陷分配事件/创建事件
    try:
        if new_defect.assignee_id:
            await AutomationService.trigger_event(
                'defect:assign',
                {'defect_id': new_defect.defect_id, 'assignee_id': new_defect.assignee_id, 'trigger': 'defect_create'},
                db,
                current_user.nickname or current_user.username
            )
        else:
             await AutomationService.trigger_event(
                'defect:create',
                {'defect_id': new_defect.defect_id, 'trigger': 'defect_create'},
                db,
                current_user.nickname or current_user.username
            )
    except Exception as e:
        logger.error(f"Failed to trigger automation event for defect {new_defect.defect_id}: {e}")
    
    return {'code': 200, 'msg': 'success', 'data': new_defect.to_dict()}

@router.put("/update", response_model=dict)
async def update_defect(
    defect_in: DefectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    更新缺陷
    """
    stmt = select(PMDefect).where(PMDefect.defect_id == defect_in.defect_id, PMDefect.del_flag == 0)
    result = await db.execute(stmt)
    defect = result.scalar_one_or_none()
    
    if not defect:
        return {'code': 404, 'msg': '缺陷不存在', 'data': None}
        
    update_data = defect_in.dict(exclude_unset=True)
    if 'defect_id' in update_data:
        del update_data['defect_id']
        
    # 处理模块即时创建/查找逻辑
    if 'module_id' in update_data:
        module_val = update_data['module_id']
        if module_val is not None:
            if isinstance(module_val, int):
                pass # 已经是 ID，无需处理
            elif isinstance(module_val, str):
                if module_val.isdigit():
                    update_data['module_id'] = int(module_val)
                else:
                    # 尝试查找是否存在同名模块
                    # 注意：更新时可能没有传 project_id，如果没传，使用 defect 原有的 project_id
                    current_project_id = update_data.get('project_id', defect.project_id)
                    
                    stmt_mod = select(PMModule).where(
                        PMModule.module_name == module_val,
                        PMModule.project_id == current_project_id
                    )
                    result_mod = await db.execute(stmt_mod)
                    existing_module = result_mod.scalar_one_or_none()
                    
                    if existing_module:
                        update_data['module_id'] = existing_module.module_id
                    else:
                        # 创建新模块
                        new_module = PMModule(
                            module_name=module_val,
                            project_id=current_project_id,
                            description=f"Auto created for defect update",
                            create_by=current_user.username
                        )
                        db.add(new_module)
                        await db.flush()
                        update_data['module_id'] = new_module.module_id
    
    # Capture old values before update
    old_assignee_id = defect.assignee_id
    old_status = defect.status

    update_data['update_by'] = current_user.nickname or current_user.username
    
    # Auto update progress based on status change if progress is not explicitly provided
    if 'status' in update_data and 'progress' not in update_data:
        new_status = update_data['status']
        if new_status in DEFECT_STATUS_PROGRESS_MAP:
            update_data['progress'] = DEFECT_STATUS_PROGRESS_MAP[new_status]
            
            # If status is Closed or Rejected, set completed_at if not set
            if new_status in ['Closed', 'Rejected'] and not defect.completed_at:
                update_data['completed_at'] = datetime.now()

    for key, value in update_data.items():
        setattr(defect, key, value)

    await db.commit()
    await db.refresh(defect)
    
    # 触发自动化助手 - 缺陷更新事件
    triggered_assign = False
    # Only trigger assign event if assignee actually changed
    if 'assignee_id' in update_data and update_data['assignee_id'] != old_assignee_id:
        await AutomationService.trigger_event(
            'defect:assign',
            {'defect_id': defect.defect_id, 'assignee_id': defect.assignee_id, 'trigger': 'defect_update'},
            db,
            current_user.nickname or current_user.username
        )
        triggered_assign = True
    
    # Trigger update event if status changed, or if no assign event was triggered (generic update)
    # This ensures status changes (like Closed) are always notified even if assignee_id is present in payload
    if ('status' in update_data and update_data['status'] != old_status) or (not triggered_assign):
        await AutomationService.trigger_event(
            'defect:update', 
            {'defect_id': defect.defect_id, 'trigger': 'defect_update'},
            db, 
            current_user.nickname or current_user.username
        )
    
    return {'code': 200, 'msg': 'success', 'data': defect.to_dict()}

@router.delete("/{defect_id}", response_model=dict)
async def delete_defect(
    defect_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    删除缺陷
    """
    stmt = update(PMDefect).where(PMDefect.defect_id == defect_id).values(
        del_flag=1,
        update_by=current_user.nickname or current_user.username
    )
    await db.execute(stmt)
    await db.commit()
    
    return {'code': 200, 'msg': 'success', 'data': None}

@router.get("/statistics", response_model=dict)
async def get_defect_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    获取缺陷统计信息 (用于左侧菜单)
    """
    # 1. 按类型统计
    stmt_type = select(PMDefect.defect_type, func.count(PMDefect.defect_id)).where(PMDefect.del_flag == 0).group_by(PMDefect.defect_type)
    result_type = await db.execute(stmt_type)
    type_stats = result_type.all()
    type_data = {t[0]: t[1] for t in type_stats}
    
    # 2. 按项目统计
    stmt_project = select(
        PMProject.project_id,
        PMProject.project_name,
        func.count(PMDefect.defect_id)
    ).join(
        PMDefect, 
        PMProject.project_id == PMDefect.project_id
    ).where(
        PMDefect.del_flag == 0
    ).group_by(
        PMProject.project_id, 
        PMProject.project_name
    )
    
    result_project = await db.execute(stmt_project)
    project_stats = result_project.all()
    
    projects_data = [
        {
            "project_id": p[0],
            "project_name": p[1],
            "count": p[2]
        } 
        for p in project_stats
    ]
    
    total_count = sum(type_data.values())
    
    # 构造返回数据
    # 类型映射到菜单 key
    # 'Functional', 'UI', 'Performance', 'Security', 'Compatibility'
    
    data = {
        "all": total_count,
        "unclassified": 0, # Simplify for now
        "functional": type_data.get('Functional', 0),
        "ui": type_data.get('UI', 0),
        "performance": type_data.get('Performance', 0),
        "security": type_data.get('Security', 0),
        "compatibility": type_data.get('Compatibility', 0),
        "projects": projects_data
    }
    
    return {'code': 200, 'msg': 'success', 'data': data}

@router.get("/{defect_id}", response_model=dict)
async def get_defect_detail(
    defect_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取缺陷详情
    """
    stmt = select(PMDefect, TestCase.case_name, PMRequirement.title.label("req_title")).outerjoin(TestCase, PMDefect.case_id == TestCase.case_id).outerjoin(PMRequirement, PMDefect.linked_req_id == PMRequirement.req_id).where(
        PMDefect.defect_id == defect_id,
        PMDefect.del_flag == 0
    )
    result = await db.execute(stmt)
    row = result.first()
    
    if not row:
        return {'code': 404, 'msg': '缺陷不存在', 'data': None}
    
    defect, case_name, req_title = row
    data = defect.to_dict()
    data['case_name'] = case_name
    data['req_title'] = req_title
        
    return {'code': 200, 'msg': 'success', 'data': data}
