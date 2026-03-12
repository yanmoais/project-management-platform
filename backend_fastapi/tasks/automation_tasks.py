from backend_fastapi.core.celery_app import celery_app
from backend_fastapi.db.session import AutomationSessionLocalSync, SessionLocal
from backend_fastapi.models.automation_models import AutomationExecution, AutomationProject, ProjectFile
from backend_fastapi.models.sys_automation_models import SysAutomationRule, SysAutomationLog
from backend_fastapi.models.pm_models import PMRequirement, PMSubRequirement, PMTask
from backend_fastapi.models.sys_models import SysNotification, SysUser, SysUserFollow
from backend_fastapi.utils.LogManeger import log_info, set_current_execution_id, clear_current_execution_id
from backend_fastapi.core.constants import REQUIREMENT_STATUS_PROGRESS_MAP
from datetime import datetime
from sqlalchemy import text, update, or_, select
import os
import sys
import subprocess
import json

@celery_app.task
def scan_automation_rules():
    """
    定时扫描规则任务
    扫描 rule_type='schedule' 的规则并执行
    """
    db = SessionLocal() # 使用主数据库同步 Session
    try:
        log_info("Start scanning automation rules...")
        
        # 1. 获取所有启用的定时规则
        # 注意：这里简化处理，不解析 cron 表达式，假设任务每分钟执行一次，
        # 并检查所有 active 的 schedule 规则。
        # 实际生产中可能需要根据 cron 表达式判断当前时间是否应该执行，
        # 或者由外部调度器（如 Beat）根据 Cron 配置生成不同的任务。
        # 为了 MVP，我们假设所有 schedule 规则都是"每分钟检查一次"。
        
        rules = db.query(SysAutomationRule).filter(
            SysAutomationRule.is_active == True,
            SysAutomationRule.rule_type == 'schedule'
        ).all()
        for rule in rules:
            log_info(f"Processing rule: {rule.rule_name} ({rule.rule_code})")
            try:
                # 2. 根据 query_config 扫描数据
                # query_config 示例: {"target": "parent_requirement", "condition": "all_children_completed"}
                # 目前主要支持 "父需求自动流转" 这一类规则
                
                config = rule.query_config or {}
                condition_type = config.get('condition') or (rule.conditions.get('type') if rule.conditions else None)
                
                if condition_type == 'check_all_children_completed':
                    # 执行检查逻辑
                    _check_and_complete_parents(db, rule)
                    
            except Exception as e:
                log_info(f"Error executing rule {rule.rule_code}: {e}")
                
    except Exception as e:
        log_info(f"Error in scan_automation_rules: {e}")
    finally:
        db.close()

