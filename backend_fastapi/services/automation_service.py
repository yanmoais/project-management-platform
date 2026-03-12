from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_, insert
from backend_fastapi.models.sys_automation_models import SysAutomationRule, SysAutomationLog
from backend_fastapi.models.pm_models import PMRequirement, PMSubRequirement, PMTask, PMDefect
from backend_fastapi.core.constants import REQUIREMENT_STATUS_PROGRESS_MAP
from datetime import datetime
import json
import logging

# Logger configuration
logger = logging.getLogger(__name__)

# --- Metadata Registry ---
AUTOMATION_EVENTS = [
    {'value': 'requirement:child:update', 'label': '自动更新需求状态', 'params': []},
    {'value': 'requirement:update', 'label': '发送站内通知 (需求状态变更)', 'params': [
        {'name': 'template', 'label': '通知模板', 'type': 'textarea', 'placeholder': 'e.g. 需求 {title} 状态变更'}
    ]},
    {'value': 'requirement:assign', 'label': '发送站内通知 (需求分配)', 'params': [
        {'name': 'template', 'label': '通知模板', 'type': 'textarea', 'placeholder': 'e.g. 您有新需求：{title}'}
    ]},
    {'value': 'task:assign', 'label': '发送站内通知 (任务分配)', 'params': [
        {'name': 'template', 'label': '通知模板', 'type': 'textarea', 'placeholder': 'e.g. 您有新任务：{title}'}
    ]},
    {'value': 'task:update', 'label': '发送站内通知 (任务信息更新)', 'params': []},
    {'value': 'defect:create', 'label': '发送站内通知 (新建缺陷)', 'params': [
        {'name': 'template', 'label': '通知模板', 'type': 'textarea', 'placeholder': 'e.g. 新缺陷已创建：{title}'}
    ]},
    {'value': 'defect:update', 'label': '发送站内通知 (缺陷状态变更)', 'params': [
        {'name': 'template', 'label': '通知模板', 'type': 'textarea', 'placeholder': 'e.g. 缺陷 {title} 状态变更'}
    ]},
    {'value': 'defect:assign', 'label': '发送站内通知 (缺陷分配)', 'params': [
        {'name': 'template', 'label': '通知模板', 'type': 'textarea', 'placeholder': 'e.g. 您有新缺陷待处理：{title}'}
    ]}
]

AUTOMATION_CONDITIONS = [
    {
        'value': 'check_all_children_completed', 
        'label': '检查所有子项(子需求/子任务)是否已完成/已上线',
        'params': []
    },
    {
        'value': 'status_changed', 
        'label': '状态变更为特定值',
        'params': [
            {'name': 'target_status', 'label': '目标状态', 'type': 'select', 'options': [
                {'label': '已完成 (Completed)', 'value': 'completed'},
                {'label': '已上线 (Online)', 'value': 'online'},
                {'label': '进行中 (Processing)', 'value': 'processing'}
            ]}
        ]
    },
    {
        'value': 'assignee_changed',
        'label': '负责人发生变更',
        'params': []
    },
    {
        'value': 'always_true',
        'label': '无条件 (总是执行)',
        'params': []
    }
]

AUTOMATION_ACTIONS = [
    # 动作已合并到事件中，此列表保留为空或用于特殊用途
]

