from flask import Blueprint, request, jsonify, send_file, current_app
import os
import requests
import json
import subprocess
import sys
from backend.models import db, AutomationExecution, AutomationProject, Project, ProjectFile, AutomationExecutMethodLog
from backend.utils.UitilTools import UitilTools
from backend.utils.LogManeger import log_info, set_current_execution_id, clear_current_execution_id
from datetime import datetime
import threading
import time
import random
from backend.extensions import celery
from celery.result import AsyncResult
from datetime import timedelta
from backend.utils.AccountManager import generate_unique_email_for_url, update_account_data, get_credentials_for_url
from backend.utils.TestCodeGenerator import TestCodeGenerator

automation_management_bp = Blueprint('automation_management', __name__)

@automation_management_bp.route('/generate_register_accounts', methods=['POST'])
def generate_register_accounts():
    try:
        data = request.json
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'code': 400, 'message': 'URLs list is required'}), 400
            
        results = {}
        for url in urls:
            email = generate_unique_email_for_url(url)
            results[url] = {
                'email': email,
                'password': '123456789'
            }
            
        return jsonify({
            'code': 200,
            'message': 'Accounts generated successfully',
            'data': results
        })
    except Exception as e:
        log_info(f"Generate accounts error: {str(e)}")
        return jsonify({'code': 500, 'message': str(e)}), 500

@automation_management_bp.route('/get_login_accounts', methods=['POST'])
def get_login_accounts():
    try:
        data = request.json
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'code': 400, 'message': '产品地址必填'}), 400
            
        results = {}
        for url in urls:
            creds = get_credentials_for_url(url)
            if creds:
                results[url] = creds
            else:
                results[url] = {
                    'email': '',
                    'password': ''
                }
            
        return jsonify({
            'code': 200,
            'message': '账号密码获取成功',
            'data': results
        })
    except Exception as e:
        log_info(f"Get login accounts error: {str(e)}")
        return jsonify({'code': 500, 'message': str(e)}), 500

@automation_management_bp.route('/test_projects', methods=['GET'])
def get_projects():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # Join AutomationProject with Project to get product details
        query = db.session.query(AutomationProject, Project).outerjoin(
            Project, AutomationProject.project_id == Project.id
        )
        
        # Filters
        process_name = request.args.get('process_name')
        if process_name:
            query = query.filter(AutomationProject.process_name.like(f'%{process_name}%'))
            
        status = request.args.get('status')
        if status:
            # Handle multiple statuses (comma separated)
            status_list = status.split(',')
            query = query.filter(AutomationProject.status.in_(status_list))
            
        product_names = request.args.get('product_names')
        if product_names:
            # Handle multiple product names (comma separated)
            name_list = product_names.split(',')
            query = query.filter(Project.product_package_name.in_(name_list))

        environment = request.args.get('environment')
        if environment:
            query = query.filter(Project.environment == environment)
            
        pagination = query.order_by(AutomationProject.updated_at.desc()).paginate(
            page=page, per_page=page_size, error_out=False
        )
        
        projects = []
        for ap, p in pagination.items:
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
                        # Fallback for old CSV format
                        ap_dict['product_ids'] = [i.strip() for i in ap_dict['product_ids'].split(',') if i.strip()]
            except:
                ap_dict['product_ids'] = []

            try:
                if ap_dict.get('test_steps') and isinstance(ap_dict['test_steps'], str):
                    ap_dict['test_steps'] = json.loads(ap_dict['test_steps'])
            except:
                ap_dict['test_steps'] = []
                
            try:
                if ap_dict.get('tab_switch_config') and isinstance(ap_dict['tab_switch_config'], str):
                    ap_dict['tab_switch_config'] = json.loads(ap_dict['tab_switch_config'])
            except:
                ap_dict['tab_switch_config'] = {}
                
            try:
                if ap_dict.get('assertion_config') and isinstance(ap_dict['assertion_config'], str):
                    ap_dict['assertion_config'] = json.loads(ap_dict['assertion_config'])
            except:
                ap_dict['assertion_config'] = {}
                
            try:
                if ap_dict.get('screenshot_config') and isinstance(ap_dict['screenshot_config'], str):
                    ap_dict['screenshot_config'] = json.loads(ap_dict['screenshot_config'])
            except:
                ap_dict['screenshot_config'] = {}
                
            try:
                if ap_dict.get('product_package_names') and isinstance(ap_dict['product_package_names'], str):
                    ap_dict['product_package_names'] = json.loads(ap_dict['product_package_names'])
            except:
                pass

            if p:
                ap_dict['project_info'] = p.to_dict()
            else:
                ap_dict['project_info'] = {}
            projects.append(ap_dict)
        
        return jsonify({
            'code': 200,
            'message': 'Success',
            'data': {
                'list': projects,
                'total': pagination.total,
                'page': page,
                'page_size': page_size
            }
        })
    except Exception as e:
        log_info(f"Get projects error: {str(e)}")
        return jsonify({'code': 500, 'message': str(e)}), 500