def _check_and_complete_parents(db, rule):
    """
    扫描所有未完成的父需求，检查其子项是否全部完成
    """
    # 1. 查找所有未完成且未关闭的父需求
    parents = db.query(PMRequirement).filter(
        PMRequirement.status.notin_(['completed', 'closed', 'cancelled']),
        PMRequirement.del_flag == 0
    ).all()
    
    log_info(f"Checking {len(parents)} active requirements for auto-completion...")
    
    for parent in parents:
        # 检查子需求
        sub_reqs = db.query(PMSubRequirement).filter(
            PMSubRequirement.requirement_id == parent.req_id,
            PMSubRequirement.del_flag == 0
        ).all()
        
        # 检查关联任务
        # 任务可能直接关联父需求，也可能关联子需求
        # 这里为了简化，我们只检查直接关联的任务 + 子需求关联的任务
        sub_req_ids = [s.sub_req_id for s in sub_reqs]
        
        task_query = db.query(PMTask).filter(PMTask.del_flag == 0)
        conditions = [PMTask.requirement_id == parent.req_id]
        if sub_req_ids:
            conditions.append(PMTask.sub_requirement_id.in_(sub_req_ids))
        
        tasks = task_query.filter(or_(*conditions)).all()
        
        if not sub_reqs and not tasks:
            continue
            
        # 检查状态
        # 子需求必须是 'online' (已上线) 
        # 子任务必须是 'completed' (已完成)
        all_sub_reqs_ok = all(s.status == 'online' for s in sub_reqs)
        all_tasks_ok = all(t.status == 'completed' for t in tasks)
        
        # Debug log for specific requirement if close to completion
        # if sub_reqs or tasks:
        #    log_info(f"Req {parent.req_id} status check: Sub({len(sub_reqs)})={all_sub_reqs_ok}, Task({len(tasks)})={all_tasks_ok}")
        
        if all_sub_reqs_ok and all_tasks_ok:
            log_info(f"Auto-completing parent requirement: {parent.req_id} - {parent.title}")
            
            # 更新状态
            parent.status = 'completed'
            parent.progress = REQUIREMENT_STATUS_PROGRESS_MAP.get('completed', 100)
            parent.completed_at = datetime.now()
            parent.update_by = 'system_automation'
            parent.update_time = datetime.now()

            # 发送通知 (验收人、开发、测试、负责人、创建人)
            try:
                recipient_ids = set()
                if parent.assignee_id: recipient_ids.add(parent.assignee_id)
                if parent.developer_id: recipient_ids.add(parent.developer_id)
                if parent.tester_id: recipient_ids.add(parent.tester_id)
                if parent.accepter_id: recipient_ids.add(parent.accepter_id)
                
                if parent.create_by:
                    # 尝试用 username 查询
                    creator_id = db.query(SysUser.user_id).filter(SysUser.username == parent.create_by).scalar()
                    if not creator_id:
                        # 尝试用 nickname 查询 (兼容旧数据)
                        creator_id = db.query(SysUser.user_id).filter(SysUser.nickname == parent.create_by).scalar()
                    
                    if creator_id:
                        recipient_ids.add(creator_id)
                
                # 添加关注者
                followers = db.query(SysUserFollow.user_id).filter(
                    SysUserFollow.target_id == parent.req_id,
                    SysUserFollow.target_type == 'requirement'
                ).all()
                for f in followers:
                    recipient_ids.add(f[0])
                
                if recipient_ids:
                    log_info(f"Sending notification to {len(recipient_ids)} users for req {parent.req_id}")
                    
                    # 准备通知内容数据
                    REQ_STATUS_MAP = {
                        'draft': '草稿', 'pending': '待内审', 'reviewing': '待开发评审',
                        'tech_review': '待技术方案评审', 'planning': '规划中', 'developing': '开发中',
                        'testing': '测试中', 'completed': '已完成', 'closed': '已关闭', 'suspended': '已暂停'
                    }
                    PRIORITY_MAP = {
                        'low': '低', 'medium': '中', 'high': '高', 'urgent': '紧急'
                    }
                    
                    assignee_name = '未分配'
                    if parent.assignee_id:
                        assignee_user = db.query(SysUser).filter(SysUser.user_id == parent.assignee_id).first()
                        if assignee_user:
                            assignee_name = assignee_user.nickname or assignee_user.username
                            
                    sender_display = '系统自动' if parent.update_by == 'system_automation' else parent.update_by
                    status_text = REQ_STATUS_MAP.get(parent.status, parent.status)
                    priority_text = PRIORITY_MAP.get(parent.priority, parent.priority)
                    
                    html_content = f"""
                    <p><strong>需求编码:</strong> {parent.req_code or 'N/A'}</p>
                    <p><strong>需求标题:</strong> {parent.title}</p>
                    <p><strong>当前状态:</strong> {status_text}</p>
                    <p><strong>优先级:</strong> {priority_text}</p>
                    <p><strong>负责人:</strong> {assignee_name}</p>
                    <p><strong>更新人:</strong> {sender_display}</p>
                    <p><strong>更新时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p style="color: #909399; font-size: 12px; margin-top: 10px;">(由于所有子需求已上线且关联任务已完成，系统自动流转)</p>
                    """

                    for uid in recipient_ids:
                        notif = SysNotification(
                            user_id=uid,
                            title=f"需求自动完成: {parent.title}",
                            content=html_content,
                            type='system',
                            target_id=parent.req_id,
                            target_type='requirement',
                            create_time=datetime.now()
                        )
                        db.add(notif)
            except Exception as e:
                log_info(f"Failed to prepare notifications: {e}")
            
            # 记录日志 (SysAutomationLog)
            try:
                log_info(f"Creating automation log for rule {rule.rule_id} ({rule.rule_name})")
                log = SysAutomationLog(
                    rule_id=rule.rule_id,
                    rule_name=rule.rule_name,
                    trigger_event=rule.trigger_event,
                    target_id=str(parent.req_id),
                    execution_status='success',
                    execution_result=f'Auto-completed requirement {parent.req_id}. Notifications sent to {len(recipient_ids)} users.',
                    execution_time=datetime.now()
                )
                db.add(log)
                log_info("Flushing log to DB...")
                db.flush() # Ensure ID is generated and object is attached
                log_info(f"Log flushed. New Log ID: {log.log_id}")
            except Exception as e:
                log_info(f"Failed to create automation log: {e}")
                # Re-raise exception to ensure we don't commit partial state if critical?
                # Actually, if log fails, maybe we still want to update parent status?
                # But here we want to debug why it fails.
            
            log_info("Committing transaction...")
            db.commit()
            log_info("Transaction committed.")

