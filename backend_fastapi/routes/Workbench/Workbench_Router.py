from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_, and_
from sqlalchemy.orm import aliased
from backend_fastapi.db.session import get_automation_db, get_db
from backend_fastapi.models.automation_models import AutomationProject, AutomationExecution, Project
from backend_fastapi.models.pm_models import PMRequirement, PMSubRequirement, PMTask, PMProject, PMDefect
from backend_fastapi.models.sys_models import SysUser, SysUserFollow, SysNotification
from backend_fastapi.core.deps import get_current_user
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
import json

router = APIRouter(tags=["工作台"])

def parse_list_string(value):
    if not value:
        return value
    try:
        # Check if it looks like a list
        if isinstance(value, str) and value.strip().startswith('[') and value.strip().endswith(']'):
            parsed = json.loads(value)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed[0]
    except:
        pass
    return value

@router.get("/")
@router.get("", include_in_schema=False)
async def get_workbench_data(
    current_user: SysUser = Depends(get_current_user),
    automation_db: AsyncSession = Depends(get_automation_db),
    main_db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Statistics
        # Total Automation Projects (del_flag=0)
        stmt_total_projects = select(func.count()).where(AutomationProject.del_flag == 0)
        total_projects = (await automation_db.execute(stmt_total_projects)).scalar() or 0
        
        # Total Executions
        stmt_total_executions = select(func.count()).select_from(AutomationExecution)
        total_executions = (await automation_db.execute(stmt_total_executions)).scalar() or 0
        
        # 获取第一页数据
        todos_data = await get_todos_data(current_user, main_db, page=1, page_size=5)
        activities_data = await get_activities_data(current_user, automation_db, main_db, page=1, page_size=5)
        followed_data = await get_followed_data(current_user, main_db, automation_db, page=1, page_size=5)
        
        data = {
            'greeting': f'Hi, {current_user.nickname or current_user.username}, 欢迎回来!',
            'stats': {
                'total_projects': total_projects,
                'total_executions': total_executions
            },
            'todos': todos_data['items'],
            'todos_total': todos_data['total'],
            'activities': activities_data['items'],
            'activities_total': activities_data['total'],
            'followed': followed_data['items'],
            'followed_total': followed_data['total']
        }
        
        return {'code': 200, 'msg': 'success', 'data': data}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'code': 500, 'msg': str(e), 'data': None}

