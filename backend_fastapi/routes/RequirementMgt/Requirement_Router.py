from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func, or_
from typing import List, Optional
from datetime import datetime
import io
import csv

from backend_fastapi.db.session import get_db
from backend_fastapi.core.deps import get_current_user
from backend_fastapi.models.sys_models import SysUser, SysUserFollow
from backend_fastapi.models.pm_models import PMRequirement, PMModule, PMProject, PMTask, PMSubRequirement
from backend_fastapi.routes.RequirementMgt.schemas import (
    RequirementCreate, RequirementUpdate, RequirementResponse,
    ModuleCreate, ModuleResponse,
    TaskCreate, TaskUpdate, TaskResponse,
    SubRequirementCreate, SubRequirementUpdate, SubRequirementResponse
)
from backend_fastapi.services.automation_service import AutomationService
from backend_fastapi.utils.user_utils import enrich_usernames_with_nicknames

from backend_fastapi.models.sys_dict_models import SysDictType, SysDictData
from backend_fastapi.core.constants import REQUIREMENT_STATUS_PROGRESS_MAP

import json
from redis import asyncio as aioredis
from backend_fastapi.core.config import settings

# Redis connection
redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

router = APIRouter(tags=["需求管理"])

# --- 需求管理接口 ---

@router.post("/follow/{req_id}", response_model=dict)
async def toggle_follow_requirement(
    req_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    切换关注状态 (关注/取消关注)
    """
    # Check if already followed in SysUserFollow
    stmt = select(SysUserFollow).where(
        SysUserFollow.user_id == current_user.user_id,
        SysUserFollow.target_id == req_id,
        SysUserFollow.target_type == 'requirement'
    )
    result = await db.execute(stmt)
    follow = result.scalar_one_or_none()
    
    if follow:
        # Unfollow
        await db.delete(follow)
        await db.commit()
        return {'code': 200, 'msg': '取消关注成功', 'data': {'is_followed': False}}
    else:
        # Follow
        # Verify requirement exists first
        req_stmt = select(PMRequirement).where(PMRequirement.req_id == req_id)
        req_result = await db.execute(req_stmt)
        if not req_result.scalar_one_or_none():
             return {'code': 404, 'msg': '需求不存在', 'data': None}
             
        new_follow = SysUserFollow(
            user_id=current_user.user_id,
            target_id=req_id,
            target_type='requirement'
        )
        db.add(new_follow)
        await db.commit()
        return {'code': 200, 'msg': '关注成功', 'data': {'is_followed': True}}

@router.post("/sub_requirements/follow/{sub_req_id}", response_model=dict)
async def toggle_follow_sub_requirement(
    sub_req_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    切换关注子需求状态 (关注/取消关注)
    """
    # Check if already followed in SysUserFollow
    stmt = select(SysUserFollow).where(
        SysUserFollow.user_id == current_user.user_id,
        SysUserFollow.target_id == sub_req_id,
        SysUserFollow.target_type == 'sub_requirement'
    )
    result = await db.execute(stmt)
    follow = result.scalar_one_or_none()
    
    if follow:
        # Unfollow
        await db.delete(follow)
        await db.commit()
        return {'code': 200, 'msg': '取消关注成功', 'data': {'is_followed': False}}
    else:
        # Follow
        # Verify sub-requirement exists first
        sub_req_stmt = select(PMSubRequirement).where(PMSubRequirement.sub_req_id == sub_req_id)
        sub_req_result = await db.execute(sub_req_stmt)
        if not sub_req_result.scalar_one_or_none():
             return {'code': 404, 'msg': '子需求不存在', 'data': None}
             
        new_follow = SysUserFollow(
            user_id=current_user.user_id,
            target_id=sub_req_id,
            target_type='sub_requirement'
        )
        db.add(new_follow)
        await db.commit()
        return {'code': 200, 'msg': '关注成功', 'data': {'is_followed': True}}

@router.get("/search", response_model=List[dict])
async def search_requirements(
    query: str,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    搜索需求和子需求
    """
    if not query:
        return []

    results = []
    seen_ids = set()

    # 1. Search Requirements
    stmt_req = select(PMRequirement).where(
        or_(
            PMRequirement.title.like(f"%{query}%"),
            PMRequirement.req_code.like(f"%{query}%")
        )
    ).where(PMRequirement.del_flag == 0).limit(20)
    
    res_req = await db.execute(stmt_req)
    reqs = res_req.scalars().all()
    
    for r in reqs:
        if r.req_id not in seen_ids:
            results.append({
                "req_id": r.req_id,
                "req_code": r.req_code,
                "title": r.title
            })
            seen_ids.add(r.req_id)
            
    # 2. Search Sub-Requirements
    stmt_sub = select(PMSubRequirement, PMRequirement).join(
        PMRequirement, PMSubRequirement.requirement_id == PMRequirement.req_id
    ).where(
        or_(
            PMSubRequirement.title.like(f"%{query}%"),
            PMSubRequirement.sub_req_code.like(f"%{query}%")
        )
    ).where(PMSubRequirement.del_flag == 0).limit(20)
    
    res_sub = await db.execute(stmt_sub)
    subs = res_sub.all()
    
    for sub, parent in subs:
        if parent.req_id not in seen_ids:
            results.append({
                "req_id": parent.req_id,
                "req_code": parent.req_code,
                "title": f"{parent.title} (包含子需求: {sub.title})"
            })
            seen_ids.add(parent.req_id)
            
    return results

@router.get("/list", response_model=None)
async def get_requirement_list(
    project_id: Optional[int] = None,
    module_id: Optional[int] = None,
    search_term: Optional[str] = None,
    req_id: Optional[int] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    is_followed: Optional[bool] = False,
    is_recent: Optional[bool] = False, # Reserved
    only_parents: Optional[bool] = False,
    export: Optional[bool] = False,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取需求列表
    """
    stmt = select(PMRequirement).where(PMRequirement.del_flag == 0)
    
    if project_id:
        stmt = stmt.where(PMRequirement.project_id == project_id)
    if module_id:
        stmt = stmt.where(PMRequirement.module_id == module_id)
    if type:
        if type == 'unclassified':
             # Unclassified means type is not one of the standard types or is null/empty
             # Assuming standard types are 'product', 'tech', 'bug'
             stmt = stmt.where(or_(
                 PMRequirement.type.not_in(['product', 'tech', 'bug']),
                 PMRequirement.type == None
             ))
        else:
            stmt = stmt.where(PMRequirement.type == type)
    if status:
        stmt = stmt.where(PMRequirement.status == status)
    if priority:
        stmt = stmt.where(PMRequirement.priority == priority)
    if assignee_id:
        stmt = stmt.where(PMRequirement.assignee_id == assignee_id)
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            # 筛选开始时间晚于等于查询开始时间的需求
            stmt = stmt.where(PMRequirement.start_date >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            # 筛选结束时间早于等于查询结束时间的需求
            stmt = stmt.where(PMRequirement.start_date <= end_dt)
        except ValueError:
            pass
    
    # --- 核心修改：计算每个需求的进度 (进度 = (子需求进度总和 + 子任务进度总和) / (子需求数 + 子任务数)) ---
    # 尝试从 Redis 缓存获取状态映射
    status_map = {}
    redis_key = "sys:dict:requirement_status_progress"
    
    try:
        cached_map = await redis.get(redis_key)
        if cached_map:
            status_map = json.loads(cached_map)
    except Exception as e:
        print(f"Failed to read from Redis: {e}")

    # 如果缓存未命中，尝试从数据库字典获取
    if not status_map:
        try:
            # 获取 dict_id
            type_stmt = select(SysDictType).where(SysDictType.dict_type == 'requirement_status_progress')
            type_res = await db.execute(type_stmt)
            dict_type = type_res.scalar_one_or_none()
            
            if dict_type:
                data_stmt = select(SysDictData).where(SysDictData.dict_id == dict_type.dict_id, SysDictData.status == 1)
                data_res = await db.execute(data_stmt)
                dict_data = data_res.scalars().all()
                
                for d in dict_data:
                    # Value is string in DB, convert to int
                    try:
                        status_map[d.dict_label] = int(d.dict_value)
                    except:
                        pass
                
                # 写入 Redis 缓存 (过期时间 1 小时)
                if status_map:
                    try:
                        await redis.set(redis_key, json.dumps(status_map), ex=3600)
                    except Exception as e:
                        print(f"Failed to write to Redis: {e}")
        except Exception as e:
            print(f"Failed to load status map from DB: {e}")
        
    # 如果数据库也没数据，回退到常量文件
    if not status_map:
        status_map = REQUIREMENT_STATUS_PROGRESS_MAP

    if is_followed:
        stmt = stmt.join(
            SysUserFollow, 
            (SysUserFollow.target_id == PMRequirement.req_id) & (SysUserFollow.target_type == 'requirement')
        ).where(SysUserFollow.user_id == current_user.user_id)
    
    if only_parents:
        stmt = stmt.where(PMRequirement.parent_id == None)
            
    if search_term:
        stmt = stmt.where(or_(
            PMRequirement.title.like(f"%{search_term}%"),
            PMRequirement.req_code.like(f"%{search_term}%")
        ))
    
    if req_id:
        stmt = stmt.where(PMRequirement.req_id == req_id)
     
    # Export logic
    if export:
        stmt = stmt.order_by(desc(PMRequirement.create_time))
        result = await db.execute(stmt)
        requirements = result.scalars().all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', '标题', '类型', '状态', '优先级', '创建人', '创建时间'])
        for r in requirements:
            writer.writerow([
                r.req_code, 
                r.title, 
                r.type, 
                r.status, 
                r.priority, 
                r.create_by, 
                r.create_time.strftime('%Y-%m-%d %H:%M:%S') if r.create_time else ''
            ])
            
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment;filename=requirements.csv"}
        )

    # Pagination
    # Count total first
    # 注意：如果是 is_followed 模式，total 的计算需要包含子需求，这里的 count 只计算了父需求。
    # 但由于分页逻辑比较复杂，混合列表的分页很难做准确。
    # 鉴于“我的关注”通常数量不多，我们可以先获取所有关注项，然后在内存分页。
    # 或者，我们接受 total 只显示父需求数量的瑕疵（或者稍微修正一下）。
    
    # 考虑到用户体验，如果 is_followed=True，我们禁用数据库分页，改用内存分页。
    
    if is_followed:
        # 获取所有符合条件的父需求 (不分页)
        stmt = stmt.distinct().order_by(desc(PMRequirement.create_time))
        result = await db.execute(stmt)
        requirements = result.scalars().all()
        
        # 获取所有符合条件的子需求
        sub_stmt = select(PMSubRequirement, PMRequirement.project_id).join(
            PMRequirement, PMSubRequirement.requirement_id == PMRequirement.req_id
        ).join(
            SysUserFollow,
            (SysUserFollow.target_id == PMSubRequirement.sub_req_id) & (SysUserFollow.target_type == 'sub_requirement')
        ).where(
            SysUserFollow.user_id == current_user.user_id,
            PMSubRequirement.del_flag == 0
        )
        
        if search_term:
             sub_stmt = sub_stmt.where(or_(
                PMSubRequirement.title.like(f"%{search_term}%"),
                PMSubRequirement.sub_req_code.like(f"%{search_term}%")
            ))
            
        # Apply filters to sub_stmt
        if type:
            if type == 'unclassified':
                 sub_stmt = sub_stmt.where(or_(
                     PMSubRequirement.type.not_in(['product', 'tech', 'bug']),
                     PMSubRequirement.type == None
                 ))
            else:
                sub_stmt = sub_stmt.where(PMSubRequirement.type == type)
        
        if status:
            sub_stmt = sub_stmt.where(PMSubRequirement.status == status)
            
        if priority:
            sub_stmt = sub_stmt.where(PMSubRequirement.priority == priority)
            
        if assignee_id:
            sub_stmt = sub_stmt.where(PMSubRequirement.assignee_id == assignee_id)
            
        if project_id:
            # Note: PMRequirement is already joined
            sub_stmt = sub_stmt.where(PMRequirement.project_id == project_id)
            
        if module_id:
            sub_stmt = sub_stmt.where(PMRequirement.module_id == module_id)
            
        sub_stmt = sub_stmt.distinct()
        sub_result = await db.execute(sub_stmt)
        sub_req_data = sub_result.all() # list of (PMSubRequirement, project_id)
        
        # 构建混合列表
        req_map = {}
        items = []
        
        # 1. 处理父需求
        for r in requirements:
            item = r.to_dict()
            item['is_followed'] = True
            item['children'] = [] # 初始化 children 为空，确保只包含关注的子需求
            req_map[r.req_id] = item
            items.append(item)
            
        # 2. 处理子需求
        for sub_req, project_id in sub_req_data:
            sub_item = sub_req.to_dict()
            # 适配前端字段
            sub_item['req_id'] = f"sub_{sub_req.sub_req_id}" # 使用字符串ID避免冲突
            sub_item['original_req_id'] = sub_req.sub_req_id
            sub_item['req_code'] = sub_req.sub_req_code
            sub_item['is_sub'] = True
            sub_item['parent_id'] = sub_req.requirement_id
            sub_item['children'] = []
            sub_item['is_followed'] = True
            sub_item['project_id'] = project_id
            
            # 逻辑判断：如果父需求在列表中，加入 children；否则作为独立项
            if sub_req.requirement_id in req_map:
                req_map[sub_req.requirement_id]['children'].append(sub_item)
            else:
                 # 如果父需求不在列表中（只关注了子需求），则作为顶级项展示
                 # 为了避免前端表格缩进（前端根据 parent_id 判断缩进），我们将 parent_id 设为 None
                 # 但保留 real_parent_id 供详情页使用
                 sub_item['real_parent_id'] = sub_req.requirement_id
                 sub_item['parent_id'] = None
                 items.append(sub_item)
        
        # 3. 内存分页
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        paged_items = items[start:end]
        
        # --- 针对 is_followed=True 的进度计算补丁 ---
        # 提取当前分页中的需求ID (is_sub=False)
        paged_req_ids = [i['req_id'] for i in paged_items if not i.get('is_sub')]
        
        if paged_req_ids:
            # 批量查询子需求
            sub_stmt_prog = select(PMSubRequirement).where(
                PMSubRequirement.requirement_id.in_(paged_req_ids),
                PMSubRequirement.del_flag == 0
            )
            sub_res_prog = await db.execute(sub_stmt_prog)
            all_sub_reqs_prog = sub_res_prog.scalars().all()
            
            # 批量查询子任务
            tasks_stmt_prog = select(PMTask).where(
                or_(
                    PMTask.requirement_id.in_(paged_req_ids),
                    PMTask.sub_requirement_id.in_([s.sub_req_id for s in all_sub_reqs_prog])
                ),
                PMTask.del_flag == 0
            )
            tasks_res_prog = await db.execute(tasks_stmt_prog)
            all_tasks_prog = tasks_res_prog.scalars().all()
            
            # 计算进度并更新 paged_items
            for item in paged_items:
                if item.get('is_sub'):
                    continue
                    
                rid = item['req_id']
                # 找出子项
                my_sub = [s for s in all_sub_reqs_prog if s.requirement_id == rid]
                my_sub_ids = [s.sub_req_id for s in my_sub]
                
                my_tasks_direct = [t for t in all_tasks_prog if t.requirement_id == rid]
                my_tasks_sub = [t for t in all_tasks_prog if t.sub_requirement_id in my_sub_ids]
                
                # 去重任务 (有些任务可能既有 requirement_id 又有 sub_requirement_id)
                my_tasks = {t.task_id: t for t in my_tasks_direct + my_tasks_sub}.values()
                
                all_subs = list(my_sub) + list(my_tasks)
                cnt = len(all_subs)
                
                if cnt > 0:
                    prog_sum = 0
                    for sub in all_subs:
                        p = getattr(sub, 'progress', None)
                        if p is not None:
                            prog_sum += p
                        else:
                            st = getattr(sub, 'status', 'not_started')
                            prog_sum += status_map.get(st, 0)
                    item['progress'] = round(prog_sum / cnt)
                else:
                    # 无子项，使用自身进度
                    st = item.get('status', 'not_started')
                    item['progress'] = status_map.get(st, 0)

        return {
            'code': 200, 
            'msg': 'success', 
            'data': {
                'items': paged_items,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }

    # 标准分页逻辑 (非关注列表)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    result_count = await db.execute(count_stmt)
    total = result_count.scalar()
    
    stmt = stmt.order_by(desc(PMRequirement.create_time))
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(stmt)
    requirements = result.scalars().all()
    
    # Check follow status for current page items
    followed_ids = set()
    req_ids = [r.req_id for r in requirements]
    if req_ids:
        follow_stmt = select(SysUserFollow.target_id).where(
            SysUserFollow.user_id == current_user.user_id,
            SysUserFollow.target_id.in_(req_ids),
            SysUserFollow.target_type == 'requirement'
        )
        follow_res = await db.execute(follow_stmt)
        followed_ids = set(follow_res.scalars().all())

    # --- 核心修改：计算每个需求的进度 (进度 = (子需求进度总和 + 子任务进度总和) / (子需求数 + 子任务数)) ---
    # 尝试从 Redis 缓存获取状态映射
    status_map = {}
    redis_key = "sys:dict:requirement_status_progress"
    
    try:
        cached_map = await redis.get(redis_key)
        if cached_map:
            status_map = json.loads(cached_map)
    except Exception as e:
        print(f"Failed to read from Redis: {e}")

    # 如果缓存未命中，尝试从数据库字典获取
    if not status_map:
        try:
            # 获取 dict_id
            type_stmt = select(SysDictType).where(SysDictType.dict_type == 'requirement_status_progress')
            type_res = await db.execute(type_stmt)
            dict_type = type_res.scalar_one_or_none()
            
            if dict_type:
                data_stmt = select(SysDictData).where(SysDictData.dict_id == dict_type.dict_id, SysDictData.status == 1)
                data_res = await db.execute(data_stmt)
                dict_data = data_res.scalars().all()
                
                for d in dict_data:
                    # Value is string in DB, convert to int
                    try:
                        status_map[d.dict_label] = int(d.dict_value)
                    except:
                        pass
                
                # 写入 Redis 缓存 (过期时间 1 小时)
                if status_map:
                    try:
                        await redis.set(redis_key, json.dumps(status_map), ex=3600)
                    except Exception as e:
                        print(f"Failed to write to Redis: {e}")
        except Exception as e:
            print(f"Failed to load status map from DB: {e}")
        
    # 如果数据库也没数据，回退到常量文件
    if not status_map:
        status_map = REQUIREMENT_STATUS_PROGRESS_MAP
    
    # 批量查询关联的子需求
    sub_reqs_stmt = select(PMSubRequirement).where(
        PMSubRequirement.requirement_id.in_(req_ids),
        PMSubRequirement.del_flag == 0
    )
    
    # Apply filters to sub_reqs_stmt (standard pagination)
    if type:
        if type == 'unclassified':
             sub_reqs_stmt = sub_reqs_stmt.where(or_(
                 PMSubRequirement.type.not_in(['product', 'tech', 'bug']),
                 PMSubRequirement.type == None
             ))
        else:
            sub_reqs_stmt = sub_reqs_stmt.where(PMSubRequirement.type == type)
            
    if status:
        sub_reqs_stmt = sub_reqs_stmt.where(PMSubRequirement.status == status)
        
    if priority:
        sub_reqs_stmt = sub_reqs_stmt.where(PMSubRequirement.priority == priority)
        
    if assignee_id:
        sub_reqs_stmt = sub_reqs_stmt.where(PMSubRequirement.assignee_id == assignee_id)
        
    # 增加排序，确保子需求顺序正确
    sub_reqs_stmt = sub_reqs_stmt.order_by(PMSubRequirement.sort_order)
    sub_reqs_res = await db.execute(sub_reqs_stmt)
    all_sub_reqs = sub_reqs_res.scalars().all()
    
    # 批量查询关联的子任务 (直接关联父需求的，或关联子需求的)
    # 1. 直接关联父需求的任务
    tasks_stmt_direct = select(PMTask).where(
        PMTask.requirement_id.in_(req_ids),
        PMTask.del_flag == 0
    )
    tasks_direct_res = await db.execute(tasks_stmt_direct)
    all_tasks_direct = tasks_direct_res.scalars().all()
    
    # 2. 关联子需求的任务 (需要先拿到子需求ID列表)
    sub_req_ids = [s.sub_req_id for s in all_sub_reqs]
    all_tasks_sub = []
    if sub_req_ids:
        tasks_stmt_sub = select(PMTask).where(
            PMTask.sub_requirement_id.in_(sub_req_ids),
            PMTask.del_flag == 0
        )
        tasks_sub_res = await db.execute(tasks_stmt_sub)
        all_tasks_sub = tasks_sub_res.scalars().all()

    # 组装数据并计算进度
    final_items = []
    for r in requirements:
        item = r.to_dict()
        item['is_followed'] = r.req_id in followed_ids
        
        # 找出该需求下的所有子项
        my_sub_reqs = [s for s in all_sub_reqs if s.requirement_id == r.req_id]
        my_tasks_direct = [t for t in all_tasks_direct if t.requirement_id == r.req_id]
        
        # 找出该需求下子需求的子任务
        my_sub_req_ids = [s.sub_req_id for s in my_sub_reqs]
        my_tasks_sub = [t for t in all_tasks_sub if t.sub_requirement_id in my_sub_req_ids]
        
        all_my_items = my_sub_reqs + my_tasks_direct + my_tasks_sub
        total_count = len(all_my_items)
        
        # 构建 children 结构
        item['children'] = []
        for sub_req in my_sub_reqs:
            sub_item = sub_req.to_dict()
            sub_item['req_id'] = f"sub_{sub_req.sub_req_id}"
            sub_item['original_req_id'] = sub_req.sub_req_id
            sub_item['req_code'] = sub_req.sub_req_code
            sub_item['is_sub'] = True
            sub_item['parent_id'] = sub_req.requirement_id
            sub_item['children'] = []
            
            # Check follow status for sub-requirements if needed (optional optimization)
            # Currently frontend might assume parent follow implies child follow or separate
            # For now let's leave is_followed False for children unless we query it
            
            item['children'].append(sub_item)
            
        if total_count > 0:
            total_progress = 0
            for sub_item in all_my_items:
                # 优先使用 progress 字段 (如果模型中有)，否则使用 status 映射
                p = getattr(sub_item, 'progress', None)
                if p is not None:
                    total_progress += p
                else:
                    status = getattr(sub_item, 'status', 'not_started')
                    total_progress += status_map.get(status, 0)
            
            item['progress'] = round(total_progress / total_count)
        else:
            # 无子项，使用自身进度 (status 映射)
            item['progress'] = status_map.get(r.status, 0)
            
        final_items.append(item)
    
    # 统一映射用户昵称
    await enrich_usernames_with_nicknames(db, final_items)

    return {
        'code': 200, 
        'msg': 'success', 
        'data': {
            'items': final_items,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    }

@router.post("/create", response_model=dict)
async def create_requirement(
    req_in: RequirementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    创建需求
    """
    try:
        # 处理模块即时创建
        final_module_id = None
        if req_in.module_id is not None:
            if isinstance(req_in.module_id, int):
                final_module_id = req_in.module_id
            elif isinstance(req_in.module_id, str):
                if req_in.module_id.isdigit():
                    final_module_id = int(req_in.module_id)
                else:
                    # 尝试查找是否存在同名模块
                    stmt = select(PMModule).where(
                        PMModule.module_name == req_in.module_id,
                        PMModule.project_id == req_in.project_id
                    )
                    result = await db.execute(stmt)
                    existing_module = result.scalar_one_or_none()
                    
                    if existing_module:
                        final_module_id = existing_module.module_id
                    else:
                        # 创建新模块
                        new_module = PMModule(
                            module_name=req_in.module_id,
                            project_id=req_in.project_id,
                            description=f"Auto created for requirement",
                            create_by=current_user.username
                        )
                        db.add(new_module)
                        await db.flush() # 获取 ID 但不提交事务
                        final_module_id = new_module.module_id

        new_req = PMRequirement(
            title=req_in.title,
            type=req_in.type,
            priority=req_in.priority,
            status=req_in.status,
            project_id=req_in.project_id,
            module_id=final_module_id,
            parent_id=req_in.parent_id,
            assignee_id=req_in.assignee_id,
            developer_id=req_in.developer_id,
            tester_id=req_in.tester_id,
            accepter_id=req_in.accepter_id,
            start_date=req_in.start_date,
            end_date=req_in.end_date,
            description=req_in.description,
            iteration_id=req_in.iteration_id,
            risk_level=req_in.risk_level,
            tags=req_in.tags,
            attachments=req_in.attachments,
            create_by=current_user.username
        )
        db.add(new_req)
        await db.commit()
        await db.refresh(new_req)
        
        # 生成 req_code
        stmt = select(PMRequirement.req_code).order_by(desc(PMRequirement.req_code)).limit(1)
        result = await db.execute(stmt)
        last_req_code = result.scalar_one_or_none()
        
        if last_req_code and last_req_code.isdigit():
            new_req.req_code = str(int(last_req_code) + 1)
        else:
            new_req.req_code = "100000001"
            
        db.add(new_req)
        await db.commit()
        await db.refresh(new_req)
        
        # 触发自动化助手 - 需求分配事件
        if new_req.assignee_id:
            await AutomationService.trigger_event(
                'requirement:assign',
                {'requirement_id': new_req.req_id, 'assignee_id': new_req.assignee_id, 'trigger': 'requirement_create'},
                db,
                current_user.nickname or current_user.username
            )
        else:
             await AutomationService.trigger_event(
                'requirement:update',
                {'requirement_id': new_req.req_id, 'trigger': 'requirement_create'},
                db,
                current_user.nickname or current_user.username
            )
        
        return {'code': 200, 'msg': 'success', 'data': new_req.to_dict()}
    except Exception as e:
        import traceback
        print(f"Error creating requirement: {e}\n{traceback.format_exc()}")
        return {'code': 500, 'msg': f"Server Error: {str(e)}", 'data': None}


@router.put("/update", response_model=dict)
async def update_requirement(
    req_in: RequirementUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    更新需求
    """
    stmt = select(PMRequirement).where(PMRequirement.req_id == req_in.req_id)
    result = await db.execute(stmt)
    req = result.scalar_one_or_none()
    
    if not req:
        return {'code': 404, 'msg': '需求不存在', 'data': None}
        
    update_data = req_in.dict(exclude_unset=True)
    if 'req_id' in update_data:
        del update_data['req_id']
        
    # 如果状态变更为 completed 或 online，更新 completed_at
    if update_data.get('status') in ['completed', 'online']:
        update_data['completed_at'] = datetime.now()
    elif update_data.get('status') and update_data.get('status') not in ['completed', 'online']:
        # 如果状态变为非完成态，清除完成时间
        update_data['completed_at'] = None
        
    update_data['update_by'] = current_user.username
    
    stmt = update(PMRequirement).where(PMRequirement.req_id == req_in.req_id).values(**update_data)
    await db.execute(stmt)
    await db.commit()
    await db.refresh(req)
    
    # 触发自动化助手 - 需求更新事件
    if 'assignee_id' in update_data:
        await AutomationService.trigger_event(
            'requirement:assign',
            {'requirement_id': req.req_id, 'assignee_id': req.assignee_id},
            db,
            current_user.nickname or current_user.username
        )
    else:
        await AutomationService.trigger_event(
            'requirement:update', 
            {'requirement_id': req.req_id, 'trigger': 'requirement_update'},
            db, 
            current_user.nickname or current_user.username
        )
    
    return {'code': 200, 'msg': 'success', 'data': req.to_dict()}

@router.get("/statistics", response_model=dict)
async def get_requirement_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取需求统计信息
    """
    # 1. 按类型统计 (PMRequirement)
    stmt_type = select(PMRequirement.type, func.count(PMRequirement.req_id)).where(PMRequirement.del_flag == 0).group_by(PMRequirement.type)
    result_type = await db.execute(stmt_type)
    type_stats = result_type.all()
    
    type_data = {t[0]: t[1] for t in type_stats}
    
    # 2. 按项目统计
    stmt_project = select(
        PMProject.project_id,
        PMProject.project_name,
        func.count(PMRequirement.req_id)
    ).join(
        PMRequirement, 
        PMProject.project_id == PMRequirement.project_id
    ).where(
        PMRequirement.del_flag == 0
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
    
    # 3. 统计我的关注 (SysUserFollow)
    # 统计未删除的关注父需求
    stmt_follow_req = select(func.count(SysUserFollow.follow_id)).join(
        PMRequirement,
        (SysUserFollow.target_id == PMRequirement.req_id) & (SysUserFollow.target_type == 'requirement')
    ).where(
        SysUserFollow.user_id == current_user.user_id,
        PMRequirement.del_flag == 0
    )
    
    # 统计未删除的关注子需求
    stmt_follow_sub = select(func.count(SysUserFollow.follow_id)).join(
        PMSubRequirement,
        (SysUserFollow.target_id == PMSubRequirement.sub_req_id) & (SysUserFollow.target_type == 'sub_requirement')
    ).where(
        SysUserFollow.user_id == current_user.user_id,
        PMSubRequirement.del_flag == 0
    )
    
    result_follow_req = await db.execute(stmt_follow_req)
    count_req = result_follow_req.scalar() or 0
    
    result_follow_sub = await db.execute(stmt_follow_sub)
    count_sub = result_follow_sub.scalar() or 0
    
    follow_count = count_req + count_sub
    
    # 4. 汇总数据
    total_count = sum(type_data.values())
    product_count = type_data.get('product', 0)
    tech_count = type_data.get('tech', 0)
    bug_count = type_data.get('bug', 0)
    
    # 计算未分类 (总数 - 已知类型)
    known_count = product_count + tech_count + bug_count
    unclassified_count = total_count - known_count
    
    data = {
        "all": total_count,
        "unclassified": unclassified_count,
        "product": product_count,
        "tech": tech_count,
        "bug": bug_count,
        "follow": follow_count,
        "projects": projects_data
    }
    
    return {'code': 200, 'msg': 'success', 'data': data}

@router.delete("/{req_id}", response_model=dict)
async def delete_requirement(
    req_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除需求
    """
    stmt = update(PMRequirement).where(PMRequirement.req_id == req_id).values(del_flag=1)
    await db.execute(stmt)
    await db.commit()
    
    return {'code': 200, 'msg': 'success', 'data': None}

@router.get("/{req_id}", response_model=dict)
async def get_requirement_detail(
    req_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取需求详情
    """
    stmt = select(PMRequirement).where(
        PMRequirement.req_id == req_id,
        PMRequirement.del_flag == 0
    )
    result = await db.execute(stmt)
    req = result.scalar_one_or_none()
    
    if not req:
        return {'code': 404, 'msg': '需求不存在', 'data': None}
        
    data = req.to_dict()
    # 统一映射用户昵称
    await enrich_usernames_with_nicknames(db, data)
    
    return {'code': 200, 'msg': 'success', 'data': data}

@router.put("/update_sort", response_model=dict)
async def update_requirement_sort(
    sort_data: List[dict], # [{"req_id": 1, "sort_order": 1}, ...]
    db: AsyncSession = Depends(get_db)
):
    """
    更新需求排序
    """
    for item in sort_data:
        stmt = update(PMRequirement).where(PMRequirement.req_id == item['req_id']).values(sort_order=item['sort_order'])
        await db.execute(stmt)
    
    await db.commit()
    return {'code': 200, 'msg': 'success', 'data': None}


# --- 模块管理接口 ---

@router.get("/module/list", response_model=dict)
async def get_module_list(
    project_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取模块列表
    """
    stmt = select(PMModule)
    if project_id:
        stmt = stmt.where(PMModule.project_id == project_id)
        
    result = await db.execute(stmt)
    modules = result.scalars().all()
    
    return {'code': 200, 'msg': 'success', 'data': [m.to_dict() for m in modules]}

@router.post("/module/create", response_model=dict)
async def create_module(
    module_in: ModuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    创建模块
    """
    new_module = PMModule(
        module_name=module_in.module_name,
        project_id=module_in.project_id,
        description=module_in.description,
        create_by=current_user.nickname or current_user.username
    )
    db.add(new_module)
    await db.commit()
    await db.refresh(new_module)
    
    return {'code': 200, 'msg': 'success', 'data': new_module.to_dict()}


# --- 详情获取接口 ---

@router.get("/detail/{item_id}", response_model=dict)
async def get_item_detail(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    根据ID获取详情（自动识别需求、子需求、任务）
    """
    # 1. Try Requirement (Parent)
    stmt = select(PMRequirement).where(PMRequirement.req_id == item_id)
    result = await db.execute(stmt)
    req = result.scalar_one_or_none()
    if req:
        data = req.to_dict()
        data['type_category'] = 'requirement'
        # 统一映射用户昵称
        await enrich_usernames_with_nicknames(db, data)
        return {'code': 200, 'msg': 'success', 'data': data}

    # 2. Try SubRequirement
    stmt = select(PMSubRequirement).where(PMSubRequirement.sub_req_id == item_id)
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()
    if sub:
        data = sub.to_dict()
        data['type_category'] = 'sub_requirement'
        # Frontend compatibility
        data['req_id'] = f"sub_{sub.sub_req_id}" 
        data['is_sub'] = True
        data['original_req_id'] = sub.sub_req_id
        
        # 统一映射用户昵称
        await enrich_usernames_with_nicknames(db, data)
                
        return {'code': 200, 'msg': 'success', 'data': data}

    # 3. Try Task
    stmt = select(PMTask).where(PMTask.task_id == item_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if task:
        data = task.to_dict()
        data['type_category'] = 'task'
        
        # 统一映射用户昵称
        await enrich_usernames_with_nicknames(db, data)
                
        return {'code': 200, 'msg': 'success', 'data': data}

    return {'code': 404, 'msg': '未找到相关记录', 'data': None}


# --- 子需求管理接口 ---

@router.get("/sub_requirements/list", response_model=dict)
async def get_sub_requirements(
    requirement_id: Optional[int] = None,
    parent_sub_id: Optional[int] = None,
    is_followed: Optional[bool] = False,
    type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search_term: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取子需求列表
    """
    stmt = select(PMSubRequirement).where(PMSubRequirement.del_flag == 0)
    
    if is_followed:
        stmt = stmt.join(
            SysUserFollow,
            (SysUserFollow.target_id == PMSubRequirement.sub_req_id) & (SysUserFollow.target_type == 'sub_requirement')
        ).where(SysUserFollow.user_id == current_user.user_id)
    
    if requirement_id:
        stmt = stmt.where(PMSubRequirement.requirement_id == requirement_id)
    
    if parent_sub_id:
        stmt = stmt.where(PMSubRequirement.parent_sub_id == parent_sub_id)

    if search_term:
        stmt = stmt.where(or_(
            PMSubRequirement.title.like(f"%{search_term}%"),
            PMSubRequirement.sub_req_code.like(f"%{search_term}%")
        ))

    if type:
        if type == 'unclassified':
             stmt = stmt.where(or_(
                 PMSubRequirement.type.not_in(['product', 'tech', 'bug']),
                 PMSubRequirement.type == None
             ))
        else:
            stmt = stmt.where(PMSubRequirement.type == type)
            
    if status:
        stmt = stmt.where(PMSubRequirement.status == status)
        
    if priority:
        stmt = stmt.where(PMSubRequirement.priority == priority)
        
    if assignee_id:
        stmt = stmt.where(PMSubRequirement.assignee_id == assignee_id)
        
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            # 筛选开始时间晚于等于查询开始时间的需求
            stmt = stmt.where(PMSubRequirement.start_date >= start_dt)
        except ValueError:
            pass
            
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            # 筛选结束时间早于等于查询结束时间的需求
            stmt = stmt.where(PMSubRequirement.start_date <= end_dt)
        except ValueError:
            pass
        
    stmt = stmt.order_by(PMSubRequirement.sort_order)
    
    result = await db.execute(stmt)
    sub_reqs = result.scalars().all()
    
    # Check follow status for current page items
    followed_ids = set()
    req_ids = [r.sub_req_id for r in sub_reqs]
    if req_ids:
        follow_stmt = select(SysUserFollow.target_id).where(
            SysUserFollow.user_id == current_user.user_id,
            SysUserFollow.target_id.in_(req_ids),
            SysUserFollow.target_type == 'sub_requirement'
        )
        follow_res = await db.execute(follow_stmt)
        followed_ids = set(follow_res.scalars().all())

    items = []
    for r in sub_reqs:
        item = r.to_dict()
        item['is_followed'] = r.sub_req_id in followed_ids
        items.append(item)
    
    # 统一映射用户昵称
    await enrich_usernames_with_nicknames(db, items)
    
    return {'code': 200, 'msg': 'success', 'data': {'items': items}}

@router.post("/sub_requirements/create", response_model=dict)
async def create_sub_requirement(
    sub_req_in: SubRequirementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    创建子需求
    """
    new_sub_req = PMSubRequirement(
        title=sub_req_in.title,
        type=sub_req_in.type,
        priority=sub_req_in.priority,
        status=sub_req_in.status,
        requirement_id=sub_req_in.requirement_id,
        parent_sub_id=sub_req_in.parent_sub_id,
        assignee_id=sub_req_in.assignee_id,
        start_date=sub_req_in.start_date,
        end_date=sub_req_in.end_date,
        risk_level=sub_req_in.risk_level,
        sort_order=sub_req_in.sort_order,
        attachments=sub_req_in.attachments,
        create_by=current_user.username
    )
    db.add(new_sub_req)
    await db.commit()
    await db.refresh(new_sub_req)
    
    # 生成 sub_req_code
    stmt = select(PMSubRequirement.sub_req_code).order_by(desc(PMSubRequirement.sub_req_code)).limit(1)
    result = await db.execute(stmt)
    last_sub_req_code = result.scalar_one_or_none()
    
    if last_sub_req_code and last_sub_req_code.isdigit():
        new_sub_req.sub_req_code = str(int(last_sub_req_code) + 1)
    else:
        new_sub_req.sub_req_code = "100000001"
        
    db.add(new_sub_req)
    await db.commit()
    await db.refresh(new_sub_req)
    
    # 触发自动化助手 - 子需求更新事件
    await AutomationService.trigger_event(
        'requirement:update', 
        {'sub_req_id': new_sub_req.sub_req_id, 'trigger': 'sub_requirement_create'},
        db, 
        current_user.nickname or current_user.username
    )
    
    return {'code': 200, 'msg': 'success', 'data': new_sub_req.to_dict()}

@router.put("/sub_requirements/update", response_model=dict)
async def update_sub_requirement(
    sub_req_in: SubRequirementUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    更新子需求
    """
    stmt = select(PMSubRequirement).where(PMSubRequirement.sub_req_id == sub_req_in.sub_req_id)
    result = await db.execute(stmt)
    sub_req = result.scalar_one_or_none()
    
    if not sub_req:
        return {'code': 404, 'msg': '子需求不存在', 'data': None}
        
    update_data = sub_req_in.dict(exclude_unset=True)
    if 'sub_req_id' in update_data:
        del update_data['sub_req_id']
        
    # 如果状态变更为 completed 或 online，更新 completed_at
    if update_data.get('status') in ['completed', 'online']:
        update_data['completed_at'] = datetime.now()
    elif update_data.get('status') and update_data.get('status') not in ['completed', 'online']:
        # 如果状态变为非完成态，清除完成时间
        update_data['completed_at'] = None
    elif update_data.get('status') and update_data.get('status') != 'completed':
        # 如果状态变为非完成态，清除完成时间
        update_data['completed_at'] = None
        
    update_data['update_by'] = current_user.username
    
    stmt = update(PMSubRequirement).where(PMSubRequirement.sub_req_id == sub_req_in.sub_req_id).values(**update_data)
    await db.execute(stmt)
    await db.commit()
    await db.refresh(sub_req)
    
    # 触发自动化助手 - 子需求更新事件 (复用 requirement:update 事件，但在 context 中传递 sub_req_id)
    await AutomationService.trigger_event(
        'requirement:update', 
        {'sub_req_id': sub_req.sub_req_id, 'trigger': 'sub_requirement_update'},
        db, 
        current_user.nickname or current_user.username
    )
    
    return {'code': 200, 'msg': 'success', 'data': sub_req.to_dict()}

@router.delete("/sub_requirements/{sub_req_id}", response_model=dict)
async def delete_sub_requirement(
    sub_req_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    删除子需求
    """
    # 先查询子需求，获取 parent_id 用于触发事件
    stmt_check = select(PMSubRequirement).where(PMSubRequirement.sub_req_id == sub_req_id)
    res_check = await db.execute(stmt_check)
    sub_req = res_check.scalar_one_or_none()
    
    if not sub_req:
        return {'code': 404, 'msg': '子需求不存在', 'data': None}
        
    stmt = update(PMSubRequirement).where(PMSubRequirement.sub_req_id == sub_req_id).values(del_flag=1)
    await db.execute(stmt)
    await db.commit()
    
    # 触发自动化助手 - 子需求更新事件 (删除也是更新的一种)
    # if sub_req.requirement_id:
    #     await AutomationService.trigger_event(
    #         'requirement:child:update', 
    #         {'requirement_id': sub_req.requirement_id, 'sub_req_id': sub_req.sub_req_id, 'trigger': 'sub_requirement_delete'},
    #         db, 
    #         current_user.nickname or current_user.username
    #     )
    
    return {'code': 200, 'msg': 'success', 'data': None}

@router.put("/sub_requirements/update_sort", response_model=dict)
async def update_sub_requirement_sort(
    sort_data: List[dict], # [{"sub_req_id": 1, "sort_order": 1}, ...]
    db: AsyncSession = Depends(get_db)
):
    """
    更新子需求排序
    """
    for item in sort_data:
        stmt = update(PMSubRequirement).where(PMSubRequirement.sub_req_id == item['sub_req_id']).values(sort_order=item['sort_order'])
        await db.execute(stmt)
    
    await db.commit()
    return {'code': 200, 'msg': 'success', 'data': None}


# --- 子任务管理接口 ---

@router.get("/tasks/list", response_model=dict)
async def get_tasks(
    requirement_id: Optional[int] = None,
    sub_requirement_id: Optional[int] = None,
    search_term: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取任务列表
    """
    stmt = select(PMTask).where(PMTask.del_flag == 0)
    
    if requirement_id:
        stmt = stmt.where(PMTask.requirement_id == requirement_id)
        
    if sub_requirement_id:
        stmt = stmt.where(PMTask.sub_requirement_id == sub_requirement_id)
    
    if search_term:
        # 尝试转换为ID或直接匹配标题/task_code
        try:
            search_id = int(search_term)
            stmt = stmt.where(or_(
                PMTask.title.like(f"%{search_term}%"),
                PMTask.task_code.like(f"%{search_term}%"),
                PMTask.task_id == search_id
            ))
        except ValueError:
            stmt = stmt.where(or_(
                PMTask.title.like(f"%{search_term}%"),
                PMTask.task_code.like(f"%{search_term}%")
            ))
            
    stmt = stmt.order_by(PMTask.sort_order)
    
    result = await db.execute(stmt)
    tasks = result.scalars().all()
    
    items = [t.to_dict() for t in tasks]
    
    # 统一映射用户昵称
    await enrich_usernames_with_nicknames(db, items)
    
    return {'code': 200, 'msg': 'success', 'data': items}

@router.post("/tasks/create", response_model=dict)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    创建任务
    """
    new_task = PMTask(
        title=task_in.title,
        estimate_time=task_in.estimate_time,
        assignee_id=task_in.assignee_id,
        status=task_in.status,
        priority=task_in.priority,
        start_date=task_in.start_date,
        end_date=task_in.end_date,
        sort_order=task_in.sort_order,
        requirement_id=task_in.requirement_id,
        sub_requirement_id=task_in.sub_requirement_id,
        create_by=current_user.username
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # 自动生成 task_code: 1000000 + task_id
    stmt = select(PMTask.task_code).order_by(desc(PMTask.task_code)).limit(1)
    result = await db.execute(stmt)
    last_task_code = result.scalar_one_or_none()
    if last_task_code and last_task_code.isdigit():
        new_task.task_code = str(int(last_task_code) + 1)
    else:
        new_task.task_code = "10000001"
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    # 触发自动化助手 - 任务更新事件 (创建也是更新的一种)
    # target_req_id = new_task.requirement_id
    # if not target_req_id and new_task.sub_requirement_id:
    #     sub_stmt = select(PMSubRequirement).where(PMSubRequirement.sub_req_id == new_task.sub_requirement_id)
    #     sub_res = await db.execute(sub_stmt)
    #     sub_req = sub_res.scalar_one_or_none()
    #     if sub_req:
    #         target_req_id = sub_req.requirement_id
            
    # if target_req_id:
    #     await AutomationService.trigger_event(
    #         'requirement:child:update', 
    #         {'requirement_id': target_req_id, 'task_id': new_task.task_id, 'trigger': 'task_create'},
    #         db, 
    #         current_user.nickname or current_user.username
    #     )
        
    # 同时触发 task:assign
    if new_task.assignee_id:
        await AutomationService.trigger_event(
            'task:assign',
            {'task_id': new_task.task_id, 'assignee_id': new_task.assignee_id, 'task_title': new_task.title, 'trigger': 'task_create'},
            db,
            current_user.nickname or current_user.username
        )
    else:
        await AutomationService.trigger_event(
            'task:update',
            {'task_id': new_task.task_id, 'trigger': 'task_create'},
            db,
            current_user.nickname or current_user.username
        )
    
    return {'code': 200, 'msg': 'success', 'data': new_task.to_dict()}

@router.put("/tasks/update", response_model=dict)
async def update_task(
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    更新任务
    """
    stmt = select(PMTask).where(PMTask.task_id == task_in.task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    
    if not task:
        return {'code': 404, 'msg': '任务不存在', 'data': None}
        
    update_data = task_in.dict(exclude_unset=True)
    if 'task_id' in update_data:
        del update_data['task_id']
        
    # 如果状态变更为 completed，更新 completed_at
    if update_data.get('status') == 'completed':
        update_data['completed_at'] = datetime.now()
        
    update_data['update_by'] = current_user.username
    
    stmt = update(PMTask).where(PMTask.task_id == task_in.task_id).values(**update_data)
    await db.execute(stmt)
    await db.commit()
    await db.refresh(task)
    
    # 触发自动化助手 - 任务更新事件
    if 'assignee_id' in update_data:
        await AutomationService.trigger_event(
            'task:assign',
            {'task_id': task.task_id, 'assignee_id': task.assignee_id},
            db,
            current_user.nickname or current_user.username
        )
    else:
        await AutomationService.trigger_event(
            'task:update',
            {'task_id': task.task_id},
            db,
            current_user.nickname or current_user.username
        )
    
    return {'code': 200, 'msg': 'success', 'data': task.to_dict()}

@router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    删除任务
    """
    # 先查询任务，获取 parent_id 用于触发事件
    stmt_check = select(PMTask).where(PMTask.task_id == task_id)
    res_check = await db.execute(stmt_check)
    task = res_check.scalar_one_or_none()
    
    if not task:
        return {'code': 404, 'msg': '任务不存在', 'data': None}
        
    stmt = update(PMTask).where(PMTask.task_id == task_id).values(del_flag=1)
    await db.execute(stmt)
    await db.commit()
    
    # 触发自动化助手 - 任务更新事件
    # target_req_id = task.requirement_id
    # if not target_req_id and task.sub_requirement_id:
    #     sub_stmt = select(PMSubRequirement).where(PMSubRequirement.sub_req_id == task.sub_requirement_id)
    #     sub_res = await db.execute(sub_stmt)
    #     sub_req = sub_res.scalar_one_or_none()
    #     if sub_req:
    #         target_req_id = sub_req.requirement_id
            
    # if target_req_id:
    #     await AutomationService.trigger_event(
    #         'requirement:child:update', 
    #         {'requirement_id': target_req_id, 'task_id': task.task_id, 'trigger': 'task_delete'},
    #         db, 
    #         current_user.nickname or current_user.username
    #     )
    
    return {'code': 200, 'msg': 'success', 'data': None}

@router.put("/tasks/update_sort", response_model=dict)
async def update_task_sort(
    sort_data: List[dict], # [{"task_id": 1, "sort_order": 1}, ...]
    db: AsyncSession = Depends(get_db)
):
    """
    更新任务排序
    """
    for item in sort_data:
        stmt = update(PMTask).where(PMTask.task_id == item['task_id']).values(sort_order=item['sort_order'])
        await db.execute(stmt)
    
    await db.commit()
    return {'code': 200, 'msg': 'success', 'data': None}