def _process_account_data_saving(project_id, process_name, test_steps):
    try:
        # Get project to know products
        project = AutomationProject.query.get(project_id)
        if not project or not project.product_ids:
            return

        # Get all products for this project
        p_ids_raw = project.product_ids
        p_ids = []
        if isinstance(p_ids_raw, str):
            try:
                # Try to parse as JSON list first (e.g. ["SC", "Other"])
                parsed = json.loads(p_ids_raw)
                if isinstance(parsed, list):
                    p_ids = [str(i).strip() for i in parsed if i]
                else:
                    p_ids = [str(parsed).strip()]
            except:
                # Fallback to comma separated string
                p_ids = [i.strip() for i in p_ids_raw.split(',') if i.strip()]
        
        if not p_ids:
            return
            
        products = Project.query.filter(Project.id.in_(p_ids)).all()
        
        # Map URL -> Product Name
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
                    # Store both normalized (strip slash) and raw
                    url_to_product_name[addr.strip()] = p.product_package_name
                    url_to_product_name[addr.strip().rstrip('/')] = p.product_package_name

        # Calculate file name
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

# Helper functions for file generation
def generate_test_case_path(automation_project):
    """
    Generate test case file path based on naming convention:
    {product_id}_{system_type}_test_{index}.py
    e.g. SC_Web_test.py, SC_Web_test_2.py
    """
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    test_case_dir = os.path.join(root_path, 'Test_Case')
    if not os.path.exists(test_case_dir):
        os.makedirs(test_case_dir)
        
    # 1. Determine Product Code and System Type
    product_code = "Unknown"
    system_type = "Web" # Default
    
    # Get linked Project
    linked_project = None
    if automation_project.project_id:
        linked_project = Project.query.get(automation_project.project_id)
    
    if linked_project:
        if linked_project.product_id:
            product_code = linked_project.product_id
        if linked_project.system_type:
            system_type = linked_project.system_type
    
    # Fallback from automation_project if needed
    if product_code == "Unknown" and automation_project.product_ids:
        try:
            ids = json.loads(automation_project.product_ids)
            if ids:
                product_code = ids[0]
        except:
            pass
            
    if automation_project.system:
        system_type = automation_project.system
        
    # Sanitize
    def sanitize(s):
        return "".join([c for c in s if c.isalnum() or c in ('_',)]).strip()
    
    product_code = sanitize(product_code)
    system_type = sanitize(system_type)
    
    base_name = f"{product_code}_{system_type}_test"
    
    # 2. Check if this project already has a compliant file in DB
    # This prevents renaming existing files that already follow the pattern
    existing_record = ProjectFile.query.filter_by(project_id=automation_project.id).first()
    
    if existing_record and existing_record.file_path:
        file_name = os.path.basename(existing_record.file_path)
        name_part = os.path.splitext(file_name)[0]
        
        # Check matching: starts with base_name, and remainder is empty or _\d+
        if name_part.startswith(base_name):
            suffix = name_part[len(base_name):]
            if suffix == "" or (suffix.startswith("_") and suffix[1:].isdigit()):
                # It's already compliant, return it to avoid renaming
                abs_path = existing_record.file_path
                if not os.path.isabs(abs_path):
                    abs_path = os.path.join(root_path, abs_path)
                
                # Rel path
                rel_path = existing_record.file_path
                if os.path.isabs(rel_path):
                     try:
                         rel_path = os.path.relpath(abs_path, root_path)
                     except:
                         rel_path = os.path.join('Test_Case', file_name)
                
                return abs_path, rel_path

    # 3. Generate New Name
    # List all files to find max index
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
    rel_path = os.path.join('Test_Case', new_name)
    return abs_path, rel_path



