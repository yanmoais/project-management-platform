from flask import Blueprint, jsonify, request
from backend.models import db, TestEnvironment, TestEnvironmentLog
from backend.utils.LogManeger import log_info
from datetime import datetime

environment_bp = Blueprint('environment_bp', __name__)

# List
@environment_bp.route('/list', methods=['GET'])
def get_list():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    project_name = request.args.get('projectName', '')
    env_type = request.args.get('envType', '')

    query = TestEnvironment.query
    if project_name:
        query = query.filter(TestEnvironment.project_name.like(f'%{project_name}%'))
    if env_type:
        query = query.filter(TestEnvironment.env_type == env_type)
    
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    data = {
        'total': pagination.total,
        'rows': [item.to_dict() for item in pagination.items]
    }
    
    return jsonify({'code': 200, 'msg': 'success', 'data': data})

# Add
@environment_bp.route('/add', methods=['POST'])
def add_env():
    data = request.json
    log_info(f"添加测试环境数据为: {data}")
        
    try:
        new_env = TestEnvironment(
            project_name=data.get('project_name'),
            env_name=data.get('env_name'),
            env_type=data.get('env_type'),
            env_url=data.get('env_url'),
            db_type=data.get('db_type'),
            db_host=data.get('db_host'),
            db_port=data.get('db_port'),
            db_user=data.get('db_user'),
            db_password=data.get('db_password'),
            account=data.get('account'),
            password=data.get('password'),
            status=data.get('status', 'Active'),
            create_by=data.get('create_by')
        )
        db.session.add(new_env)
        db.session.flush() # Get ID before commit

        # Record log
        log = TestEnvironmentLog(
            env_id=new_env.env_id,
            username=data.get('create_by', 'Unknown'),
            operation_type='新增',
            change_content=f"新增测试环境: {new_env.env_name} (Project: {new_env.project_name})",
            operation_time=datetime.now()
        )
        db.session.add(log)

        db.session.commit()
        return jsonify({'code': 200, 'msg': '操作成功', 'data': None})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e), 'data': None})

# Update
@environment_bp.route('/update', methods=['PUT'])
def update_env():
    data = request.json
    env_id = data.get('env_id')
    if not env_id:
         return jsonify({'code': 400, 'msg': 'Missing env_id', 'data': None})
         
    env = TestEnvironment.query.get(env_id)
    if not env:
        return jsonify({'code': 404, 'msg': 'Environment not found', 'data': None})
        
    try:
        # Prepare change content
        changes = []
        if data.get('project_name') and data.get('project_name') != env.project_name:
            changes.append(f"项目名称: {env.project_name} -> {data.get('project_name')}")
        if data.get('env_name') and data.get('env_name') != env.env_name:
            changes.append(f"环境名称: {env.env_name} -> {data.get('env_name')}")
        if data.get('env_url') and data.get('env_url') != env.env_url:
            changes.append(f"环境地址: {env.env_url} -> {data.get('env_url')}")
        if data.get('status') and data.get('status') != env.status:
            changes.append(f"状态: {env.status} -> {data.get('status')}")
        
        change_content = "编辑环境: " + "; ".join(changes) if changes else "编辑环境 (无关键字段变更)"

        env.project_name = data.get('project_name', env.project_name)
        env.env_name = data.get('env_name', env.env_name)
        env.env_type = data.get('env_type', env.env_type)
        env.env_url = data.get('env_url', env.env_url)
        env.db_type = data.get('db_type', env.db_type)
        env.db_host = data.get('db_host', env.db_host)
        env.db_port = data.get('db_port', env.db_port)
        env.db_user = data.get('db_user', env.db_user)
        env.db_password = data.get('db_password', env.db_password)
        env.account = data.get('account', env.account)
        env.password = data.get('password', env.password)
        env.status = data.get('status', env.status)
        env.update_by = data.get('update_by')
        
        # Record log
        log = TestEnvironmentLog(
            env_id=env.env_id,
            username=data.get('update_by', 'Unknown'),
            operation_type='编辑',
            change_content=change_content,
            operation_time=datetime.now()
        )
        db.session.add(log)

        db.session.commit()
        return jsonify({'code': 200, 'msg': '操作成功', 'data': None})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e), 'data': None})

# Delete
@environment_bp.route('/delete/<int:env_id>', methods=['DELETE'])
def delete_env(env_id):
    env = TestEnvironment.query.get(env_id)
    if not env:
        return jsonify({'code': 404, 'msg': 'Environment not found', 'data': None})
        
    try:
        db.session.delete(env)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '操作成功', 'data': None})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e), 'data': None})

# Logs
@environment_bp.route('/logs/<int:env_id>', methods=['GET'])
def get_logs(env_id):
    try:
        logs = TestEnvironmentLog.query.filter_by(env_id=env_id).order_by(TestEnvironmentLog.operation_time.desc()).all()
        return jsonify({
            'code': 200, 
            'msg': 'success', 
            'data': [log.to_dict() for log in logs]
        })
    except Exception as e:
        log_info(f"Get logs error: {str(e)}")
        return jsonify({'code': 500, 'msg': str(e), 'data': None})