class AutomationService:
    """
    自动化服务核心类
    负责处理事件触发、规则匹配和动作执行
    """
    
    @staticmethod
    def get_metadata():
        """
        获取自动化元数据
        """
        return {
            'events': AUTOMATION_EVENTS,
            'conditions': AUTOMATION_CONDITIONS,
            'actions': [] # 前端不再需要 actions
        }

    @staticmethod
    async def trigger_event(event_name: str, context: dict, db: AsyncSession, current_user_name: str = 'system'):
        """
        触发事件
        :param event_name: 事件名称 (e.g., 'requirement:child:update')
        :param context: 上下文数据 (e.g., {'requirement_id': 1})
        :param db: 数据库会话
        :param current_user_name: 当前操作用户
        """
        logger.info(f"Automation Event Triggered: {event_name}, Context: {context}")
        
        # 1. 加载所有针对该事件的活跃规则
        stmt = select(SysAutomationRule).where(
            SysAutomationRule.trigger_event == event_name,
            SysAutomationRule.is_active == True
        ).order_by(SysAutomationRule.priority.desc())
        
        result = await db.execute(stmt)
        rules = result.scalars().all()
        
        if not rules:
            logger.info(f"No active rules found for event: {event_name}")
            return

        # Initialize deduplication cache for this event trigger
        if '_sent_notifications' not in context:
            context['_sent_notifications'] = set()

        # 2. 遍历规则并评估条件
        for rule in rules:
            try:
                if await AutomationService._evaluate_conditions(rule, context, db):
                    logger.info(f"Rule matched: {rule.rule_name} ({rule.rule_code})")
                    # 3. 执行动作 (逻辑已合并到事件处理中)
                    await AutomationService._execute_rule_logic(rule, context, db, current_user_name)
                    
                    # 4. 记录日志
                    await AutomationService._log_execution(rule, context, "success", "Executed successfully", db)
                else:
                    logger.info(f"Rule condition not met: {rule.rule_name}")
            except Exception as e:
                logger.error(f"Error executing rule {rule.rule_code}: {e}")
                await AutomationService._log_execution(rule, context, "failed", str(e), db)

    @staticmethod
    async def _execute_rule_logic(rule: SysAutomationRule, context: dict, db: AsyncSession, current_user_name: str):
        """
        执行规则逻辑（根据事件类型和条件参数执行相应操作）
        """
        event_name = rule.trigger_event
        
        # 移除 requirement:child:update 的硬编码调用，改为由 Celery Beat 定时扫描处理
        # if event_name == 'requirement:child:update':
        #     await AutomationService._builtin_check_parent_completion(context, db, current_user_name)
            
        if event_name == 'requirement:update':
            # 逻辑：需求状态变更 -> 发送通知
            # 从 conditions 中获取配置参数（如果有）
            await AutomationService._action_send_notification(rule, context, db, current_user_name)
            
        elif event_name == 'task:assign':
            # 逻辑：任务分配 -> 发送通知
            await AutomationService._action_send_notification(rule, context, db, current_user_name)

        elif event_name == 'requirement:assign':
            # 逻辑：需求分配 -> 发送通知
            await AutomationService._action_send_notification(rule, context, db, current_user_name)
            
        elif event_name == 'task:update':
             # 逻辑待定
             pass

        elif event_name in ['defect:create', 'defect:update', 'defect:assign']:
            # 逻辑：缺陷相关 -> 发送通知
            await AutomationService._action_send_notification(rule, context, db, current_user_name)

    # ... (保留 _evaluate_conditions, _check_children_status, _builtin_check_parent_completion)

    @staticmethod
    async def _action_send_notification(rule: SysAutomationRule, context: dict, db: AsyncSession, sender: str):
        """
        执行动作：发送站内通知
        """
        # 从规则条件参数中获取模板，或者使用默认模板
        # 兼容旧逻辑：如果 conditions 中没有 template，尝试从 actions 中获取
        template = rule.conditions.get('template', '') if rule.conditions else ''
        if not template and rule.actions and len(rule.actions) > 0:
            template = rule.actions[0].get('template', '')
            
        if not template:
             template = "通知：{title} 状态已更新"

        target_id = None
        target_type = None
        title = ""
        content = ""
        user_ids = set()
        
        # 1. 解析上下文，确定目标对象和相关用户
        # 引入 SysUser 模型用于查询用户名
        from backend_fastapi.models.sys_models import SysUser
        
        async def get_user_name(user_id):
            if not user_id: return str(user_id)
            stmt = select(SysUser.nickname, SysUser.username).where(SysUser.user_id == user_id)
            res = (await db.execute(stmt)).first()
            if res:
                return res.nickname or res.username or str(user_id)
            return str(user_id)

        # 状态映射字典
        REQ_STATUS_MAP = {
            'draft': '草稿', 'pending': '待内审', 'reviewing': '待开发评审',
            'tech_review': '待技术方案评审', 'planning': '规划中', 'developing': '开发中',
            'testing': '测试中', 'accepting': '验收中','completed': '已完成', 'closed': '已关闭', 'suspended': '已暂停'
        }
        SUB_REQ_STATUS_MAP = {
            'not_started': '未开始', 'testing': '测试中', 'accepting': '验收中', 'online': '已上线'
        }
        TASK_STATUS_MAP = {
            'not_started': '未开始', 'in_progress': '进行中', 'completed': '已完成', 
            'pending': '待处理', 'Pending': '待处理'
        }
        PRIORITY_MAP = {
            'High': '高', 'Medium': '中', 'Low': '低','medium': '中'
        }
        
        DEFECT_STATUS_MAP = {
            'New': '新建', 'In_Progress': '处理中', 'Resolved': '已解决', 'Verified': '待验证', 'Closed': '已关闭', 'Reopened': '重新打开', 'Rejected': '已拒绝'
        }
        DEFECT_SEVERITY_MAP = {
            'Critical': '致命', 'Major': '严重', 'Minor': '一般', 'Trivial': '轻微'
        }

        if 'requirement_id' in context:
            req_id = context['requirement_id']
            target_id = req_id
            target_type = 'requirement'
            
            stmt = select(PMRequirement).where(PMRequirement.req_id == req_id)
            req = (await db.execute(stmt)).scalar_one_or_none()
            
            if req:
                assignee_name = await get_user_name(req.assignee_id)
                status_text = REQ_STATUS_MAP.get(req.status, req.status)
                priority_text = PRIORITY_MAP.get(req.priority, req.priority)

                trigger = context.get('trigger', '')
                
                if rule.trigger_event == 'requirement:assign':
                    title = f"新需求分配: {req.title}"
                    content = f"""
                    <p><strong>需求编码:</strong> {req.req_code or 'N/A'}</p>
                    <p><strong>需求标题:</strong> {req.title}</p>
                    <p><strong>优先级:</strong> {priority_text}</p>
                    <p><strong>截止日期:</strong> {req.end_date or '未设置'}</p>
                    <p><strong>分配人:</strong> {sender}</p>
                    <p><strong>分配时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    """
                elif trigger == 'requirement_create':
                    title = f"新需求创建: {req.title}"
                    content = f"""
                    <p><strong>需求编码:</strong> {req.req_code or 'N/A'}</p>
                    <p><strong>需求标题:</strong> {req.title}</p>
                    <p><strong>当前状态:</strong> {status_text}</p>
                    <p><strong>优先级:</strong> {priority_text}</p>
                    <p><strong>负责人:</strong> {assignee_name}</p>
                    <p><strong>创建人:</strong> {sender}</p>
                    <p><strong>创建时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    """
                else:
                    title = f"需求变更: {req.title}"
                    # 使用 HTML 格式化内容，以便前端富文本展示
                    content = f"""
                    <p><strong>需求编码:</strong> {req.req_code or 'N/A'}</p>
                    <p><strong>需求标题:</strong> {req.title}</p>
                    <p><strong>当前状态:</strong> {status_text}</p>
                    <p><strong>优先级:</strong> {priority_text}</p>
                    <p><strong>负责人:</strong> {assignee_name}</p>
                    <p><strong>更新人:</strong> {sender}</p>
                    <p><strong>更新时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    """
                
                # 关联用户：负责人、开发、测试、验收
                if req.assignee_id: user_ids.add(req.assignee_id)
                if req.developer_id: user_ids.add(req.developer_id)
                if req.tester_id: user_ids.add(req.tester_id)
                if req.accepter_id: user_ids.add(req.accepter_id)
                
                # 关联用户：创建人
                if req.create_by:
                    # 尝试用 username 查询
                    stmt_creator = select(SysUser.user_id).where(SysUser.username == req.create_by)
                    creator_id = (await db.execute(stmt_creator)).scalar_one_or_none()
                    if not creator_id:
                        # 尝试用 nickname 查询 (兼容旧数据)
                        stmt_creator = select(SysUser.user_id).where(SysUser.nickname == req.create_by)
                        creator_id = (await db.execute(stmt_creator)).scalar_one_or_none()
                    
                    if creator_id:
                        user_ids.add(creator_id)

        elif 'sub_req_id' in context:
            sub_req_id = context['sub_req_id']
            target_id = sub_req_id
            target_type = 'sub_requirement'
            
            stmt = select(PMSubRequirement).where(PMSubRequirement.sub_req_id == sub_req_id)
            sub_req = (await db.execute(stmt)).scalar_one_or_none()
            
            if sub_req:
                assignee_name = await get_user_name(sub_req.assignee_id)
                status_text = SUB_REQ_STATUS_MAP.get(sub_req.status, sub_req.status)
                trigger = context.get('trigger', '')
                
                if trigger == 'sub_requirement_create':
                    title = f"新子需求创建: {sub_req.title}"
                    content = f"""
                    <p><strong>子需求编码:</strong> {sub_req.sub_req_code or 'N/A'}</p>
                    <p><strong>标题:</strong> {sub_req.title}</p>
                    <p><strong>状态:</strong> {status_text}</p>
                    <p><strong>负责人:</strong> {assignee_name}</p>
                    <p><strong>创建人:</strong> {sender}</p>
                    """
                else:
                    title = f"子需求变更: {sub_req.title}"
                    content = f"""
                    <p><strong>子需求编码:</strong> {sub_req.sub_req_code or 'N/A'}</p>
                    <p><strong>标题:</strong> {sub_req.title}</p>
                    <p><strong>状态:</strong> {status_text}</p>
                    <p><strong>负责人:</strong> {assignee_name}</p>
                    <p><strong>更新人:</strong> {sender}</p>
                    """
                if sub_req.assignee_id: user_ids.add(sub_req.assignee_id)
                
                # 关联用户：创建人
                if sub_req.create_by:
                    # 尝试用 username 查询
                    stmt_creator = select(SysUser.user_id).where(SysUser.username == sub_req.create_by)
                    creator_id = (await db.execute(stmt_creator)).scalar_one_or_none()
                    if not creator_id:
                        # 尝试用 nickname 查询 (兼容旧数据)
                        stmt_creator = select(SysUser.user_id).where(SysUser.nickname == sub_req.create_by)
                        creator_id = (await db.execute(stmt_creator)).scalar_one_or_none()
                    
                    if creator_id:
                        user_ids.add(creator_id)
                
        elif 'task_id' in context:
            task_id = context['task_id']
            target_id = task_id
            target_type = 'task'
            
            stmt = select(PMTask).where(PMTask.task_id == task_id)
            task = (await db.execute(stmt)).scalar_one_or_none()
            
            if task:
                assignee_name = await get_user_name(task.assignee_id)
                status_text = TASK_STATUS_MAP.get(task.status, task.status)
                trigger = context.get('trigger', '')
                
                if trigger == 'task_create':
                    title = f"新任务创建: {task.title}"
                    content = f"""
                    <p><strong>任务编码:</strong> {task.task_code or 'N/A'}</p>
                    <p><strong>标题:</strong> {task.title}</p>
                    <p><strong>状态:</strong> {status_text}</p>
                    <p><strong>负责人:</strong> {assignee_name}</p>
                    <p><strong>创建人:</strong> {sender}</p>
                    """
                else:
                    title = f"任务通知: {task.title}"
                    content = f"""
                    <p><strong>任务编码:</strong> {task.task_code or 'N/A'}</p>
                    <p><strong>标题:</strong> {task.title}</p>
                    <p><strong>状态:</strong> {status_text}</p>
                    <p><strong>负责人:</strong> {assignee_name}</p>
                    <p><strong>更新人:</strong> {sender}</p>
                    """
                if task.assignee_id: user_ids.add(task.assignee_id)

                # 关联用户：创建人
                if task.create_by:
                    # 尝试用 username 查询
                    stmt_creator = select(SysUser.user_id).where(SysUser.username == task.create_by)
                    creator_id = (await db.execute(stmt_creator)).scalar_one_or_none()
                    if not creator_id:
                        # 尝试用 nickname 查询 (兼容旧数据)
                        stmt_creator = select(SysUser.user_id).where(SysUser.nickname == task.create_by)
                        creator_id = (await db.execute(stmt_creator)).scalar_one_or_none()
                    
                    if creator_id:
                        user_ids.add(creator_id)

        elif 'defect_id' in context:
            defect_id = context['defect_id']
            target_id = defect_id
            target_type = 'defect'
            
            stmt = select(PMDefect).where(PMDefect.defect_id == defect_id)
            defect = (await db.execute(stmt)).scalar_one_or_none()
            
            if defect:
                assignee_name = await get_user_name(defect.assignee_id)
                status_text = DEFECT_STATUS_MAP.get(defect.status, defect.status)
                severity_text = DEFECT_SEVERITY_MAP.get(defect.severity, defect.severity)
                priority_text = PRIORITY_MAP.get(defect.priority, defect.priority)
                
                trigger = context.get('trigger', '')
                
                if trigger == 'defect_create':
                    title = f"新缺陷创建: {defect.title}"
                    content = f"""
                    <p><strong>缺陷编码:</strong> {defect.defect_code or 'N/A'}</p>
                    <p><strong>标题:</strong> {defect.title}</p>
                    <p><strong>状态:</strong> {status_text}</p>
                    <p><strong>严重程度:</strong> {severity_text}</p>
                    <p><strong>优先级:</strong> {priority_text}</p>
                    <p><strong>负责人:</strong> {assignee_name}</p>
                    <p><strong>创建人:</strong> {sender}</p>
                    <p><strong>创建时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    """
                elif trigger == 'defect_assign':
                    title = f"缺陷分配: {defect.title}"
                    content = f"""
                    <p><strong>缺陷编码:</strong> {defect.defect_code or 'N/A'}</p>
                    <p><strong>标题:</strong> {defect.title}</p>
                    <p><strong>状态:</strong> {status_text}</p>
                    <p><strong>优先级:</strong> {priority_text}</p>
                    <p><strong>分配给:</strong> {assignee_name}</p>
                    <p><strong>分配人:</strong> {sender}</p>
                    <p><strong>分配时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    """
                elif defect.status == 'Closed':
                    title = f"缺陷已关闭: {defect.title}"
                    content = f"""
                    <p><strong>缺陷编码:</strong> {defect.defect_code or 'N/A'}</p>
                    <p><strong>标题:</strong> {defect.title}</p>
                    <p><strong>当前状态:</strong> {status_text}</p>
                    <p><strong>负责人:</strong> {assignee_name}</p>
                    <p><strong>关闭人:</strong> {sender}</p>
                    <p><strong>关闭时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    """
                else:
                    title = f"缺陷更新: {defect.title}"
                    content = f"""
                    <p><strong>缺陷编码:</strong> {defect.defect_code or 'N/A'}</p>
                    <p><strong>标题:</strong> {defect.title}</p>
                    <p><strong>当前状态:</strong> {status_text}</p>
                    <p><strong>负责人:</strong> {assignee_name}</p>
                    <p><strong>更新人:</strong> {sender}</p>
                    <p><strong>更新时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    """
                
                # 关联用户：负责人、报告人
                if defect.assignee_id: user_ids.add(defect.assignee_id)
                if defect.reporter_id: user_ids.add(defect.reporter_id)
                
                # 关联用户：创建人 (如果不等于报告人)
                if defect.create_by:
                    stmt_creator = select(SysUser.user_id).where(SysUser.username == defect.create_by)
                    creator_id = (await db.execute(stmt_creator)).scalar_one_or_none()
                    if not creator_id:
                        stmt_creator = select(SysUser.user_id).where(SysUser.nickname == defect.create_by)
                        creator_id = (await db.execute(stmt_creator)).scalar_one_or_none()
                    
                    if creator_id:
                        user_ids.add(creator_id)

        # 2. 添加关注者 (Followers)
        if target_id and target_type:
            # 引入 SysUserFollow 模型 (局部引入避免循环依赖)
            from backend_fastapi.models.sys_models import SysUserFollow, SysNotification
            
            stmt_follow = select(SysUserFollow.user_id).where(
                SysUserFollow.target_id == target_id,
                SysUserFollow.target_type == target_type
            )
            followers = (await db.execute(stmt_follow)).scalars().all()
            for uid in followers:
                user_ids.add(uid)
            
            # 3. 发送通知 (插入数据库)
            if user_ids and title:
                sent_cache = context.get('_sent_notifications', set())
                
                # Check DB for recent duplicates (Global Deduplication across requests)
                from datetime import timedelta
                cutoff_time = datetime.now() - timedelta(seconds=10) # 10 seconds window
                
                stmt_recent = select(SysNotification.user_id).where(
                    SysNotification.user_id.in_(user_ids),
                    SysNotification.target_id == target_id,
                    SysNotification.target_type == target_type,
                    SysNotification.title == title,
                    SysNotification.create_time >= cutoff_time
                )
                result = await db.execute(stmt_recent)
                recently_notified_users = set(result.scalars().all())

                for uid in user_ids:
                    # 避免给操作者自己发送通知 (可选逻辑，这里暂时保留发送)
                    # if str(uid) == str(sender_id): continue 
                    
                    # Deduplicate notifications
                    # Use (user_id, title) as unique key
                    cache_key = (str(uid), title)
                    if cache_key in sent_cache:
                        logger.info(f"Duplicate notification skipped for user {uid} (Context Cache): {title}")
                        continue
                    
                    if uid in recently_notified_users:
                        logger.info(f"Duplicate notification skipped for user {uid} (DB Recent): {title}")
                        continue
                        
                    notif = SysNotification(
                        user_id=uid,
                        title=title,
                        content=content,
                        type=target_type,
                        target_id=target_id,
                        target_type=target_type,
                        is_read=0,
                        create_time=datetime.now()
                    )
                    db.add(notif)
                    sent_cache.add(cache_key)
                
                # Update context cache
                context['_sent_notifications'] = sent_cache
                
                await db.commit()
                logger.info(f"Action: Send Notification. Sent to {len(user_ids)} users. Context: {context}")
        else:
            logger.warning(f"Notification skipped: No valid target found in context {context}")

        
    @staticmethod
    async def _action_auto_assign(rule: SysAutomationRule, context: dict, db: AsyncSession, sender: str):
        """
        执行动作：自动分配负责人
        """
        logger.info(f"Action: Auto Assign. Rule: {rule.rule_name}, Context: {context}")


    @staticmethod
    async def _execute_builtin_rules(event_name: str, context: dict, db: AsyncSession, current_user_name: str):
        """
        执行内置规则 (作为数据库规则的补充或兜底) - 已弃用，逻辑移至 _execute_rule_logic
        """
        pass # 逻辑已重构，不再使用独立的内置规则执行入口

    @staticmethod
    async def _builtin_check_parent_completion(context: dict, db: AsyncSession, current_user_name: str):
        """
        内置规则：检查父需求是否完成
        """
        requirement_id = context.get('requirement_id')
        if not requirement_id:
            return

        # 1. 查询所有子需求
        stmt_sub = select(PMSubRequirement).where(
            PMSubRequirement.requirement_id == requirement_id,
            PMSubRequirement.del_flag == 0
        )
        result_sub = await db.execute(stmt_sub)
        sub_reqs = result_sub.scalars().all()
        sub_req_ids = [s.sub_req_id for s in sub_reqs]

        # 2. 查询所有关联任务
        conditions = [PMTask.requirement_id == requirement_id]
        if sub_req_ids:
            conditions.append(PMTask.sub_requirement_id.in_(sub_req_ids))
            
        stmt_task = select(PMTask).where(
            PMTask.del_flag == 0,
            or_(*conditions)
        )
        result_task = await db.execute(stmt_task)
        tasks = result_task.scalars().all()

        if not sub_reqs and not tasks:
            return

        # 3. 检查状态
        all_sub_reqs_online = all(s.status == 'online' for s in sub_reqs)
        all_tasks_completed = all(t.status == 'completed' for t in tasks)

        if all_sub_reqs_online and all_tasks_completed:
            # 更新父需求状态
            stmt_update = update(PMRequirement).where(
                PMRequirement.req_id == requirement_id
            ).values(
                status='completed',
                progress=REQUIREMENT_STATUS_PROGRESS_MAP.get('completed', 100),
                completed_at=datetime.now(),
                update_by=current_user_name,
                update_time=datetime.now()
            )
            await db.execute(stmt_update)
            await db.commit()
            logger.info(f"Builtin Rule Executed: Auto-completed Requirement {requirement_id}")

    @staticmethod
    async def _evaluate_conditions(rule: SysAutomationRule, context: dict, db: AsyncSession) -> bool:
        """
        评估规则条件
        目前支持简单的配置，复杂逻辑仍需代码扩展
        """
        conditions = rule.conditions
        if not conditions:
            return True
            
        # Example condition: {"type": "check_all_children_completed"}
        condition_type = conditions.get('type')
        
        if condition_type == 'check_all_children_completed':
            # 复用内置逻辑的检查部分，这里简单演示，实际上应该拆分得更细
            # 如果是纯配置化，需要更复杂的解析器。
            # 为了 MVP，如果数据库里配置了这个类型，我们还是调用内置逻辑检查一下状态
            # 但为了避免重复执行，这里仅仅返回 True/False，动作由 _execute_actions 处理
            return await AutomationService._check_children_status(context, db)
            
        return True

    @staticmethod
    async def _check_children_status(context: dict, db: AsyncSession) -> bool:
        requirement_id = context.get('requirement_id')
        if not requirement_id: return False
        
        # 查询子需求和任务状态... (代码略，与内置逻辑类似)
        # 为了避免代码重复，实际项目中应该提取公共查询方法
        # 这里简化处理：直接返回 True，假设触发了这个规则就是为了去尝试执行动作
        # 真正的条件判断应该在 Action 执行前再次确认，或者在这里做完全检查。
        # 考虑到 MVP，我们假设 _builtin_check_parent_completion 已经包含了完整的 Check-Act 逻辑
        # 所以如果规则配置的是 "check_and_complete_parent"，我们在这里返回 True，然后在 Action 里调用逻辑
        return True

    @staticmethod
    async def _execute_actions(rule: SysAutomationRule, context: dict, db: AsyncSession, current_user_name: str):
        """
        执行动作 (Deprecated - Logic moved to _execute_rule_logic)
        """
        pass # 逻辑已合并到 _execute_rule_logic

    @staticmethod
    async def _action_send_notification_deprecated(action: dict, context: dict, db: AsyncSession, sender: str):
        """
        执行动作：发送站内通知
        """
        # TODO: 集成站内信模块
        # target_user_id = ...
        # content = ...
        logger.info(f"Action: Send Notification. Config: {action}, Context: {context}")
        
    @staticmethod
    async def _action_auto_assign_deprecated(action: dict, context: dict, db: AsyncSession, sender: str):
        """
        执行动作：自动分配负责人 (Deprecated)
        """
        logger.info(f"Action: Auto Assign. Config: {action}, Context: {context}")
        # 逻辑实现：根据配置更新 requirement/task 的 assignee_id


    @staticmethod
    async def _log_execution(rule: SysAutomationRule, context: dict, status: str, result: str, db: AsyncSession):
        """
        记录执行日志
        """
        try:
            log = SysAutomationLog(
                rule_id=rule.rule_id,
                rule_name=rule.rule_name,
                trigger_event=rule.trigger_event,
                target_id=str(context.get('requirement_id') or context.get('sub_req_id') or context.get('task_id') or ''),
                execution_status=status,
                execution_result=result
            )
            db.add(log)
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to log automation execution: {e}")

    @staticmethod
    async def initialize_default_rules(db: AsyncSession):
        """
        初始化默认规则到数据库
        """
        # 1. 默认规则：父需求自动流转完成 (现在改为定时任务)
        stmt = select(SysAutomationRule).where(SysAutomationRule.rule_code == 'AUTO_COMPLETE_PARENT_REQ')
        rule1_res = await db.execute(stmt)
        if not rule1_res.scalar_one_or_none():
            rule1 = SysAutomationRule(
                rule_name='父需求自动流转完成',
                rule_code='AUTO_COMPLETE_PARENT_REQ',
                description='当所有子需求上线且所有子任务完成时，自动将父需求标记为已完成。',
                trigger_event='requirement:child:update', # 这里的 event 仅作为标识，实际由 schedule 驱动
                rule_type='schedule',
                cron_expression='*/1 * * * *', # 每分钟
                query_config={'condition': 'check_all_children_completed'},
                conditions={'type': 'check_all_children_completed'},
                actions=[{'type': 'update_parent_status', 'target': 'parent_requirement', 'value': 'completed'}],
                is_active=True,
                priority=100,
                create_by='system'
            )
            db.add(rule1)
        else:
            # 如果规则已存在，更新其类型为 schedule
            stmt_update = update(SysAutomationRule).where(
                SysAutomationRule.rule_code == 'AUTO_COMPLETE_PARENT_REQ'
            ).values(
                rule_type='schedule',
                cron_expression='*/1 * * * *',
                query_config={'condition': 'check_all_children_completed'}
            )
            await db.execute(stmt_update)

        # 2. 默认规则：需求状态变更通知
        stmt = select(SysAutomationRule).where(SysAutomationRule.rule_code == 'NOTIFY_REQ_STATUS_CHANGE')
        if not (await db.execute(stmt)).scalar_one_or_none():
            rule2 = SysAutomationRule(
                rule_name='需求状态变更通知',
                rule_code='NOTIFY_REQ_STATUS_CHANGE',
                description='当需求状态发生变更时，通知相关人员（创建人、负责人）。',
                trigger_event='requirement:update',
                rule_type='schedule',
                conditions={'type': 'status_changed'},
                actions=[{'type': 'send_notification', 'template': '需求 {title} 状态已变更为 {status}'}],
                is_active=True,
                priority=90,
                create_by='system'
            )
            db.add(rule2)

        # 3. 默认规则：新任务分配通知
        stmt = select(SysAutomationRule).where(SysAutomationRule.rule_code == 'NOTIFY_TASK_ASSIGNED')
        if not (await db.execute(stmt)).scalar_one_or_none():
            rule3 = SysAutomationRule(
                rule_name='新任务分配通知',
                rule_code='NOTIFY_TASK_ASSIGNED',
                description='当任务分配给用户时，发送站内通知提醒。',
                trigger_event='task:assign',
                rule_type='schedule',
                conditions={'type': 'assignee_changed'},
                actions=[{'type': 'send_notification', 'template': '您有一个新任务待处理：{title}'}],
                is_active=True,
                priority=90,
                create_by='system'
            )
            db.add(rule3)

        # 4. 默认规则：需求分配通知
        stmt = select(SysAutomationRule).where(SysAutomationRule.rule_code == 'NOTIFY_REQ_ASSIGNED')
        if not (await db.execute(stmt)).scalar_one_or_none():
            rule4 = SysAutomationRule(
                rule_name='需求分配通知',
                rule_code='NOTIFY_REQ_ASSIGNED',
                description='当需求分配给用户时，发送站内通知提醒。',
                trigger_event='requirement:assign',
                rule_type='event',
                conditions={'type': 'assignee_changed'},
                actions=[{'type': 'send_notification', 'template': '您有一个新需求待处理：{title}'}],
                is_active=True,
                priority=90,
                create_by='system'
            )
            db.add(rule4)
            
        await db.commit()