@celery.task(bind=True)
def run_test_execution(self, execution_id, project_id):
    """Run test execution as a Celery task"""
    # 设置当前执行ID，以便将日志写入数据库 detailed_log 字段
    set_current_execution_id(execution_id)
    log_info(f"开始执行Celery任务: execution_id={execution_id}, project_id={project_id}")
    
    try:
        execution = AutomationExecution.query.get(execution_id)
        project = AutomationProject.query.get(project_id)
        
        if not execution or not project:
            log_info("Execution or Project not found")
            return

        # 查找测试文件路径
        project_file = ProjectFile.query.filter_by(project_id=project_id).first()
        file_path = None
        
        # 计算项目根目录 (backend)
        # 当前文件在 backend/routes/AutomationPlatform/WebAutomation/
        root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        if project_file:
            if os.path.exists(project_file.file_path):
                file_path = project_file.file_path
            elif not os.path.isabs(project_file.file_path):
                # 尝试相对路径
                candidate = os.path.join(root_path, project_file.file_path)
                if os.path.exists(candidate):
                    file_path = candidate
        
        if not file_path:
            # Fallback: 尝试在 Test_Case 目录下查找
            test_case_dir = os.path.join(root_path, 'Test_Case')
            if os.path.exists(test_case_dir):
                # 尝试查找以 project_id 开头的 py 文件
                for f in os.listdir(test_case_dir):
                    if f.startswith(f"{project_id}_") and f.endswith(".py"):
                        file_path = os.path.join(test_case_dir, f)
                        break
        
        if not file_path:
            raise Exception(f"找不到项目 {project_id} 的测试文件")

        log_info(f"找到测试文件: {file_path}")

        # 构建 pytest 命令
        # 指定执行 test_concurrent_independent_browsers 方法
        target = f"{file_path}::test_concurrent_independent_browsers"
        cmd = [sys.executable, '-m', 'pytest', target, '-v', '-s']
        
        # 准备环境变量
        env = os.environ.copy()
        env['AUTOMATION_EXECUTION_ID'] = str(execution_id)
        env['PROJECT_ID'] = str(project_id)
        env['SERVICE_HOST'] = os.environ.get('SERVICE_HOST', '127.0.0.1')
        env['SERVICE_PORT'] = os.environ.get('SERVICE_PORT', '5000')
        # 强制 Python 子进程使用 UTF-8 编码进行 I/O，避免中文乱码
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # 添加项目根目录到 PYTHONPATH
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{root_path}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = root_path
            
        log_info(f"执行命令: {' '.join(cmd)}")
        
        # 执行子进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            # text=True,      # 移除文本模式，获取字节流以处理潜在的编码问题
            # encoding='utf-8',
            cwd=root_path # 在 backend 目录下执行
        )
        
        # 等待执行完成并获取输出
        stdout_bytes, _ = process.communicate()
        return_code = process.returncode
        
        # 尝试解码输出，处理潜在的编码错误
        try:
            stdout = stdout_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Windows 下常见的回退编码
                stdout = stdout_bytes.decode('gbk')
            except UnicodeDecodeError:
                # 如果都失败了，使用 ignore 或 replace
                stdout = stdout_bytes.decode('utf-8', errors='replace')

        # 将 pytest 输出打印到日志文件，方便调试
        if stdout:
            log_info(f"Pytest Output for execution {execution_id}:\n{stdout}")
            
        result = 'Passed' if return_code == 0 else 'Failed'
        log_info(f"任务执行完成，结果: {result}, 返回码: {return_code}")
        
        # 更新执行记录
        execution.status = result
        execution.end_time = datetime.now()
        execution.log_message = '测试执行成功' if result == 'Passed' else '测试执行失败'
        
        # 将控制台输出追加到详细日志
        header = f"\n\n{'='*20} Console Output {'='*20}\n"
        if execution.detailed_log:
            execution.detailed_log = execution.detailed_log + header + stdout
        else:
            execution.detailed_log = header + stdout
            
        if project:
            project.status = result
            project.updated_at = datetime.now()
            
        db.session.commit()
        log_info(f"Celery任务 {execution_id} 数据库更新成功: {result}")
            
    except Exception as e:
        log_info(f"Celery任务执行异常 (execution_id={execution_id}): {str(e)}")
        # 尝试更新状态为失败
        try:
            execution = AutomationExecution.query.get(execution_id)
            if execution:
                execution.status = 'Failed'
                execution.log_message = str(e)
                execution.end_time = datetime.now()
                
            # 同时更新项目状态为 Failed
            project = AutomationProject.query.get(project_id)
            if project:
                project.status = 'Failed'
                project.updated_at = datetime.now()
                
            db.session.commit()
        except Exception as update_error:
            log_info(f"更新失败状态时发生错误: {str(update_error)}")
    finally:
        # 清除当前执行ID
        clear_current_execution_id()

