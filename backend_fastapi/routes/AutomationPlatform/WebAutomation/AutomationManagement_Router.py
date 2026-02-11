from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from backend_fastapi.db.session import get_automation_db, get_db
from backend_fastapi.models.automation_models import AutomationProject, ProjectFile, AutomationExecution, AutomationExecutMethodLog, Project
from backend_fastapi.utils.LogManeger import log_info
from backend_fastapi.utils.AccountManager import generate_unique_email_for_url, get_credentials_for_url, update_account_data
from backend_fastapi.utils.TestCodeGenerator import TestCodeGenerator
from backend_fastapi.tasks.automation_tasks import run_test_execution
from celery.result import AsyncResult
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
import json
import os
import shutil
import requests
import re
import ast
import pytz
import asyncio

router = APIRouter(tags=["自动化管理"])

from .schemas import (
    GenerateAccountsRequest,
    GetLoginAccountsRequest,
    CreateProjectRequest,
    UpdateProjectRequest,
    ExecuteProjectRequest,
    TestConnectionRequest,
    SaveCodeRequest
)

# Helper Functions
async def _process_account_data_saving(project_id, process_name, test_steps, db: AsyncSession):
    try:
        stmt = select(AutomationProject).where(AutomationProject.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        
        if not project or not project.product_ids:
            return

        p_ids_raw = project.product_ids
        p_ids = []
        if isinstance(p_ids_raw, str):
            try:
                parsed = json.loads(p_ids_raw)
                if isinstance(parsed, list):
                    p_ids = [str(i).strip() for i in parsed if i]
                else:
                    p_ids = [str(parsed).strip()]
            except:
                p_ids = [i.strip() for i in p_ids_raw.split(',') if i.strip()]
        
        if not p_ids:
            return
            
        stmt = select(Project).where(Project.id.in_(p_ids))
        result = await db.execute(stmt)
        products = result.scalars().all()
        
        url_to_product_name = {}
        for p in products:
            addrs = []
            raw_addr = p.product_address or ""
            if raw_addr.strip().startswith('[') and raw_addr.strip().endswith(']'):
                try:
                    addrs = json.loads(raw_addr)
                    if not isinstance(addrs, list):
                        addrs = [str(addrs)]
                except:
                    addrs = [raw_addr]
            elif ',' in raw_addr and '{' not in raw_addr:
                addrs = [s.strip() for s in raw_addr.split(',')]
            else:
                addrs = [raw_addr]
            
            for addr in addrs:
                if addr:
                    url_to_product_name[addr.strip()] = p.product_package_name
                    url_to_product_name[addr.strip().rstrip('/')] = p.product_package_name

        safe_name = "".join([c for c in process_name if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).strip()
        file_name = f"{project_id}_{safe_name}.py"

        for index, step in enumerate(test_steps):
            if step.get('operation_event') == 'register':
                config = step.get('login_register_config', {})
                if not config:
                    continue
                    
                address_str = config.get('address_url', '')
                account_str = config.get('account', '')
                password = config.get('password', '123456789')
                
                urls = [u.strip() for u in address_str.split('\n') if u.strip()]
                emails = [e.strip() for e in account_str.split('\n') if e.strip()]
                
                product_updates = {} 
                
                for i, url in enumerate(urls):
                    if i < len(emails):
                        email = emails[i]
                        p_name = url_to_product_name.get(url) or url_to_product_name.get(url.rstrip('/'))
                        
                        if not p_name and products:
                            p_name = products[0].product_package_name
                        
                        if p_name:
                            if p_name not in product_updates:
                                product_updates[p_name] = {}
                            product_updates[p_name][url] = {'email': email, 'password': password}

                for p_name, addr_map in product_updates.items():
                    update_account_data(
                        product_name=p_name,
                        process_name=process_name,
                        test_file_name=file_name,
                        step_index=index,
                        step_name=step.get('step_name', f'Step {index+1}'),
                        operation_event='register',
                        address_url_map=addr_map
                    )
                    
    except Exception as e:
        log_info(f"Failed to save account data to YAML: {str(e)}")

async def generate_test_case_path(automation_project, db: AsyncSession):
    # backend_fastapi/routes/AutomationPlatform/WebAutomation
    # 1. WebAutomation
    # 2. AutomationPlatform
    # 3. routes
    # 4. backend_fastapi
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    test_case_dir = os.path.join(root_path, 'Test_Case')
    if not os.path.exists(test_case_dir):
        os.makedirs(test_case_dir)
        
    product_code = "Unknown"
    system_type = "Web"
    
    linked_project = None
    if automation_project.project_id:
        stmt = select(Project).where(Project.id == automation_project.project_id)
        result = await db.execute(stmt)
        linked_project = result.scalar_one_or_none()
    
    if linked_project:
        if linked_project.product_id:
            product_code = linked_project.product_id
        if linked_project.system_type:
            system_type = linked_project.system_type
    
    if product_code == "Unknown" and automation_project.product_ids:
        try:
            ids = json.loads(automation_project.product_ids)
            if ids:
                product_code = ids[0]
        except:
            pass
            
    if automation_project.system:
        system_type = automation_project.system
        
    def sanitize(s):
        return "".join([c for c in s if c.isalnum() or c in ('_',)]).strip()
    
    product_code = sanitize(product_code)
    system_type = sanitize(system_type)
    
    base_name = f"{product_code}_{system_type}_test"
    
    stmt = select(ProjectFile).where(ProjectFile.project_id == automation_project.id)
    result = await db.execute(stmt)
    existing_record = result.scalar_one_or_none()
    
    if existing_record and existing_record.file_path:
        file_name = os.path.basename(existing_record.file_path)
        name_part = os.path.splitext(file_name)[0]
        
        if name_part.startswith(base_name):
            suffix = name_part[len(base_name):]
            if suffix == "" or (suffix.startswith("_") and suffix[1:].isdigit()):
                abs_path = existing_record.file_path
                if not os.path.isabs(abs_path):
                    abs_path = os.path.join(test_case_dir, file_name) # Assume flat structure in Test_Case
                
                rel_path = existing_record.file_path
                # Normalize rel path
                if os.path.isabs(rel_path):
                     try:
                         rel_path = os.path.relpath(abs_path, root_path)
                     except:
                         rel_path = os.path.join('Test_Case', file_name)
                
                return abs_path, rel_path

    try:
        files = os.listdir(test_case_dir)
    except:
        files = []
        
    max_index = 0
    base_exists = False
    
    for f in files:
        if not f.endswith(".py"): continue
        name_part = f[:-3]
        
        if name_part == base_name:
            base_exists = True
            if max_index == 0: max_index = 1
        elif name_part.startswith(base_name + "_"):
            suffix = name_part[len(base_name)+1:]
            if suffix.isdigit():
                idx = int(suffix)
                if idx > max_index:
                    max_index = idx
    
    if not base_exists:
        new_name = f"{base_name}.py"
    else:
        new_index = max_index + 1
        if new_index == 1: new_index = 2
        new_name = f"{base_name}_{new_index}.py"
        
    abs_path = os.path.join(test_case_dir, new_name)
    # Return relative path consistent with Flask version: Test_Case/foo.py
    rel_path = os.path.join('Test_Case', new_name)
    return abs_path, rel_path

# Routes

@router.post('/generate_register_accounts')
async def generate_register_accounts(req: GenerateAccountsRequest):
    try:
        if not req.urls:
            return {'code': 400, 'message': 'URLs list is required'}
            
        results = {}
        for url in req.urls:
            email = generate_unique_email_for_url(url)
            results[url] = {
                'email': email,
                'password': '123456789'
            }
            
        return {'code': 200, 'message': 'Accounts generated successfully', 'data': results}
    except Exception as e:
        log_info(f"Generate accounts error: {str(e)}")
        return {'code': 500, 'message': str(e)}

@router.post('/get_login_accounts')
async def get_login_accounts(req: GetLoginAccountsRequest):
    try:
        if not req.urls:
            return {'code': 400, 'message': '产品地址必填'}
            
        results = {}
        for url in req.urls:
            creds = get_credentials_for_url(url)
            if creds:
                results[url] = creds
            else:
                results[url] = {
                    'email': '',
                    'password': ''
                }
            
        return {'code': 200, 'message': '账号密码获取成功', 'data': results}
    except Exception as e:
        log_info(f"Get login accounts error: {str(e)}")
        return {'code': 500, 'message': str(e)}

@router.get('/test_projects')
async def get_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    process_name: Optional[str] = None,
    status: Optional[str] = None,
    product_names: Optional[str] = None,
    environment: Optional[str] = None,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        stmt = select(AutomationProject, Project).outerjoin(
            Project, AutomationProject.project_id == Project.id
        )
        
        if process_name:
            stmt = stmt.where(AutomationProject.process_name.like(f'%{process_name}%'))
        if status:
            status_list = status.split(',')
            stmt = stmt.where(AutomationProject.status.in_(status_list))
        if product_names:
            name_list = product_names.split(',')
            stmt = stmt.where(Project.product_package_name.in_(name_list))
        if environment:
            stmt = stmt.where(Project.environment == environment)
            
        stmt = stmt.order_by(desc(AutomationProject.updated_at))
        
        # Pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        items = result.all() # list of (AutomationProject, Project)
        
        projects = []
        for ap, p in items:
            ap_dict = ap.to_dict()
            
            # Deserialize complex fields
            try:
                if ap_dict.get('product_ids') and isinstance(ap_dict['product_ids'], str):
                    try:
                        parsed = json.loads(ap_dict['product_ids'])
                        if isinstance(parsed, list):
                            ap_dict['product_ids'] = parsed
                        else:
                            ap_dict['product_ids'] = [str(parsed)]
                    except:
                        ap_dict['product_ids'] = [i.strip() for i in ap_dict['product_ids'].split(',') if i.strip()]
            except:
                ap_dict['product_ids'] = []

            for field in ['test_steps', 'tab_switch_config', 'assertion_config', 'screenshot_config', 'product_package_names']:
                try:
                    if ap_dict.get(field) and isinstance(ap_dict[field], str):
                        ap_dict[field] = json.loads(ap_dict[field])
                except:
                    if field in ['tab_switch_config', 'assertion_config', 'screenshot_config']:
                        ap_dict[field] = {}
                    elif field == 'test_steps':
                        ap_dict[field] = []

            if p:
                ap_dict['project_info'] = p.to_dict()
            else:
                ap_dict['project_info'] = {}
            projects.append(ap_dict)
            
        return {
            'code': 200,
            'message': 'Success',
            'data': {
                'list': projects,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }
    except Exception as e:
        log_info(f"Get projects error: {str(e)}")
        return {'code': 500, 'message': str(e)}

@router.post('/test_projects')
async def create_project(
    req: CreateProjectRequest,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        log_info(f"接收到创建项目请求: {req.process_name}")
        
        product_ids_str = "[]"
        if isinstance(req.product_ids, list):
            cleaned_ids = []
            for item in req.product_ids:
                if isinstance(item, dict):
                    cleaned_ids.append(str(item.get('id', '')))
                else:
                    cleaned_ids.append(str(item))
            cleaned_ids = [i for i in cleaned_ids if i]
            product_ids_str = json.dumps(cleaned_ids, ensure_ascii=False)
        elif req.product_ids:
            product_ids_str = str(req.product_ids)
            
        project_id = req.project_id
        if not project_id and product_ids_str != "[]":
            try:
                ids = json.loads(product_ids_str)
                if ids:
                    first_val = ids[0]
                    related_project = None
                    if first_val.isdigit():
                         stmt = select(Project).where(Project.id == int(first_val))
                         res = await db.execute(stmt)
                         related_project = res.scalar_one_or_none()
                    
                    if not related_project:
                         stmt = select(Project).where(Project.product_id == first_val)
                         res = await db.execute(stmt)
                         related_project = res.scalar_one_or_none()
                         
                    if not related_project:
                         stmt = select(Project).where(Project.product_package_name == first_val)
                         res = await db.execute(stmt)
                         related_project = res.scalar_one_or_none()
                         
                    if related_project:
                        project_id = related_project.id
            except:
                pass
                
        def to_json(val):
            if val is None: return None
            if isinstance(val, (dict, list)): return json.dumps(val, ensure_ascii=False)
            return val

        new_project = AutomationProject(
            process_name=req.process_name,
            product_ids=product_ids_str,
            system=req.system,
            product_type=req.product_type,
            environment=req.environment,
            product_address=req.product_address,
            project_id=project_id,
            product_package_names=to_json(req.product_package_names),
            test_steps=to_json(req.test_steps),
            tab_switch_config=to_json(req.tab_switch_config),
            assertion_config=to_json(req.assertion_config),
            screenshot_config=to_json(req.screenshot_config),
            status='待执行',
            created_by=req.created_by
        )
        
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        
        try:
            if req.test_steps:
                await _process_account_data_saving(new_project.id, new_project.process_name, req.test_steps, db)

            file_path, rel_path = await generate_test_case_path(new_project, db)
            
            try:
                project_data_for_gen = {
                    'process_name': new_project.process_name,
                    'product_ids': new_project.product_ids,
                    'product_address': new_project.product_address,
                    'test_steps': req.test_steps
                }
                generated_code = TestCodeGenerator.generate_full_test_code(project_data_for_gen)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(generated_code)
                log_info(f"Generated test code for project {new_project.id} at {file_path}")
            except Exception as e:
                log_info(f"Error generating test code: {str(e)}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Code generation failed: {str(e)}\n")
            
            new_file = ProjectFile(
                project_id=new_project.id,
                project_name=new_project.process_name,
                file_name=os.path.basename(file_path),
                file_path=rel_path,
                file_type='py'
            )
            db.add(new_file)
            await db.commit()
        except Exception as e:
            log_info(f"Failed to create test file: {str(e)}")
            
        resp_data = new_project.to_dict()
        resp_data['test_steps'] = req.test_steps
        if req.tab_switch_config: resp_data['tab_switch_config'] = req.tab_switch_config
        if req.assertion_config: resp_data['assertion_config'] = req.assertion_config
        if req.screenshot_config: resp_data['screenshot_config'] = req.screenshot_config
        
        return {'code': 200, 'message': '项目创建成功', 'data': resp_data}
        
    except Exception as e:
        await db.rollback()
        log_info(f"Create project error: {str(e)}")
        return {'code': 500, 'message': str(e)}

@router.put('/test_projects/{project_id}')
async def update_project(
    project_id: int,
    req: UpdateProjectRequest,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        stmt = select(AutomationProject).where(AutomationProject.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        
        if not project:
            return {'code': 404, 'message': '项目未找到'}
            
        if req.process_name is not None: project.process_name = req.process_name
        
        if req.product_ids is not None:
            if isinstance(req.product_ids, list):
                cleaned_ids = []
                for item in req.product_ids:
                    if isinstance(item, dict):
                        cleaned_ids.append(str(item.get('id', '')))
                    else:
                        cleaned_ids.append(str(item))
                cleaned_ids = [i for i in cleaned_ids if i]
                project.product_ids = json.dumps(cleaned_ids, ensure_ascii=False)
            else:
                project.product_ids = str(req.product_ids)
                
        if req.system is not None: project.system = req.system
        if req.product_type is not None: project.product_type = req.product_type
        if req.environment is not None: project.environment = req.environment
        if req.product_address is not None: project.product_address = req.product_address
        if req.project_id is not None: project.project_id = req.project_id
        
        def to_json(val):
            if val is None: return None
            if isinstance(val, (dict, list)): return json.dumps(val, ensure_ascii=False)
            return val

        if req.product_package_names is not None: project.product_package_names = to_json(req.product_package_names)
        if req.test_steps is not None: project.test_steps = to_json(req.test_steps)
        if req.tab_switch_config is not None: project.tab_switch_config = to_json(req.tab_switch_config)
        if req.assertion_config is not None: project.assertion_config = to_json(req.assertion_config)
        if req.screenshot_config is not None: project.screenshot_config = to_json(req.screenshot_config)
        
        await db.commit()
        
        try:
            stmt = select(ProjectFile).where(ProjectFile.project_id == project_id)
            result = await db.execute(stmt)
            project_file = result.scalar_one_or_none()
            
            target_path, target_rel_path = await generate_test_case_path(project, db)
            
            test_steps_list = []
            if project.test_steps:
                try:
                    test_steps_list = json.loads(project.test_steps) if isinstance(project.test_steps, str) else project.test_steps
                except:
                    pass
            
            gen_data = {
                'process_name': project.process_name,
                'product_ids': project.product_ids,
                'product_address': project.product_address,
                'test_steps': test_steps_list
            }
            
            code = TestCodeGenerator.generate_full_test_code(gen_data)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(code)
                
            if not project_file:
                new_file = ProjectFile(
                    project_id=project.id,
                    project_name=project.process_name,
                    file_name=os.path.basename(target_path),
                    file_path=target_rel_path,
                    file_type='py'
                )
                db.add(new_file)
            else:
                project_file.file_name = os.path.basename(target_path)
                project_file.file_path = target_rel_path
                
            await db.commit()
        except Exception as e:
            log_info(f"Failed to update test file: {str(e)}")
            
        resp_data = project.to_dict()
        for field in ['test_steps', 'tab_switch_config', 'assertion_config', 'screenshot_config', 'product_package_names']:
            val = resp_data.get(field)
            if isinstance(val, str):
                try:
                    resp_data[field] = json.loads(val)
                except:
                    pass
                    
        return {'code': 200, 'message': 'Project updated successfully', 'data': resp_data}
        
    except Exception as e:
        await db.rollback()
        log_info(f"Update project error: {str(e)}")
        return {'code': 500, 'message': str(e)}

@router.delete('/test_projects/{project_id}')
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        stmt = select(AutomationProject).where(AutomationProject.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        
        if not project:
            return {'code': 404, 'message': '项目未找到'}
            
        # Delete executions
        try:
            stmt = select(AutomationExecution).where(AutomationExecution.project_id == project_id)
            result = await db.execute(stmt)
            executions = result.scalars().all()
            
            for execution in executions:
                stmt_log = select(AutomationExecutMethodLog).where(AutomationExecutMethodLog.execution_id == execution.id)
                res_log = await db.execute(stmt_log)
                logs = res_log.scalars().all()
                for log in logs:
                    await db.delete(log)
                await db.delete(execution)
        except Exception as e:
            log_info(f"Error deleting execution records: {str(e)}")
            
        # Delete file
        try:
            stmt = select(ProjectFile).where(ProjectFile.project_id == project_id)
            result = await db.execute(stmt)
            project_file = result.scalar_one_or_none()
            
            paths_to_check = []
            root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

            if project_file and project_file.file_path:
                paths_to_check.append(project_file.file_path)
                if not os.path.isabs(project_file.file_path):
                     paths_to_check.append(os.path.join(root_path, project_file.file_path))
                     
            generated_path, _ = await generate_test_case_path(project, db)
            paths_to_check.append(generated_path)
            
            unique_paths = list(set(paths_to_check))
            for path in unique_paths:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                        log_info(f"Deleted test file: {path}")
                    except: pass
            
            if project_file:
                await db.delete(project_file)
        except Exception as e:
            log_info(f"Error deleting file: {str(e)}")
            
        await db.delete(project)
        await db.commit()
        
        return {'code': 200, 'message': '项目已删除'}
    except Exception as e:
        await db.rollback()
        log_info(f"Delete project error: {str(e)}")
        return {'code': 500, 'message': str(e)}

@router.post('/test_projects/{project_id}/execute')
async def execute_project(
    project_id: int,
    req: ExecuteProjectRequest,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        log_info(f"收到项目执行请求: project_id={project_id}")
        stmt = select(AutomationProject).where(AutomationProject.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        
        if not project:
            return {'code': 404, 'message': '项目未找到'}
            
        execution = AutomationExecution(
            project_id=project.id,
            process_name=project.process_name,
            product_ids=project.product_ids,
            system=project.system,
            product_type=project.product_type,
            environment=project.environment,
            product_address=project.product_address,
            status='Running',
            start_time=datetime.now(),
            executed_by=req.executed_by or 'admin',
            log_message='正在执行',
            detailed_log=f"收到项目执行请求: project_id={project_id}, 执行人={req.executed_by}\n"
        )
        
        db.add(execution)
        project.status = 'Running'
        await db.commit()
        await db.refresh(execution)
        
        # Trigger Celery task
        task = run_test_execution.apply_async(args=[execution.id, project.id])
        
        execution.task_id = task.id
        await db.commit()
        
        return {'code': 200, 'message': '执行已启动', 'data': {'execution_id': execution.id, 'task_id': task.id}}
    except Exception as e:
        await db.rollback()
        log_info(f"项目执行请求异常: {str(e)}")
        return {'code': 500, 'message': str(e)}

@router.post('/test_projects/{project_id}/cancel')
async def cancel_execution(
    project_id: int,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        stmt = select(AutomationExecution).where(
            AutomationExecution.project_id == project_id,
            AutomationExecution.status == 'Running'
        ).order_by(desc(AutomationExecution.start_time))
        result = await db.execute(stmt)
        execution = result.scalar_one_or_none()
        
        if execution:
            execution.status = 'Cancelled'
            execution.end_time = datetime.now()
            execution.log_message = (execution.log_message or '') + '\n执行已取消'
            
        stmt = select(AutomationProject).where(AutomationProject.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        
        if project:
            project.status = 'Cancelled'
            
        await db.commit()
        return {'code': 200, 'message': '执行已取消'}
    except Exception as e:
        await db.rollback()
        return {'code': 500, 'message': str(e)}

@router.get('/executions')
async def get_executions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    project_id: Optional[int] = None,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        stmt = select(AutomationExecution)
        if project_id:
            stmt = stmt.where(AutomationExecution.project_id == project_id)
            
        stmt = stmt.order_by(desc(AutomationExecution.start_time))
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        items = result.scalars().all()
        
        executions = []
        for exe in items:
            executions.append({
                'id': exe.id,
                'process_name': exe.process_name,
                'status': exe.status,
                'start_time': exe.start_time.strftime('%Y-%m-%d %H:%M:%S') if exe.start_time else None,
                'end_time': exe.end_time.strftime('%Y-%m-%d %H:%M:%S') if exe.end_time else None,
                'executed_by': exe.executed_by
            })
            
        return {
            'code': 200, 
            'message': '执行记录列表获取成功', 
            'data': {
                'list': executions,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }
    except Exception as e:
        return {'code': 500, 'message': str(e)}

@router.get('/executions/{execution_id}')
async def get_execution_detail(
    execution_id: int,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        stmt = select(AutomationExecution).where(AutomationExecution.id == execution_id)
        result = await db.execute(stmt)
        execution = result.scalar_one_or_none()
        
        if not execution:
            log_info(f"Execution not found: {execution_id}")
            return {'code': 404, 'message': f'执行记录未找到 (ID: {execution_id})'}
            
        # Check Celery status logic
        if execution.status == 'Running' and execution.task_id:
            try:
                res = AsyncResult(execution.task_id)
                log_info(f"Checking Celery task status for execution {execution_id}: {res.status}")
                
                if res.status in ['SUCCESS', 'FAILURE', 'REVOKED']:
                    if res.status == 'SUCCESS':
                         execution.status = 'Completed' 
                         execution.log_message = (execution.log_message or '') + '\n(系统检测到后台任务已结束，但状态未同步)'
                    elif res.status == 'FAILURE':
                        execution.status = 'Error'
                        execution.log_message = (execution.log_message or '') + f'\n(后台任务异常: {str(res.result)})'
                    
                    if res.date_done:
                        done_time = res.date_done
                        if isinstance(done_time, str):
                            try:
                                done_time = datetime.fromisoformat(done_time)
                            except:
                                done_time = datetime.now()
                        
                        if done_time.tzinfo is None:
                             done_time = done_time + timedelta(hours=8)
                        else:
                             shanghai_tz = pytz.timezone('Asia/Shanghai')
                             done_time = done_time.astimezone(shanghai_tz).replace(tzinfo=None)
                        
                        execution.end_time = done_time
                    else:
                        execution.end_time = datetime.now()
                    
                    await db.commit()
                    log_info(f"Synced execution {execution_id} status from Celery: {execution.status}")
            except Exception as e:
                log_info(f"Failed to check Celery status: {e}")

        # Ensure Project status is synced with Execution status
        # This covers cases where execution was updated but project wasn't (e.g. Celery error or previous miss)
        if execution.project_id and execution.status in ['Completed', 'Error', 'Failed', 'Cancelled']:
            stmt_proj = select(AutomationProject).where(AutomationProject.id == execution.project_id)
            res_proj = await db.execute(stmt_proj)
            project = res_proj.scalar_one_or_none()
            
            if project and project.status == 'Running':
                if execution.status in ['Error', 'Failed']:
                    project.status = 'Failed'
                elif execution.status == 'Completed':
                    project.status = 'Completed'
                elif execution.status == 'Cancelled':
                    project.status = 'Cancelled'
                
                project.updated_at = datetime.now()
                await db.commit()
                log_info(f"Synced project {project.id} status to {project.status} based on execution {execution.id}")

        # Parse logs
        detailed_log_content = execution.detailed_log or ""
        # Lazy import to avoid circular dependency if any
        from backend_fastapi.utils.UitilTools import UitilTools
        parsed_log = UitilTools.parse_automation_log(detailed_log_content)
        
        # Get Method Logs
        stmt_logs = select(AutomationExecutMethodLog).where(AutomationExecutMethodLog.execution_id == execution_id)
        res_logs = await db.execute(stmt_logs)
        method_logs_records = res_logs.scalars().all()
        
        method_logs_data = []
        for record in method_logs_records:
            method_logs_data.append({
                'name': record.method_name,
                'logs': UitilTools.parse_automation_log(record.log_content)
            })

        # Extract Error Logs
        error_log = None
        if detailed_log_content:
            console_output_marker = f"\n\n{'='*20} Console Output {'='*20}\n"
            if console_output_marker in detailed_log_content:
                parts = detailed_log_content.split(console_output_marker)
                if len(parts) > 1:
                    console_output = parts[1]
                    
                    if "FAILURES" in console_output or "ERRORS" in console_output:
                         match = re.search(r'(={10,}\s+(FAILURES|ERRORS)\s+={10,}[\s\S]*)', console_output)
                         if match:
                             error_content = match.group(1)
                             filtered_lines = []
                             log_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+-\s+.*?\s+-\s+INFO\s+-')
                             for line in error_content.split('\n'):
                                 if not log_pattern.match(line.strip()):
                                     filtered_lines.append(line)
                             error_content = '\n'.join(filtered_lines)
                             
                             error_log = {
                                 'name': '错误日志',
                                 'logs': UitilTools.parse_automation_log(error_content, is_error_log=True)
                             }
                         else:
                             filtered_lines = []
                             log_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+-\s+.*?\s+-\s+INFO\s+-')
                             for line in console_output.split('\n'):
                                 if not log_pattern.match(line.strip()):
                                     filtered_lines.append(line)
                                     
                             error_log = {
                                 'name': '错误日志',
                                 'logs': UitilTools.parse_automation_log('\n'.join(filtered_lines), is_error_log=True)
                             }
        
        if error_log:
            method_logs_data.append(error_log)
            
        # Legacy test methods count
        test_methods_count = 0
        if method_logs_data:
            test_methods_count = len([m for m in method_logs_data if m.get('name') != '错误日志'])
        else:
            try:
                match = re.search(r'测试文件分析结果:\s*(\{.*?\})', detailed_log_content)
                if match:
                    analysis_result = ast.literal_eval(match.group(1))
                    if isinstance(analysis_result, dict) and 'test_methods' in analysis_result:
                        methods = analysis_result['test_methods']
                        filtered_methods = [m for m in methods if m != 'test_concurrent_independent_browsers']
                        test_methods_count = len(filtered_methods)
            except Exception as e:
                log_info(f"Failed to parse legacy test methods: {e}")
                test_methods_count = len(set(s.get('method') for s in parsed_log.get('testSteps', []) if s.get('method')))

        data = execution.to_dict()
        data['logs'] = parsed_log
        data['method_logs'] = method_logs_data
        data['stats'] = {
            'test_steps_count': len(parsed_log.get('testSteps', [])),
            'test_methods_count': test_methods_count,
            'screenshots_count': detailed_log_content.count('Screenshot saved at'),
            'keyword_data_count': sum(len(step.get('logs', [])) for step in parsed_log.get('testSteps', []))
        }
            
        return {'code': 200, 'message': 'Success', 'data': data}
    except Exception as e:
        log_info(f"Get execution detail error: {str(e)}")
        return {'code': 500, 'message': f'获取执行记录详情时发生错误: {str(e)}'}

@router.get('/image')
async def get_image(path: str = Query(..., description="File path to image")):
    try:
        if not path:
            return {'code': 400, 'message': '路径是必填项'}
            
        if not os.path.exists(path):
            return {'code': 404, 'message': '文件未找到'}
            
        return FileResponse(path)
    except Exception as e:
        log_info(f"Get image error: {str(e)}")
        return {'code': 500, 'message': '获取图片时发生错误'}

@router.post('/test_connection')
async def test_connection(req: TestConnectionRequest):
    try:
        if not req.urls:
            return {'code': 400, 'message': '请提供要测试的URL'}
            
        results = []
        loop = asyncio.get_event_loop()
        
        # Use session to manage connections
        with requests.Session() as session:
            for url in req.urls:
                status = 'failed'
                message = ''
                try:
                    # Add scheme if missing
                    target_url = url
                    if not target_url.startswith('http'):
                        target_url = 'http://' + target_url
                        
                    # Use run_in_executor to avoid blocking the event loop
                    response = await loop.run_in_executor(
                        None, 
                        lambda: session.get(target_url, timeout=5)
                    )
                    
                    if response.status_code < 400:
                        status = 'success'
                    else:
                        status = 'failed'
                        message = f'Status Code: {response.status_code}'
                except Exception as e:
                    status = 'failed'
                    message = str(e)
                    
                results.append({
                    'url': url,
                    'status': status,
                    'message': message
                })
            
        return {'code': 200, 'message': '测试完成', 'data': results}
    except Exception as e:
        log_info(f"Test connection error: {str(e)}")
        return {'code': 500, 'message': str(e)}

# Code Management API - Get Code
@router.get('/code/get')
async def get_code(
    project_id: int = Query(..., description="Project ID"),
    file_path: Optional[str] = Query(None, description="Specific file path"),
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        # Find associated file
        stmt = select(ProjectFile).where(ProjectFile.project_id == project_id, ProjectFile.is_active == True)
        result = await db.execute(stmt)
        project_file = result.scalar_one_or_none()
        
        stmt = select(AutomationProject).where(AutomationProject.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        
        log_info(f"Get code for project {project_id}")
        
        file_content = ""
        target_file_path = ""
        
        # Priority 1: Use requested file path if provided
        if file_path:
             if os.path.exists(file_path) and file_path.endswith('.py'):
                 target_file_path = file_path
        
        # Priority 2: Use recorded ProjectFile path
        if not target_file_path and project_file:
            if os.path.exists(project_file.file_path):
                target_file_path = project_file.file_path
            else:
                # Try to resolve relative path
                root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                candidate_path = os.path.join(root_path, project_file.file_path)
                
                if os.path.exists(candidate_path):
                    target_file_path = candidate_path
                else:
                    # Try looking in Test_Case directory
                    filename = os.path.basename(project_file.file_path)
                    test_case_dir = os.path.join(root_path, 'Test_Case')
                    candidate_path = os.path.join(test_case_dir, filename)
                    
                    if os.path.exists(candidate_path):
                        target_file_path = candidate_path

            if target_file_path:
                with open(target_file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            else:
                return {'code': 404, 'message': '测试文件未找到，请先创建或保存项目以生成测试文件。', 
                        'data': {'file_path': project_file.file_path, 'file_name': os.path.basename(project_file.file_path)}}
        else:
            # Try to guess path
            root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            test_case_dir = os.path.join(root_path, 'Test_Case')
            
            p_name = project.process_name if project else "test"
            safe_name = "".join([c for c in p_name if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).strip()
            
            file_name = f"{project_id}_{safe_name}.py"
            target_file_path = os.path.join(test_case_dir, file_name)
            
            if os.path.exists(target_file_path):
                with open(target_file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            else:
                # Fallback: try generic name
                file_name = f"{project_id}_test.py"
                target_file_path = os.path.join(test_case_dir, file_name)
                if os.path.exists(target_file_path):
                    with open(target_file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                else:
                    return {'code': 404, 'message': '测试文件未找到，请先创建或保存项目以生成测试文件。',
                            'data': {'file_path': target_file_path, 'file_name': file_name}}

        return {
            'code': 200, 
            'message': '测试代码获取成功', 
            'data': {
                'content': file_content,
                'file_path': target_file_path
            }
        }
    except Exception as e:
        log_info(f"Get code error: {str(e)}")
        return {'code': 500, 'message': '获取测试代码时发生错误'}

# Code Management API - Save Code
@router.post('/code/save')
async def save_code(
    req: SaveCodeRequest,
    db: AsyncSession = Depends(get_automation_db)
):
    try:
        project_id = req.project_id
        content = req.content
        file_path = req.file_path
        
        stmt = select(AutomationProject).where(AutomationProject.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        
        stmt = select(ProjectFile).where(ProjectFile.project_id == project_id)
        result = await db.execute(stmt)
        project_file = result.scalar_one_or_none()
        
        # Determine file path if not provided
        if not file_path:
            if project_file:
                file_path = project_file.file_path
                # If relative, make absolute for writing
                if not os.path.isabs(file_path):
                    root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                    file_path = os.path.join(root_path, file_path)
            else:
                if project:
                    generated_abs, _ = await generate_test_case_path(project, db)
                    file_path = generated_abs
                else:
                    # Generate default path
                    root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                    test_case_dir = os.path.join(root_path, 'Test_Case')
                    if not os.path.exists(test_case_dir):
                        os.makedirs(test_case_dir)
                        
                    file_name = f"{project_id}_test.py"
                    file_name = "".join([c for c in file_name if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).strip()
                    file_path = os.path.join(test_case_dir, file_name)

        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Update or Create ProjectFile record
        if project_file:
            # Update path if we changed it (and ensure we store relative path if possible)
            # But usually we just update timestamp
            project_file.updated_at = datetime.now()
        else:
            file_name = os.path.basename(file_path)
            # Calculate relative path
            root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            try:
                rel_path = os.path.relpath(file_path, root_path)
            except:
                rel_path = file_path
                
            new_file = ProjectFile(
                project_id=project_id,
                project_name=project.process_name if project else 'Unknown',
                file_name=file_name,
                file_path=rel_path,
                file_type='py'
            )
            db.add(new_file)
            
        await db.commit()
        
        return {'code': 200, 'message': '测试代码保存成功'}
    except Exception as e:
        await db.rollback()
        log_info(f"Save code error: {str(e)}")
        return {'code': 500, 'message': '保存测试代码时发生错误'}
