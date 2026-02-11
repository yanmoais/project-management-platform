from backend_fastapi.core.celery_app import celery_app
from backend_fastapi.db.session import AutomationSessionLocalSync
from backend_fastapi.models.automation_models import AutomationExecution, AutomationProject, ProjectFile
from backend_fastapi.utils.LogManeger import log_info, set_current_execution_id, clear_current_execution_id
from datetime import datetime
import os
import sys
import subprocess

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