@automation_management_bp.route('/test_projects', methods=['POST'])
def create_project():
    try:
        data = request.json
        log_info(f"接收到创建项目请求: {data.get('process_name')}")
        
        product_ids = data.get('product_ids')
        cleaned_ids = []
        if isinstance(product_ids, list):
            for item in product_ids:
                if isinstance(item, dict):
                    cleaned_ids.append(str(item.get('id', '')))
                else:
                    cleaned_ids.append(str(item))
            # Remove empty strings
            cleaned_ids = [i for i in cleaned_ids if i]
            # Save as JSON string ["SC"] instead of comma separated "SC"
            product_ids = json.dumps(cleaned_ids, ensure_ascii=False)
        elif product_ids is None:
            product_ids = json.dumps([], ensure_ascii=False)
            
        # Ensure project_id is correct. If missing, try to find it from product_ids
        project_id = data.get('project_id')
        if not project_id and cleaned_ids:
            # Try to find project_id from the first product_id
            first_val = cleaned_ids[0]
            related_project = None
            
            # 1. Try treating it as a primary key ID (int)
            if first_val.isdigit():
                related_project = Project.query.get(int(first_val))
            
            # 2. If not found, try matching by product_id string (e.g. "SC")
            if not related_project:
                related_project = Project.query.filter_by(product_id=first_val).first()
                
            # 3. If still not found, try matching by package name
            if not related_project:
                 related_project = Project.query.filter_by(product_package_name=first_val).first()

            if related_project:
                project_id = related_project.id
                log_info(f"Auto-detected project_id={project_id} from product_id/key={first_val}")
            else:
                log_info(f"Could not auto-detect project_id from {first_val}")

        # Serialize complex fields
        test_steps_data = data.get('test_steps')
        test_steps_str = json.dumps(test_steps_data, ensure_ascii=False) if test_steps_data else None
        
        tab_switch_config = data.get('tab_switch_config')
        if isinstance(tab_switch_config, (dict, list)):
            tab_switch_config = json.dumps(tab_switch_config, ensure_ascii=False)
            
        assertion_config = data.get('assertion_config')
        if isinstance(assertion_config, (dict, list)):
            assertion_config = json.dumps(assertion_config, ensure_ascii=False)
            
        screenshot_config = data.get('screenshot_config')
        if isinstance(screenshot_config, (dict, list)):
            screenshot_config = json.dumps(screenshot_config, ensure_ascii=False)
            
        product_package_names = data.get('product_package_names')
        if isinstance(product_package_names, list):
            product_package_names = json.dumps(product_package_names, ensure_ascii=False)

        new_project = AutomationProject(
            process_name=data.get('process_name'),
            product_ids=product_ids,
            system=data.get('system'),
            product_type=data.get('product_type'),
            environment=data.get('environment'),
            product_address=data.get('product_address'),
            project_id=project_id,
            product_package_names=product_package_names,
            test_steps=test_steps_str,
            tab_switch_config=tab_switch_config,
            assertion_config=assertion_config,
            screenshot_config=screenshot_config,
            status='待执行',
            created_by=data.get('created_by', 'admin')
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        # 创建测试文件Content
        try:
            # Process account data for YAML
            if test_steps_data:
                _process_account_data_saving(new_project.id, new_project.process_name, test_steps_data)

            file_path, rel_path = generate_test_case_path(new_project)
            
            # Generate intelligent test code using TestCodeGenerator
            try:
                project_data_for_gen = {
                    'process_name': new_project.process_name,
                    'product_ids': new_project.product_ids,
                    'product_address': new_project.product_address,
                    'test_steps': test_steps_data
                }
                generated_code = TestCodeGenerator.generate_full_test_code(project_data_for_gen)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(generated_code)
                log_info(f"Generated test code for project {new_project.id} at {file_path}")
            except Exception as e:
                log_info(f"Error generating test code: {str(e)}")
                # Fallback: write error to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Code generation failed: {str(e)}\n")
                
            # Create ProjectFile record
            new_file = ProjectFile(
                project_id=new_project.id,
                project_name=new_project.process_name,
                file_name=os.path.basename(file_path),
                file_path=rel_path,
                file_type='py'
            )
            db.session.add(new_file)
            db.session.commit()
        except Exception as e:
            log_info(f"Failed to create test file: {str(e)}")
            # Don't fail the request, just log it
        
        # Return dict with original list/dict data for frontend
        resp_data = new_project.to_dict()
        resp_data['test_steps'] = test_steps_data
        if tab_switch_config: resp_data['tab_switch_config'] = data.get('tab_switch_config')
        if assertion_config: resp_data['assertion_config'] = data.get('assertion_config')
        if screenshot_config: resp_data['screenshot_config'] = data.get('screenshot_config')
        
        return jsonify({'code': 200, 'message': '项目创建成功', 'data': resp_data})
    except Exception as e:
        db.session.rollback()
        log_info(f"Create project error: {str(e)}")
        return jsonify({'code': 500, 'message': str(e)}), 500

@automation_management_bp.route('/test_projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    try:
        project = AutomationProject.query.get(project_id)
        if not project:
            return jsonify({'code': 404, 'message': '项目未找到'}), 404
            
        data = request.json
        
        if 'process_name' in data: project.process_name = data['process_name']
        if 'product_ids' in data:
            p_ids = data['product_ids']
            cleaned_ids = []
            if isinstance(p_ids, list):
                for item in p_ids:
                    if isinstance(item, dict):
                        cleaned_ids.append(str(item.get('id', '')))
                    else:
                        cleaned_ids.append(str(item))
                # Remove empty strings
                cleaned_ids = [i for i in cleaned_ids if i]
                # Save as JSON string ["SC"]
                project.product_ids = json.dumps(cleaned_ids, ensure_ascii=False)
            elif p_ids is None:
                project.product_ids = json.dumps([], ensure_ascii=False)
            else:
                # Handle direct string assignment if any
                project.product_ids = p_ids
        if 'system' in data: project.system = data['system']
        if 'product_type' in data: project.product_type = data['product_type']
        if 'environment' in data: project.environment = data['environment']
        if 'product_address' in data: project.product_address = data['product_address']
        if 'project_id' in data: project.project_id = data['project_id']
        if 'product_package_names' in data:
            names = data['product_package_names']
            if isinstance(names, list):
                project.product_package_names = json.dumps(names, ensure_ascii=False)
            else:
                project.product_package_names = names
                
        if 'test_steps' in data:
            steps = data['test_steps']
            if isinstance(steps, (list, dict)):
                project.test_steps = json.dumps(steps, ensure_ascii=False)
            else:
                project.test_steps = steps
                
        if 'tab_switch_config' in data:
            conf = data['tab_switch_config']
            if isinstance(conf, (list, dict)):
                project.tab_switch_config = json.dumps(conf, ensure_ascii=False)
            else:
                project.tab_switch_config = conf
                
        if 'assertion_config' in data:
            conf = data['assertion_config']
            if isinstance(conf, (list, dict)):
                project.assertion_config = json.dumps(conf, ensure_ascii=False)
            else:
                project.assertion_config = conf
                
        if 'screenshot_config' in data:
            conf = data['screenshot_config']
            if isinstance(conf, (list, dict)):
                project.screenshot_config = json.dumps(conf, ensure_ascii=False)
            else:
                project.screenshot_config = conf
        
        db.session.commit()
        
        # Ensure file exists and is up-to-date
        try:
            project_file = ProjectFile.query.filter_by(project_id=project_id).first()
            target_path, target_rel_path = generate_test_case_path(project)
            
            # Prepare generation data
            test_steps_list = []
            if project.test_steps:
                try:
                    test_steps_list = json.loads(project.test_steps) if isinstance(project.test_steps, str) else project.test_steps
                except:
                    test_steps_list = []

            gen_data = {
                'process_name': project.process_name,
                'product_ids': project.product_ids,
                'product_address': project.product_address,
                'test_steps': test_steps_list
            }
            
            # Generate code
            code = TestCodeGenerator.generate_full_test_code(gen_data)
            
            # Write file (always overwrite to ensure it matches DB)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(code)
                
            # Update or Create ProjectFile record
            if not project_file:
                 new_file = ProjectFile(
                    project_id=project.id,
                    project_name=project.process_name,
                    file_name=os.path.basename(target_path),
                    file_path=target_rel_path,
                    file_type='py'
                )
                 db.session.add(new_file)
            else:
                 project_file.file_name = os.path.basename(target_path)
                 project_file.file_path = target_rel_path
                     
            db.session.commit()
        except Exception as e:
            log_info(f"Failed to update test file: {str(e)}")

        resp_data = project.to_dict()
        # Deserialize fields if they are strings
        for field in ['test_steps', 'tab_switch_config', 'assertion_config', 'screenshot_config', 'product_package_names']:
            val = resp_data.get(field)
            if isinstance(val, str):
                try:
                    resp_data[field] = json.loads(val)
                except:
                    pass

        return jsonify({'code': 200, 'message': 'Project updated successfully', 'data': resp_data})
    except Exception as e:
        db.session.rollback()
        log_info(f"Update project error: {str(e)}")
        return jsonify({'code': 500, 'message': str(e)}), 500


@automation_management_bp.route('/test_projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        project = AutomationProject.query.get(project_id)
        if not project:
            return jsonify({'code': 404, 'message': '项目未找到'}), 404
            
        # 0. Delete associated execution records and their logs
        try:
            executions = AutomationExecution.query.filter_by(project_id=project_id).all()
            for execution in executions:
                # Delete method logs linked to this execution
                AutomationExecutMethodLog.query.filter_by(execution_id=execution.id).delete()
                # Delete the execution record itself
                db.session.delete(execution)
        except Exception as e:
            log_info(f"Error deleting execution records for project {project_id}: {str(e)}")

        # 1. Delete associated test file
        try:
            # Check ProjectFile record
            project_file = ProjectFile.query.filter_by(project_id=project_id).first()
            
            # Paths to check for deletion
            paths_to_check = []
            
            if project_file and project_file.file_path:
                paths_to_check.append(project_file.file_path)
                # Also check absolute path if stored path is relative
                if not os.path.isabs(project_file.file_path):
                     root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                     paths_to_check.append(os.path.join(root_path, project_file.file_path))
            
            # Also try to guess the path using standard naming convention
            generated_path, _ = generate_test_case_path(project)
            paths_to_check.append(generated_path)
            
            # Remove duplicates and filter existing files
            unique_paths = list(set(paths_to_check))
            
            for path in unique_paths:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                        log_info(f"Deleted test file: {path}")
                    except Exception as fe:
                        log_info(f"Failed to delete file {path}: {str(fe)}")
            
            # Delete ProjectFile record if exists
            if project_file:
                db.session.delete(project_file)
                
        except Exception as e:
            log_info(f"Error during file deletion for project {project_id}: {str(e)}")
            # Don't block project deletion if file deletion fails

        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '项目已删除'})
    except Exception as e:
        db.session.rollback()
        log_info(f"Delete project error: {str(e)}")
        return jsonify({'code': 500, 'message': str(e)}), 500

@automation_management_bp.route('/test_projects/<int:project_id>/execute', methods=['POST'])
def execute_project(project_id):
    try:
        log_info(f"收到项目执行请求: project_id={project_id}")
        project = AutomationProject.query.get(project_id)
        if not project:
            log_info(f"项目不存在: project_id={project_id}")
            return jsonify({'code': 404, 'message': '项目未找到'}), 404
            
        # Create execution record
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
            executed_by='admin', # Should get from user session
            log_message='正在执行',
            detailed_log=f"收到项目执行请求: project_id={project_id}\n"
        )
        
        db.session.add(execution)
        project.status = 'Running'
        db.session.commit()
        
        # Trigger Celery task
        task = run_test_execution.apply_async(args=[execution.id, project.id])
        
        # Save task_id to database for recovery
        execution.task_id = task.id
        db.session.commit()
        
        log_info(f"Celery异步任务已提交: task_id={task.id}, execution_id={execution.id}")
        
        return jsonify({'code': 200, 'message': '执行已启动', 'data': {'execution_id': execution.id, 'task_id': task.id}})
    except Exception as e:
        db.session.rollback()
        log_info(f"项目执行请求异常: {str(e)}")
        return jsonify({'code': 500, 'message': str(e)}), 500