@router.get("/todos")
async def get_todos(
    page: int = 1,
    page_size: int = 10,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        data = await get_todos_data(current_user, db, page, page_size)
        return {'code': 200, 'msg': 'success', 'data': data}
    except Exception as e:
        return {'code': 500, 'msg': str(e), 'data': None}

@router.get("/activities")
async def get_activities(
    page: int = 1,
    page_size: int = 10,
    current_user: SysUser = Depends(get_current_user),
    automation_db: AsyncSession = Depends(get_automation_db),
    main_db: AsyncSession = Depends(get_db)
):
    try:
        data = await get_activities_data(current_user, automation_db, main_db, page, page_size)
        return {'code': 200, 'msg': 'success', 'data': data}
    except Exception as e:
        return {'code': 500, 'msg': str(e), 'data': None}

@router.get("/followed")
async def get_followed(
    page: int = 1,
    page_size: int = 10,
    current_user: SysUser = Depends(get_current_user),
    automation_db: AsyncSession = Depends(get_automation_db),
    main_db: AsyncSession = Depends(get_db)
):
    try:
        data = await get_followed_data(current_user, main_db, automation_db, page, page_size)
        return {'code': 200, 'msg': 'success', 'data': data}
    except Exception as e:
        return {'code': 500, 'msg': str(e), 'data': None}

from pydantic import BaseModel

class FollowRequest(BaseModel):
    target_id: int
    target_type: str # requirement, sub_requirement, task, automation_project

@router.post("/follow")
async def follow_item(
    req: FollowRequest,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if already followed
    stmt = select(SysUserFollow).where(
        SysUserFollow.user_id == current_user.user_id,
        SysUserFollow.target_id == req.target_id,
        SysUserFollow.target_type == req.target_type
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    
    if existing:
        return {'code': 200, 'msg': '已关注', 'data': None}
        
    new_follow = SysUserFollow(
        user_id=current_user.user_id,
        target_id=req.target_id,
        target_type=req.target_type,
        create_time=datetime.now()
    )
    db.add(new_follow)
    await db.commit()
    
    return {'code': 200, 'msg': '关注成功', 'data': None}

@router.post("/unfollow")
async def unfollow_item(
    req: FollowRequest,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(SysUserFollow).where(
        SysUserFollow.user_id == current_user.user_id,
        SysUserFollow.target_id == req.target_id,
        SysUserFollow.target_type == req.target_type
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    
    if not existing:
        return {'code': 404, 'msg': '未关注', 'data': None}
        
    await db.delete(existing)
    await db.commit()
    
    return {'code': 200, 'msg': '取消关注成功', 'data': None}

async def get_todos_data(current_user, db, page=1, page_size=10):
    user_id = current_user.user_id
    items = []

    # Aliases for User joins
    Assignee = aliased(SysUser)
    Developer = aliased(SysUser)
    Tester = aliased(SysUser)

    # 1. Requirements assigned to user
    stmt_req = select(
        PMRequirement, 
        PMProject.project_name,
        Assignee.nickname.label('assignee_name'),
        Developer.nickname.label('developer_name'),
        Tester.nickname.label('tester_name')
    ).outerjoin(
        PMProject, PMRequirement.project_id == PMProject.project_id
    ).outerjoin(
        Assignee, PMRequirement.assignee_id == Assignee.user_id
    ).outerjoin(
        Developer, PMRequirement.developer_id == Developer.user_id
    ).outerjoin(
        Tester, PMRequirement.tester_id == Tester.user_id
    ).where(
        PMRequirement.assignee_id == user_id,
        PMRequirement.status.notin_(['completed', 'closed', 'cancelled']),
        PMRequirement.del_flag == 0
    ).order_by(desc(PMRequirement.update_time))
    
    reqs = (await db.execute(stmt_req)).all()
    for r, project_name, assignee_name, developer_name, tester_name in reqs:
        items.append({
            'id': r.req_id,
            'title': r.title,
            'code': r.req_code,
            'type': 'requirement',
            'type_label': '需求',
            'status': r.status,
            'priority': r.priority,
            'project_name': project_name,
            'owner': assignee_name or r.assignee_id,
            'created_by': r.create_by,
            'developer': developer_name,
            'tester': tester_name,
            'risk_level': r.risk_level,
            'progress': r.progress,
            'start_time': r.start_date.strftime('%Y-%m-%d') if r.start_date else None,
            'end_date': r.end_date.strftime('%Y-%m-%d') if r.end_date else None,
            'deadline': r.end_date.strftime('%Y-%m-%d') if r.end_date else None,
            'created_at': r.create_time.strftime('%Y-%m-%d %H:%M:%S') if r.create_time else None,
            'update_time': r.update_time
        })

    # 2. Sub-requirements assigned to user
    stmt_sub = select(
        PMSubRequirement, 
        PMProject.project_name,
        Assignee.nickname.label('assignee_name'),
        Developer.nickname.label('developer_name'),
        Tester.nickname.label('tester_name')
    ).outerjoin(
        PMRequirement, PMSubRequirement.requirement_id == PMRequirement.req_id
    ).outerjoin(
        PMProject, PMRequirement.project_id == PMProject.project_id
    ).outerjoin(
        Assignee, PMSubRequirement.assignee_id == Assignee.user_id
    ).outerjoin(
        Developer, PMSubRequirement.developer_id == Developer.user_id
    ).outerjoin(
        Tester, PMSubRequirement.tester_id == Tester.user_id
    ).where(
        PMSubRequirement.assignee_id == user_id,
        PMSubRequirement.status.notin_(['online', 'closed']),
        PMSubRequirement.del_flag == 0
    ).order_by(desc(PMSubRequirement.update_time))
    
    subs = (await db.execute(stmt_sub)).all()
    for s, project_name, assignee_name, developer_name, tester_name in subs:
        items.append({
            'id': s.sub_req_id,
            'title': s.title,
            'code': s.sub_req_code,
            'type': 'sub_requirement',
            'type_label': '子需求',
            'status': s.status,
            'priority': s.priority,
            'project_name': project_name,
            'owner': assignee_name or s.assignee_id,
            'created_by': s.create_by,
            'developer': developer_name,
            'tester': tester_name,
            'risk_level': s.risk_level,
            'start_time': s.start_date.strftime('%Y-%m-%d') if s.start_date else None,
            'end_date': s.end_date.strftime('%Y-%m-%d') if s.end_date else None,
            'deadline': s.end_date.strftime('%Y-%m-%d') if s.end_date else None,
            'created_at': s.create_time.strftime('%Y-%m-%d %H:%M:%S') if s.create_time else None,
            'update_time': s.update_time
        })

    # 3. Tasks assigned to user
    Req = aliased(PMRequirement)
    SubReq = aliased(PMSubRequirement)
    ParentReq = aliased(PMRequirement)
    Proj = aliased(PMProject)

    stmt_task = select(
        PMTask, 
        Proj.project_name,
        Assignee.nickname.label('assignee_name'),
        Developer.nickname.label('developer_name'),
        Tester.nickname.label('tester_name')
    ).outerjoin(
        Req, PMTask.requirement_id == Req.req_id
    ).outerjoin(
        SubReq, PMTask.sub_requirement_id == SubReq.sub_req_id
    ).outerjoin(
        ParentReq, SubReq.requirement_id == ParentReq.req_id
    ).outerjoin(
        Proj, func.coalesce(Req.project_id, ParentReq.project_id) == Proj.project_id
    ).outerjoin(
        Assignee, PMTask.assignee_id == Assignee.user_id
    ).outerjoin(
        Developer, PMTask.developer_id == Developer.user_id
    ).outerjoin(
        Tester, PMTask.tester_id == Tester.user_id
    ).where(
        PMTask.assignee_id == user_id,
        PMTask.status.notin_(['completed', 'closed']),
        PMTask.del_flag == 0
    ).order_by(desc(PMTask.update_time))
    
    tasks = (await db.execute(stmt_task)).all()
    for t, project_name, assignee_name, developer_name, tester_name in tasks:
        items.append({
            'id': t.task_id,
            'title': t.title,
            'code': t.task_code,
            'type': 'task',
            'type_label': '任务',
            'status': t.status,
            'priority': t.priority,
            'project_name': project_name,
            'requirement_id': t.requirement_id,
            'sub_requirement_id': t.sub_requirement_id,
            'owner': assignee_name or t.assignee_id,
            'created_by': t.create_by,
            'developer': developer_name,
            'tester': tester_name,
            'estimate_time': t.estimate_time,
            'start_time': t.start_date.strftime('%Y-%m-%d') if t.start_date else None,
            'end_date': t.end_date.strftime('%Y-%m-%d') if t.end_date else None,
            'deadline': t.end_date.strftime('%Y-%m-%d') if t.end_date else None,
            'created_at': t.create_time.strftime('%Y-%m-%d %H:%M:%S') if t.create_time else None,
            'update_time': t.update_time
        })

    # 4. Defects assigned to user
    stmt_defect = select(
        PMDefect,
        PMProject.project_name,
        Assignee.nickname.label('assignee_name'),
        Developer.nickname.label('developer_name'),
        Tester.nickname.label('tester_name')
    ).outerjoin(
        PMProject, PMDefect.project_id == PMProject.project_id
    ).outerjoin(
        Assignee, PMDefect.assignee_id == Assignee.user_id
    ).outerjoin(
        Developer, PMDefect.assignee_id == Developer.user_id
    ).outerjoin(
        Tester, PMDefect.reporter_id == Tester.user_id
    ).where(
        or_(
            PMDefect.assignee_id == user_id,
            PMDefect.reporter_id == user_id
        ),
        PMDefect.status.notin_(['Closed', 'Rejected']),
        PMDefect.del_flag == 0
    ).order_by(desc(PMDefect.update_time))

    defects = (await db.execute(stmt_defect)).all()
    for d, project_name, assignee_name, developer_name, tester_name in defects:
        items.append({
            'id': d.defect_id,
            'title': d.title,
            'code': d.defect_code,
            'type': 'defect',
            'type_label': '缺陷',
            'status': d.status,
            'priority': d.priority,
            'project_name': project_name,
            'owner': assignee_name or d.assignee_id,
            'created_by': d.create_by,
            'start_time': d.create_time.strftime('%Y-%m-%d') if d.create_time else None,
            'end_date': d.due_date.strftime('%Y-%m-%d') if d.due_date else None,
            'deadline': d.due_date.strftime('%Y-%m-%d') if d.due_date else None,
            'created_at': d.create_time.strftime('%Y-%m-%d %H:%M:%S') if d.create_time else None,
            'update_time': d.update_time,
            'developer': developer_name,
            'tester': tester_name
        })

    # Sort all by update_time desc
    items.sort(key=lambda x: x['update_time'] or datetime.min, reverse=True)
    
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paged_items = items[start:end]
    
    # Clean up datetime objects for JSON response
    for i in paged_items:
        if isinstance(i.get('update_time'), datetime):
            i['update_time'] = i['update_time'].strftime('%Y-%m-%d %H:%M:%S')

    return {'items': paged_items, 'total': total, 'page': page, 'page_size': page_size}

async def get_activities_data(current_user, automation_db, main_db, page=1, page_size=10):
    # My Activity: User operations (Create, Update, Execute)
    # Since we don't have a centralized operation log, we query create_by/update_by from entities
    # This is expensive but MVP acceptable.
    
    # 1. Automation Executions
    stmt_exec = select(
        AutomationExecution,
        AutomationProject.product_package_names
    ).outerjoin(
        AutomationProject, AutomationExecution.project_id == AutomationProject.id
    ).where(
        AutomationExecution.executed_by == current_user.username
    ).order_by(desc(AutomationExecution.start_time))
    
    # 2. Requirements Created/Updated
    stmt_req = select(PMRequirement, PMProject.project_name).outerjoin(
        PMProject, PMRequirement.project_id == PMProject.project_id
    ).where(
        or_(
            PMRequirement.create_by == current_user.username,
            PMRequirement.update_by == current_user.username
        )
    ).order_by(desc(PMRequirement.update_time))
    
    # 3. Tasks Created/Updated
    Req = aliased(PMRequirement)
    SubReq = aliased(PMSubRequirement)
    ParentReq = aliased(PMRequirement)
    Proj = aliased(PMProject)

    stmt_task = select(
        PMTask, 
        Proj.project_name
    ).outerjoin(
        Req, PMTask.requirement_id == Req.req_id
    ).outerjoin(
        SubReq, PMTask.sub_requirement_id == SubReq.sub_req_id
    ).outerjoin(
        ParentReq, SubReq.requirement_id == ParentReq.req_id
    ).outerjoin(
        Proj, func.coalesce(Req.project_id, ParentReq.project_id) == Proj.project_id
    ).where(
        or_(
            PMTask.create_by == current_user.username,
            PMTask.update_by == current_user.username
        )
    ).order_by(desc(PMTask.update_time))

    # 4. Sub-Requirements Created/Updated
    stmt_sub = select(PMSubRequirement, PMProject.project_name).outerjoin(
        PMRequirement, PMSubRequirement.requirement_id == PMRequirement.req_id
    ).outerjoin(
        PMProject, PMRequirement.project_id == PMProject.project_id
    ).where(
        or_(
            PMSubRequirement.create_by == current_user.username,
            PMSubRequirement.update_by == current_user.username
        )
    ).order_by(desc(PMSubRequirement.update_time))
    
    # 5. Automation Projects Created/Updated
    stmt_auto_proj = select(AutomationProject).where(
        AutomationProject.created_by == current_user.username
    ).order_by(desc(AutomationProject.updated_at))

    # 6. Defects Created/Updated
    stmt_defect = select(PMDefect, PMProject.project_name).outerjoin(
        PMProject, PMDefect.project_id == PMProject.project_id
    ).where(
        or_(
            PMDefect.create_by == current_user.username,
            PMDefect.update_by == current_user.username
        )
    ).order_by(desc(PMDefect.update_time))

    # Execute queries
    execs = (await automation_db.execute(stmt_exec.limit(50))).all()
    req_rows = (await main_db.execute(stmt_req.limit(50))).all()
    task_rows = (await main_db.execute(stmt_task.limit(50))).all()
    sub_rows = (await main_db.execute(stmt_sub.limit(50))).all()
    auto_projs = (await automation_db.execute(stmt_auto_proj.limit(50))).scalars().all()
    defect_rows = (await main_db.execute(stmt_defect.limit(50))).all()
    
    activities = []
    for e, package_names in execs:
        target_name = parse_list_string(e.process_name)
        project_name = parse_list_string(package_names) or '自动化项目'

        activities.append({
            'id': e.id,
            'time': e.start_time,
            'target_type': 'automation_project',
            'target_name': target_name,
            'project_name': project_name,
            'action': '执行了',
            'result': e.status,
            'content': f"执行了自动化测试: {target_name}",
            'status': e.status
        })
        
    for r, pname in req_rows:
        if r.create_by == current_user.username:
            activities.append({
                'id': r.req_id,
                'time': r.create_time,
                'target_type': 'requirement',
                'target_name': r.title,
                'project_name': pname,
                'action': '新建了',
                'result': r.status,
                'content': f"新建了需求: {r.title}",
                'status': r.status
            })
        if r.update_by == current_user.username and r.update_time and r.create_time and r.update_time > r.create_time + timedelta(seconds=1):
            activities.append({
                'id': r.req_id,
                'time': r.update_time,
                'target_type': 'requirement',
                'target_name': r.title,
                'project_name': pname,
                'action': '更新了',
                'result': r.status,
                'content': f"更新了需求: {r.title}",
                'status': r.status
            })

    for s, pname in sub_rows:
        if s.create_by == current_user.username:
            activities.append({
                'id': s.sub_req_id,
                'time': s.create_time,
                'target_type': 'sub_requirement',
                'target_name': s.title,
                'project_name': pname,
                'action': '新建了',
                'result': s.status,
                'content': f"新建了子需求: {s.title}",
                'status': s.status
            })
        if s.update_by == current_user.username and s.update_time and s.create_time and s.update_time > s.create_time + timedelta(seconds=1):
            activities.append({
                'id': s.sub_req_id,
                'time': s.update_time,
                'target_type': 'sub_requirement',
                'target_name': s.title,
                'project_name': pname,
                'action': '更新了',
                'result': s.status,
                'content': f"更新了子需求: {s.title}",
                'status': s.status
            })
        
    for t, pname in task_rows:
        if t.create_by == current_user.username:
            activities.append({
                'id': t.task_id,
                'requirement_id': t.requirement_id,
                'sub_requirement_id': t.sub_requirement_id,
                'time': t.create_time,
                'target_type': 'task',
                'target_name': t.title,
                'project_name': pname,
                'action': '新建了',
                'result': t.status,
                'content': f"新建了任务: {t.title}",
                'status': t.status
            })
        if t.update_by == current_user.username and t.update_time and t.create_time and t.update_time > t.create_time + timedelta(seconds=1):
            activities.append({
                'id': t.task_id,
                'requirement_id': t.requirement_id,
                'sub_requirement_id': t.sub_requirement_id,
                'time': t.update_time,
                'target_type': 'task',
                'target_name': t.title,
                'project_name': pname,
                'action': '更新了',
                'result': t.status,
                'content': f"更新了任务: {t.title}",
                'status': t.status
            })

    for p in auto_projs:
        status_val = p.des_status or p.status
        target_name = parse_list_string(p.process_name)
        project_name = parse_list_string(p.product_package_names)

        if p.created_at:
            activities.append({
                'id': p.id,
                'time': p.created_at,
                'target_type': 'automation_project',
                'target_name': target_name,
                'project_name': project_name,
                'action': '新建了',
                'result': status_val,
                'content': f"新建了自动化项目: {target_name}",
                'status': status_val
            })
        if p.updated_at and p.created_at and p.updated_at > p.created_at + timedelta(seconds=1):
             activities.append({
                'id': p.id,
                'time': p.updated_at,
                'target_type': 'automation_project',
                'target_name': target_name,
                'project_name': project_name,
                'action': '更新了',
                'result': status_val,
                'content': f"更新了自动化项目: {target_name}",
                'status': status_val
             })

    for d, pname in defect_rows:
        if d.create_by == current_user.username:
            activities.append({
                'id': d.defect_id,
                'time': d.create_time,
                'target_type': 'defect',
                'target_name': d.title,
                'project_name': pname,
                'action': '新建了',
                'result': d.status,
                'content': f"新建了缺陷: {d.title}",
                'status': d.status
            })
        if d.update_by == current_user.username and d.update_time and d.create_time and d.update_time > d.create_time + timedelta(seconds=1):
            activities.append({
                'id': d.defect_id,
                'time': d.update_time,
                'target_type': 'defect',
                'target_name': d.title,
                'project_name': pname,
                'action': '更新了',
                'result': d.status,
                'content': f"更新了缺陷: {d.title}",
                'status': d.status
            })
        
    # Sort
    activities.sort(key=lambda x: x['time'] or datetime.min, reverse=True)
    
    total = len(activities)
    start = (page - 1) * page_size
    end = start + page_size
    paged_items = activities[start:end]
    
    for i in paged_items:
        if isinstance(i.get('time'), datetime):
            i['time'] = i['time'].strftime('%Y-%m-%d %H:%M:%S')
            
    return {'items': paged_items, 'total': total}

async def get_followed_data(current_user, main_db, automation_db, page=1, page_size=10):
    user_id = current_user.user_id
    
    # Query SysUserFollow
    stmt = select(SysUserFollow).where(
        SysUserFollow.user_id == user_id
    ).order_by(desc(SysUserFollow.create_time))
    
    stmt_count = select(func.count()).where(SysUserFollow.user_id == user_id)
    total = (await main_db.execute(stmt_count)).scalar() or 0
    
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    follows = (await main_db.execute(stmt)).scalars().all()
    
    items = []
    for f in follows:
        item = {
            'follow_id': f.follow_id,
            'target_id': f.target_id,
            'target_type': f.target_type,
            'follow_time': f.create_time.strftime('%Y-%m-%d %H:%M:%S') if f.create_time else None
        }
        
        # Fetch details based on type
        if f.target_type == 'requirement':
            res = (await main_db.execute(select(PMRequirement).where(PMRequirement.req_id == f.target_id))).scalar_one_or_none()
            if res:
                item['title'] = res.title
                item['status'] = res.status
                item['priority'] = res.priority
                item['code'] = res.req_code
                item['type_label'] = '需求'
        elif f.target_type == 'sub_requirement':
            res = (await main_db.execute(select(PMSubRequirement).where(PMSubRequirement.sub_req_id == f.target_id))).scalar_one_or_none()
            if res:
                item['title'] = res.title
                item['status'] = res.status
                item['priority'] = res.priority
                item['code'] = res.sub_req_code
                item['type_label'] = '子需求'
        elif f.target_type == 'task':
            res = (await main_db.execute(select(PMTask).where(PMTask.task_id == f.target_id))).scalar_one_or_none()
            if res:
                item['title'] = res.title
                item['status'] = res.status
                item['priority'] = res.priority
                item['code'] = res.task_code
                item['type_label'] = '任务'
                item['requirement_id'] = res.requirement_id
                item['sub_requirement_id'] = res.sub_requirement_id
        elif f.target_type == 'defect':
            res = (await main_db.execute(select(PMDefect).where(PMDefect.defect_id == f.target_id))).scalar_one_or_none()
            if res:
                item['title'] = res.title
                item['status'] = res.status
                item['priority'] = res.priority
                item['code'] = res.defect_code
                item['type_label'] = '缺陷'
        elif f.target_type == 'automation_project':
             res = (await automation_db.execute(select(AutomationProject).where(AutomationProject.id == f.target_id))).scalar_one_or_none()
             if res:
                 item['title'] = parse_list_string(res.process_name)
                 item['status'] = res.status
                 item['priority'] = 'Normal' # AutomationProject doesn't have priority field usually
                 item['code'] = str(res.id)
                 item['type_label'] = '自动化项目'
        
        if 'title' in item: # Only add if target still exists
            items.append(item)
            
    return {'items': items, 'total': total}