@celery_app.task(bind=True)
def run_test_execution(self, execution_id, project_id):
    """Run test execution as a Celery task"""
    # Setup Sync DB Session
    db = AutomationSessionLocalSync()
    
    set_current_execution_id(execution_id)
    log_info(f"开始执行Celery任务: execution_id={execution_id}, project_id={project_id}")
    
    try:
        execution = db.query(AutomationExecution).get(execution_id)
        project = db.query(AutomationProject).get(project_id)
        
        if not execution or not project:
            log_info("Execution or Project not found")
            return

        # Find test file path
        project_file = db.query(ProjectFile).filter_by(project_id=project_id).first()
        file_path = None
        
        # Calculate root path (d:\project-management-platform)
        # file is in backend_fastapi/tasks/automation_tasks.py
        # 1. tasks
        # 2. backend_fastapi
        # 3. project-management-platform
        root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        if project_file:
            if os.path.exists(project_file.file_path):
                file_path = project_file.file_path
            elif not os.path.isabs(project_file.file_path):
                # Try relative path - assume relative to project root or backend_fastapi
                # Historically relative to backend, so now relative to backend_fastapi?
                # Let's try joining with backend_fastapi
                candidate = os.path.join(root_path, 'backend_fastapi', project_file.file_path)
                if os.path.exists(candidate):
                    file_path = candidate
                else:
                    # Try joining with root directly
                    candidate = os.path.join(root_path, project_file.file_path)
                    if os.path.exists(candidate):
                        file_path = candidate
        
        if not file_path:
            # Fallback: Try Test_Case dir in backend_fastapi
            test_case_dir = os.path.join(root_path, 'backend_fastapi', 'Test_Case')
            
            if os.path.exists(test_case_dir):
                for f in os.listdir(test_case_dir):
                    if f.startswith(f"{project_id}_") and f.endswith(".py"):
                        file_path = os.path.join(test_case_dir, f)
                        break
        
        if not file_path:
            raise Exception(f"找不到项目 {project_id} 的测试文件")

        log_info(f"找到测试文件: {file_path}")

        # Construct pytest command
        target = f"{file_path}::test_concurrent_independent_browsers"
        cmd = [sys.executable, '-m', 'pytest', target, '-v', '-s']
        
        # Environment variables
        env = os.environ.copy()
        env['AUTOMATION_EXECUTION_ID'] = str(execution_id)
        env['PROJECT_ID'] = str(project_id)
        env['SERVICE_HOST'] = os.environ.get('SERVICE_HOST', '127.0.0.1')
        env['SERVICE_PORT'] = os.environ.get('SERVICE_PORT', '5000')
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Add root path to PYTHONPATH so backend_fastapi can be imported
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{root_path}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = root_path
            
        log_info(f"执行命令: {' '.join(cmd)}")
        
        # Execute subprocess
        # We run inside backend_fastapi directory context?
        # No, root_path is safer.
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=root_path 
        )
        
        stdout_bytes, _ = process.communicate()
        return_code = process.returncode
        
        try:
            stdout = stdout_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                stdout = stdout_bytes.decode('gbk')
            except UnicodeDecodeError:
                stdout = stdout_bytes.decode('utf-8', errors='replace')

        if stdout:
            log_info(f"Pytest Output for execution {execution_id}:\n{stdout}")
            
        result = 'Passed' if return_code == 0 else 'Failed'
        log_info(f"任务执行完成，结果: {result}, 返回码: {return_code}")
        
        # Update execution record
        execution.status = result
        execution.end_time = datetime.now()
        execution.log_message = '测试执行成功' if result == 'Passed' else '测试执行失败'
        
        header = f"\n\n{'='*20} Console Output {'='*20}\n"
        if execution.detailed_log:
            execution.detailed_log = execution.detailed_log + header + stdout
        else:
            execution.detailed_log = header + stdout
            
        if project:
            project.status = result
            project.updated_at = datetime.now()
            
        db.commit()
        log_info(f"Celery任务 {execution_id} 数据库更新成功: {result}")
            
    except Exception as e:
        log_info(f"Celery任务执行异常 (execution_id={execution_id}): {str(e)}")
        try:
            execution = db.query(AutomationExecution).get(execution_id)
            if execution:
                execution.status = 'Failed'
                execution.log_message = str(e)
                execution.end_time = datetime.now()
                
            project = db.query(AutomationProject).get(project_id)
            if project:
                project.status = 'Failed'
                project.updated_at = datetime.now()
                
            db.commit()
        except Exception as update_error:
            log_info(f"更新失败状态时发生错误: {str(update_error)}")
    finally:
        db.close()
        clear_current_execution_id()