@automation_management_bp.route('/test_projects/<int:project_id>/cancel', methods=['POST'])
def cancel_execution(project_id):
    try:
        # Find running executions for this project
        execution = AutomationExecution.query.filter_by(
            project_id=project_id, 
            status='Running'
        ).order_by(AutomationExecution.start_time.desc()).first()
        
        if execution:
            execution.status = 'Cancelled'
            execution.end_time = datetime.now()
            execution.log_message += '\n执行已取消'
            
        project = AutomationProject.query.get(project_id)
        if project:
            project.status = 'Cancelled'
            
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '执行已取消'})
    except Exception as e:
        db.session.rollback()
        log_info(f"Cancel execution error: {str(e)}")
        return jsonify({'code': 500, 'message': str(e)}), 500

@automation_management_bp.route('/executions', methods=['GET'])
def get_executions():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        project_id = request.args.get('project_id', type=int)
        
        query = AutomationExecution.query
        if project_id:
            query = query.filter_by(project_id=project_id)
            
        pagination = query.order_by(AutomationExecution.start_time.desc()).paginate(
            page=page, per_page=page_size, error_out=False
        )
        
        executions = []
        for exe in pagination.items:
            executions.append({
                'id': exe.id,
                'process_name': exe.process_name,
                'status': exe.status,
                'start_time': exe.start_time.strftime('%Y-%m-%d %H:%M:%S') if exe.start_time else None,
                'end_time': exe.end_time.strftime('%Y-%m-%d %H:%M:%S') if exe.end_time else None,
                'executed_by': exe.executed_by
            })
            
        return jsonify({
            'code': 200, 
            'message': '执行记录列表获取成功', 
            'data': {
                'list': executions,
                'total': pagination.total,
                'page': page,
                'page_size': page_size
            }
        })
    except Exception as e:
        log_info(f"Get executions list error: {str(e)}")
        return jsonify({'code': 500, 'message': str(e)}), 500

