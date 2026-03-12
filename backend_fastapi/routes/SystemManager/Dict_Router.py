from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, desc
from typing import List, Optional
from backend_fastapi.db.session import get_db
from backend_fastapi.models.sys_dict_models import SysDictType, SysDictData
from backend_fastapi.core.deps import get_current_user
from backend_fastapi.models.sys_models import SysUser
from .dict_schemas import DictDataResponse, DictDataCreate
from datetime import datetime
from backend_fastapi.core.constants import REQUIREMENT_STATUS_PROGRESS_MAP

router = APIRouter(tags=["字典管理"])

@router.post("/init_constants", response_model=dict)
async def init_constants_to_db(
    db: AsyncSession = Depends(get_db)
):
    """
    将系统常量初始化到字典表 (无需鉴权，供系统初始化使用)
    """
    # 1. 初始化 REQUIREMENT_STATUS_PROGRESS_MAP
    dict_type = 'requirement_status_progress'
    dict_name = '需求状态进度映射'
    
    # Check type
    query_type = select(SysDictType).where(SysDictType.dict_type == dict_type)
    result_type = await db.execute(query_type)
    dict_type_obj = result_type.scalar_one_or_none()
    
    if not dict_type_obj:
        dict_type_obj = SysDictType(
            dict_name=dict_name,
            dict_type=dict_type,
            status=1,
            remark='系统自动初始化',
            create_by='system',
            create_time=datetime.now()
        )
        db.add(dict_type_obj)
        await db.commit()
        await db.refresh(dict_type_obj)
    
    # Check data and insert if not exists
    # First, get existing data keys
    query_data = select(SysDictData).where(SysDictData.dict_id == dict_type_obj.dict_id)
    result_data = await db.execute(query_data)
    existing_data = result_data.scalars().all()
    existing_keys = {item.dict_label for item in existing_data}
    
    sort_order = 1
    for status, progress in REQUIREMENT_STATUS_PROGRESS_MAP.items():
        if status not in existing_keys:
            new_data = SysDictData(
                dict_id=dict_type_obj.dict_id,
                dict_label=status,
                dict_value=str(progress),
                dict_sort=sort_order,
                status=1,
                remark='系统自动初始化',
                create_by='system',
                create_time=datetime.now()
            )
            db.add(new_data)
        sort_order += 1
        
    await db.commit()
    
    return {'code': 200, 'msg': 'Constants initialized successfully'}

@router.get("/data/type/{dict_type}", response_model=List[DictDataResponse])
async def get_dict_data_by_type(
    dict_type: str,
    db: AsyncSession = Depends(get_db)
):
    """
    根据字典类型获取字典数据
    """
    # First get dict_id from dict_type
    query_type = select(SysDictType).where(SysDictType.dict_type == dict_type)
    result_type = await db.execute(query_type)
    dict_type_obj = result_type.scalar_one_or_none()
    
    if not dict_type_obj:
        return []

    # Then get data
    query = select(SysDictData).where(
        SysDictData.dict_id == dict_type_obj.dict_id,
        SysDictData.status == 1
    ).order_by(SysDictData.dict_sort)
    
    result = await db.execute(query)
    data = result.scalars().all()
    
    # Map back dict_type string for response
    response_data = []
    for item in data:
        item_dict = item.__dict__
        item_dict['dict_type'] = dict_type
        response_data.append(DictDataResponse(**item_dict))
        
    return response_data

@router.post("/data", response_model=DictDataResponse)
async def create_dict_data(
    data_in: DictDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    新增字典数据
    """
    # Check if dict_type exists
    query_type = select(SysDictType).where(SysDictType.dict_type == data_in.dict_type)
    result_type = await db.execute(query_type)
    dict_type_obj = result_type.scalar_one_or_none()
    
    if not dict_type_obj:
        # Auto create dict type if not exists? Or strict? 
        # Let's auto create for now for convenience if it's a new project type
        if data_in.dict_type == 'sys_project_type':
             new_type = SysDictType(
                 dict_name='项目类型',
                 dict_type='sys_project_type',
                 status=1,
                 remark='自动创建的项目类型字典',
                 create_by=current_user.username,
                 create_time=datetime.now()
             )
             db.add(new_type)
             await db.flush()
             dict_type_obj = new_type
        else:
             raise HTTPException(status_code=404, detail="字典类型不存在")

    new_data = SysDictData(
        dict_id=dict_type_obj.dict_id,
        dict_label=data_in.dict_label,
        dict_value=data_in.dict_value,
        dict_sort=data_in.dict_sort,
        status=data_in.status,
        remark=data_in.remark,
        create_by=current_user.username,
        create_time=datetime.now(),
        update_by=current_user.username,
        update_time=datetime.now()
    )
    
    db.add(new_data)
    await db.commit()
    await db.refresh(new_data)
    
    # Prepare response
    response_dict = new_data.__dict__
    response_dict['dict_type'] = data_in.dict_type
    return DictDataResponse(**response_dict)
