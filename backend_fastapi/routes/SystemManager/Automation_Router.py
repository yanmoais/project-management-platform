from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, update
from backend_fastapi.core.deps import get_db, get_current_user
from backend_fastapi.models.sys_automation_models import SysAutomationRule, SysAutomationLog
from backend_fastapi.models.sys_models import SysUser
from backend_fastapi.services.automation_service import AutomationService
from typing import List, Optional

router = APIRouter(tags=["自动化助手"])

from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class AutomationRuleCreate(BaseModel):
    rule_name: str
    rule_code: str
    description: Optional[str] = None
    trigger_event: str
    conditions: Optional[Dict] = None
    actions: Optional[List[Dict]] = None # 保留但可选，兼容旧数据
    is_active: bool = True
    priority: int = 0
    
    # New fields
    rule_type: Optional[str] = 'event'
    cron_expression: Optional[str] = None
    query_config: Optional[Dict] = None

class AutomationRuleUpdate(BaseModel):
    rule_id: int
    rule_name: Optional[str] = None
    description: Optional[str] = None
    trigger_event: Optional[str] = None
    conditions: Optional[Dict] = None
    actions: Optional[List[Dict]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    
    # New fields
    rule_type: Optional[str] = None
    cron_expression: Optional[str] = None
    query_config: Optional[Dict] = None

@router.get("/metadata", response_model=dict)
async def get_automation_metadata(
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取自动化规则元数据 (Events, Conditions, Actions)
    """
    return {'code': 200, 'msg': 'success', 'data': AutomationService.get_metadata()}

@router.post("/rules/create", response_model=dict)
async def create_automation_rule(
    rule_in: AutomationRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    创建自动化规则
    """
    # Check if code exists
    stmt = select(SysAutomationRule).where(SysAutomationRule.rule_code == rule_in.rule_code)
    if (await db.execute(stmt)).scalar_one_or_none():
        return {'code': 400, 'msg': '规则编码已存在', 'data': None}
        
    new_rule = SysAutomationRule(
        rule_name=rule_in.rule_name,
        rule_code=rule_in.rule_code,
        description=rule_in.description,
        trigger_event=rule_in.trigger_event,
        conditions=rule_in.conditions,
        actions=rule_in.actions,
        is_active=rule_in.is_active,
        priority=rule_in.priority,
        rule_type=rule_in.rule_type,
        cron_expression=rule_in.cron_expression,
        query_config=rule_in.query_config,
        create_by=current_user.nickname or current_user.username
    )
    db.add(new_rule)
    await db.commit()
    await db.refresh(new_rule)
    
    return {'code': 200, 'msg': 'success', 'data': {'rule_id': new_rule.rule_id}}

@router.put("/rules/update", response_model=dict)
async def update_automation_rule(
    rule_in: AutomationRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    更新自动化规则
    """
    stmt = select(SysAutomationRule).where(SysAutomationRule.rule_id == rule_in.rule_id)
    rule = (await db.execute(stmt)).scalar_one_or_none()
    
    if not rule:
        return {'code': 404, 'msg': '规则不存在', 'data': None}
        
    update_data = rule_in.dict(exclude_unset=True)
    if 'rule_id' in update_data:
        del update_data['rule_id']
        
    update_data['update_by'] = current_user.nickname or current_user.username
    
    stmt = update(SysAutomationRule).where(SysAutomationRule.rule_id == rule_in.rule_id).values(**update_data)
    await db.execute(stmt)
    await db.commit()
    
    return {'code': 200, 'msg': 'success', 'data': None}

@router.delete("/rules/{rule_id}", response_model=dict)
async def delete_automation_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    删除自动化规则
    """
    # 物理删除，或标记删除（SysAutomationRule目前没有del_flag，直接物理删除）
    stmt = select(SysAutomationRule).where(SysAutomationRule.rule_id == rule_id)
    rule = (await db.execute(stmt)).scalar_one_or_none()
    
    if not rule:
        return {'code': 404, 'msg': '规则不存在', 'data': None}
        
    await db.delete(rule)
    await db.commit()
    
    return {'code': 200, 'msg': 'success', 'data': None}

@router.get("/rules", response_model=dict)
async def get_automation_rules(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取自动化规则列表
    """
    # 尝试初始化默认规则
    await AutomationService.initialize_default_rules(db)
    
    stmt = select(SysAutomationRule).where(SysAutomationRule.is_active == True)
    
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()
    
    stmt = stmt.order_by(SysAutomationRule.priority.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(stmt)
    rules = result.scalars().all()
    
    data = []
    for r in rules:
        data.append({
            'rule_id': r.rule_id,
            'rule_name': r.rule_name,
            'rule_code': r.rule_code,
            'description': r.description,
            'trigger_event': r.trigger_event,
            'conditions': r.conditions,
            'actions': r.actions,
            'is_active': r.is_active,
            'priority': r.priority,
            'rule_type': r.rule_type,
            'cron_expression': r.cron_expression,
            'query_config': r.query_config
        })
    
    return {'code': 200, 'msg': 'success', 'data': {'items': data, 'total': total}}

@router.get("/logs", response_model=dict)
async def get_automation_logs(
    page: int = 1,
    page_size: int = 20,
    rule_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取自动化执行日志
    """
    stmt = select(SysAutomationLog)
    
    if rule_id:
        stmt = stmt.where(SysAutomationLog.rule_id == rule_id)
        
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()
    
    stmt = stmt.order_by(desc(SysAutomationLog.execution_time))
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    data = []
    for l in logs:
        data.append({
            'log_id': l.log_id,
            'rule_name': l.rule_name,
            'trigger_event': l.trigger_event,
            'target_id': l.target_id,
            'execution_status': l.execution_status,
            'execution_result': l.execution_result,
            'execution_time': l.execution_time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    return {'code': 200, 'msg': 'success', 'data': {'items': data, 'total': total}}