@automation_management_bp.route('/executions/<int:execution_id>', methods=['GET'])
def get_execution_detail(execution_id):
    try:
        # Use filter_by instead of get to avoid potential issues with primary key types or session state
        execution = AutomationExecution.query.filter_by(id=execution_id).first()
        if not execution:
            log_info(f"Execution not found: {execution_id}")
            return jsonify({'code': 404, 'message': f'执行记录未找到 (ID: {execution_id})'}), 404
            
        # Check if status is 'Running' and task_id exists - Check Celery status
        if execution.status == 'Running' and execution.task_id:
            try:
                res = AsyncResult(execution.task_id)
                log_info(f"Checking Celery task status for execution {execution_id}: {res.status}")
                
                if res.status in ['SUCCESS', 'FAILURE', 'REVOKED']:
                    # 任务结束但是数据库状态未更新 (可能是worker崩溃或网络问题)
                    if res.status == 'SUCCESS':
                         # Celery 任务成功, 但数据库状态可能未更新task
                         # # 在我们的 run_test_execution 中，我们更新数据库。如果我们在这里，数据库更新可能会失败。
                         # 仅从任务状态中我们无法得知确切的测试结果，除非我们将其存储在 result 中。
                         # 但 run_test_execution 不返回结果，它返回 None。
                         # 假设任务成功但数据库正在运行 -> 可能刚刚完成或数据库写入失败。
                         # 如果数据库更新了，我们就相信它的内容。但这里的状态是正在运行。
                         
                         # 如果无法恢复，则强制更新状态为失败，或者检查 date_done
                         execution.status = 'Completed' # Or 'Unknown'
                         execution.log_message += '\n(系统检测到后台任务已结束，但状态未同步)'
                    elif res.status == 'FAILURE':
                        execution.status = 'Error'
                        execution.log_message += f'\n(后台任务异常: {str(res.result)})'
                    if res.date_done:
                        done_time = res.date_done
                        if isinstance(done_time, str):
                            try:
                                done_time = datetime.fromisoformat(done_time)
                            except:
                                done_time = datetime.now()
                        
                        # 处理时区问题：Celery 存储的 date_done 可能是 UTC
                        # 如果是 naive 时间 (无时区信息)，且用户反馈少8小时，则默认为 UTC，需 +8 小时
                        if done_time.tzinfo is None:
                             done_time = done_time + timedelta(hours=8)
                        else:
                             # 如果有时区信息，转换为本地时间 (假设服务器运行在 Asia/Shanghai 或需要移除 tzinfo)
                             # 简单处理：转为 naive local time
                             import pytz
                             shanghai_tz = pytz.timezone('Asia/Shanghai')
                             done_time = done_time.astimezone(shanghai_tz).replace(tzinfo=None)
                        
                        execution.end_time = done_time
                    else:
                        execution.end_time = datetime.now()
                        
                    db.session.commit()
                    log_info(f"Synced execution {execution_id} status from Celery: {execution.status}")
            except Exception as e:
                log_info(f"Failed to check Celery status: {e}")

        # Parse logs
        detailed_log_content = execution.detailed_log or ""
        parsed_log = UitilTools.parse_automation_log(detailed_log_content)
        
        # Get Method Logs
        method_logs_records = AutomationExecutMethodLog.query.filter_by(execution_id=execution_id).all()
        method_logs_data = []
        for record in method_logs_records:
            method_logs_data.append({
                'name': record.method_name,
                'logs': UitilTools.parse_automation_log(record.log_content)
            })

        # 提取错误日志 (Pytest Output)
        error_log = None
        if detailed_log_content:
            console_output_marker = f"\n\n{'='*20} Console Output {'='*20}\n"
            if console_output_marker in detailed_log_content:
                # 提取控制台输出部分
                console_output = detailed_log_content.split(console_output_marker)[1]
                
                # 查找 FAILURES 或 ERRORS 区域
                if "FAILURES" in console_output or "ERRORS" in console_output:
                     # 简单地将整个控制台输出作为错误日志，或者可以更精细地提取
                     # 这里我们提取从 FAILURES/ERRORS 开始的内容
                     import re
                     match = re.search(r'(={10,}\s+(FAILURES|ERRORS)\s+={10,}[\s\S]*)', console_output)
                     if match:
                         error_content = match.group(1)
                         
                         # 进一步过滤：移除标准日志行 (包含 INFO 且符合时间戳格式的行)
                         # 格式如: 2026-02-02 14:29:07 - 星火:  - INFO - ...
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
                         # 如果没匹配到标准格式但有 Console Output，也可以作为兜底
                         # 同样应用过滤逻辑
                         filtered_lines = []
                         log_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+-\s+.*?\s+-\s+INFO\s+-')
                         for line in console_output.split('\n'):
                             if not log_pattern.match(line.strip()):
                                 filtered_lines.append(line)
                                 
                         error_log = {
                             'name': '错误日志',
                             'logs': UitilTools.parse_automation_log('\n'.join(filtered_lines), is_error_log=True)
                         }
        
        # 将错误日志添加到 method_logs_data 的最后
        if error_log:
            method_logs_data.append(error_log)
            
        # 兼容历史数据：如果 method_logs_data 为空，尝试从 detailed_log 解析测试文件分析结果
        test_methods_count = 0
        if method_logs_data:
            test_methods_count = len(method_logs_data)
        else:
            # 尝试解析 "测试文件分析结果: {'test_methods': ...}"
            try:
                import re
                import ast
                match = re.search(r'测试文件分析结果:\s*(\{.*?\})', detailed_log_content)
                if match:
                    analysis_result = ast.literal_eval(match.group(1))
                    if isinstance(analysis_result, dict) and 'test_methods' in analysis_result:
                        methods = analysis_result['test_methods']
                        # 剔除公共方法
                        filtered_methods = [m for m in methods if m != 'test_concurrent_independent_browsers']
                        test_methods_count = len(filtered_methods)
            except Exception as e:
                log_info(f"Failed to parse legacy test methods: {e}")
                # Fallback to existing logic if parsing fails
                test_methods_count = len(set(s.get('method') for s in parsed_log.get('testSteps', []) if s.get('method')))

        return jsonify({
            'code': 200,
            'message': '获取执行详情成功',
            'data': {
                'id': execution.id,
                'status': execution.status,
                'detailed_log': execution.detailed_log,
                'logs': parsed_log,  # Parsed detailed logs
                'method_logs': method_logs_data, # Parsed method logs
                'stats': {
                    'test_steps_count': len(parsed_log.get('testSteps', [])),
                    'test_methods_count': test_methods_count,
                    'screenshots_count': detailed_log_content.count('Screenshot saved at'),
                    'keyword_data_count': sum(len(step.get('logs', [])) for step in parsed_log.get('testSteps', []))
                }
            }
        })
        
    except Exception as e:
        log_info(f"Get execution detail error: {str(e)}")
        # Return specific error message for easier debugging
        return jsonify({'code': 500, 'message': f'获取执行记录详情时发生错误: {str(e)}'}), 500

