from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Union, List, Dict, Any, Set
from backend_fastapi.models.sys_models import SysUser

async def enrich_usernames_with_nicknames(db: AsyncSession, data: Union[Dict[str, Any], List[Dict[str, Any]]]):
    """
    递归遍历数据结构，将 create_by 和 update_by 的 username 替换为 nickname
    支持单个字典或字典列表，支持嵌套 children
    """
    if not data:
        return

    items = data if isinstance(data, list) else [data]
    usernames: Set[str] = set()

    # 1. 收集所有 username
    def collect_usernames(item: Dict[str, Any]):
        if not isinstance(item, dict):
            return
            
        create_by = item.get('create_by')
        if create_by and isinstance(create_by, str):
            usernames.add(create_by)
            
        update_by = item.get('update_by')
        if update_by and isinstance(update_by, str):
            usernames.add(update_by)
            
        # 递归处理 children
        children = item.get('children')
        if children and isinstance(children, list):
            for child in children:
                collect_usernames(child)
    
    for item in items:
        collect_usernames(item)
        
    if not usernames:
        return

    # 2. 查询数据库获取映射
    user_map = {}
    stmt = select(SysUser.username, SysUser.nickname).where(SysUser.username.in_(usernames))
    result = await db.execute(stmt)
    for row in result:
        # row is (username, nickname)
        user_map[row.username] = row.nickname or row.username

    # 3. 替换值
    def replace_usernames(item: Dict[str, Any]):
        if not isinstance(item, dict):
            return

        create_by = item.get('create_by')
        if create_by and create_by in user_map:
            item['create_by'] = user_map[create_by]
            
        update_by = item.get('update_by')
        if update_by and update_by in user_map:
            item['update_by'] = user_map[update_by]
            
        # 递归处理 children
        children = item.get('children')
        if children and isinstance(children, list):
            for child in children:
                replace_usernames(child)

    for item in items:
        replace_usernames(item)