@automation_management_bp.route('/image', methods=['GET'])
def get_image():
    try:
        file_path = request.args.get('path')
        if not file_path:
            return jsonify({'code': 400, 'message': '路径是必填项'}), 400
            
        if not os.path.exists(file_path):
            return jsonify({'code': 404, 'message': '文件未找到'}), 404
            
        return send_file(file_path)
    except Exception as e:
        log_info(f"Get image error: {str(e)}")
        return jsonify({'code': 500, 'message': '获取图片时发生错误'}), 500

# Test Connection API
@automation_management_bp.route('/test_connection', methods=['POST'])
def test_connection():
    try:
        data = request.json
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'code': 400, 'message': '请提供要测试的URL'}), 400
            
        results = []
        for url in urls:
            status = 'failed'
            message = ''
            try:
                # Add scheme if missing
                target_url = url
                if not target_url.startswith('http'):
                    target_url = 'http://' + target_url
                    
                response = requests.get(target_url, timeout=5)
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
            
        return jsonify({'code': 200, 'message': '测试连接成功', 'data': results})
    except Exception as e:
        return jsonify({'code': 500, 'message': '测试连接时发生错误'}), 500

# Code Management API - Get Code
@automation_management_bp.route('/code/get', methods=['GET'])
def get_code():
    try:
        project_id = request.args.get('project_id')
        requested_file_path = request.args.get('file_path')
        
        if not project_id:
            return jsonify({'code': 400, 'message': '项目ID是必填项'}), 400
            
        # Find associated file
        project_file = ProjectFile.query.filter_by(project_id=project_id, is_active=True).first()
        project = AutomationProject.query.get(project_id)
        
        log_info(f"Get code for project {project_id}")
        
        file_content = ""
        file_path = ""
        
        # Priority 1: Use requested file path if provided (security check needed)
        if requested_file_path:
             # Basic security check: ensure it's within project bounds or is a valid absolute path
             # For now, we trust the path if it exists and looks like a python file
             if os.path.exists(requested_file_path) and requested_file_path.endswith('.py'):
                 file_path = requested_file_path
        
        # Priority 2: Use recorded ProjectFile path
        if not file_path and project_file:
            # Check if file exists at the recorded path
            if os.path.exists(project_file.file_path):
                file_path = project_file.file_path
            else:
                # Try to resolve relative path or fix path issues
                # 1. Try relative to project backend root
                root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                candidate_path = os.path.join(root_path, project_file.file_path)
                
                if os.path.exists(candidate_path):
                    file_path = candidate_path
                else:
                    # 2. Try looking in Test_Case directory with just the filename
                    filename = os.path.basename(project_file.file_path)
                    test_case_dir = os.path.join(root_path, 'Test_Case')
                    candidate_path = os.path.join(test_case_dir, filename)
                    
                    if os.path.exists(candidate_path):
                        file_path = candidate_path

            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            else:
                return jsonify({
                    'code': 404, 
                    'message': '测试文件未找到，请先创建或保存项目以生成测试文件。',
                    'data': {
                        'file_path': project_file.file_path,
                        'file_name': os.path.basename(project_file.file_path)
                    }
                }), 404
        else:
            # Try to guess path but do not create
            root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            test_case_dir = os.path.join(root_path, 'Test_Case')
            
            file_name = f"{project_id}_{project.process_name}.py" if project else f"{project_id}_test.py"
            # Sanitize filename
            file_name = "".join([c for c in file_name if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).strip()
            file_path = os.path.join(test_case_dir, file_name)
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            else:
                return jsonify({
                    'code': 404, 
                    'message': '测试文件未找到，请先创建或保存项目以生成测试文件。',
                    'data': {
                        'file_path': file_path,
                        'file_name': file_name
                    }
                }), 404

        return jsonify({
            'code': 200, 
            'message': '测试代码获取成功', 
            'data': {
                'content': file_content,
                'file_path': file_path
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': '获取测试代码时发生错误'}), 500

# Code Management API - Save Code
@automation_management_bp.route('/code/save', methods=['POST'])
def save_code():
    try:
        data = request.json
        project_id = data.get('project_id')
        content = data.get('content')
        # Optional: file_path from frontend, or generate it
        file_path = data.get('file_path')
        
        if not project_id or content is None:
            return jsonify({'code': 400, 'message': '项目ID和测试代码内容是必填项'}), 400
            
        project = AutomationProject.query.get(project_id)
        project_file = ProjectFile.query.filter_by(project_id=project_id).first()
        
        # Determine file path if not provided
        if not file_path:
            if project_file:
                file_path = project_file.file_path
            else:
                if project:
                    generated_abs, _ = generate_test_case_path(project)
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
            project_file.file_path = file_path
            project_file.updated_at = datetime.now()
        else:
            file_name = os.path.basename(file_path)
            new_file = ProjectFile(
                project_id=project_id,
                project_name=project.process_name if project else 'Unknown',
                file_name=file_name,
                file_path=file_path,
                file_type='py'
            )
            db.session.add(new_file)
            
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '测试代码保存成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': '保存测试代码时发生错误'}), 500
