from flask import Blueprint, request, jsonify
from backend.models import db, Project, EnumValue, ProjectLog, SysUser
from datetime import datetime
import os
import uuid
import jwt
from backend.config import Config
from backend.utils.LogManeger import log_info

# Define Blueprint
product_management_bp = Blueprint('product_management', __name__)

# Upload configuration
# Calculate backend directory path: .../backend
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_FOLDER = os.path.join(BACKEND_DIR, 'static', 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper for standard response
def success_response(data=None, message="Success"):
    return jsonify({'code': 200, 'message': message, 'data': data})

def error_response(message="Error", code=500):
    return jsonify({'code': code, 'message': message})

def get_current_user():
    token = request.headers.get('Authorization')
    if not token:
        return None
    try:
        if " " in token:
            token = token.split(" ")[1]
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        return SysUser.query.get(user_id)
    except Exception as e:
        log_info(f"Get user error: {str(e)}")
        return None

# 1. Get Project List
@product_management_bp.route('/projects', methods=['GET'])
def get_projects():
    try:
        # Pagination params
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        
        # Query with pagination
        query = Project.query
        
        # Filters
        product_ids = request.args.get('product_ids')
        if product_ids:
            id_list = product_ids.split(',')
            query = query.filter(Project.product_id.in_(id_list))
            
        product_names = request.args.get('product_names')
        if product_names:
            name_list = product_names.split(',')
            query = query.filter(Project.product_package_name.in_(name_list))
            
        environment = request.args.get('environment')
        if environment:
            query = query.filter(Project.environment == environment)
            
        product_address = request.args.get('product_address')
        if product_address:
            query = query.filter(Project.product_address.like(f'%{product_address}%'))

        pagination = query.order_by(Project.id.desc()).paginate(
            page=page, per_page=page_size, error_out=False
        )
        
        projects = pagination.items
        total = pagination.total
        
        # Result
        result = [p.to_dict() for p in projects]
        # log_info(result)
        return success_response({
            'list': result,
            'total': total,
            'page': page,
            'page_size': page_size
        })
    except Exception as e:
        return error_response(str(e))

@product_management_bp.route('/projects/options', methods=['GET'])
def get_project_options():
    try:
        # Get distinct product IDs and Names
        ids = db.session.query(Project.product_id).distinct().all()
        names = db.session.query(Project.product_package_name).distinct().all()
        
        return success_response({
            'product_ids': [i[0] for i in ids if i[0]],
            'product_names': [n[0] for n in names if n[0]]
        })
    except Exception as e:
        return error_response(str(e))

# 2. Create Project
@product_management_bp.route('/projects', methods=['POST'])
def create_project():
    try:
        data = request.json
        new_project = Project(
            product_package_name=data.get('product_package_name'),
            product_id=data.get('product_id'),
            system_type=data.get('system_type'),
            product_type=data.get('product_type'),
            environment=data.get('environment'),
            product_address=data.get('product_address'),
            is_automated=data.get('is_automated', '待接入'),
            version_number=data.get('version_number'),
            product_image=data.get('product_image'),
            remarks=data.get('remarks')
        )
        db.session.add(new_project)
        db.session.commit()

        # Log
        try:
            current_user = get_current_user()
            if current_user:
                log = ProjectLog(
                    project_id=new_project.id,
                    user_id=current_user.user_id,
                    username=current_user.nickname or current_user.username,
                    operation_type='新增',
                    change_content=f"新增产品: {new_project.product_package_name}",
                    operation_ip=request.remote_addr
                )
                db.session.add(log)
                db.session.commit()
        except Exception as log_e:
            log_info(f"Failed to create log: {str(log_e)}")

        return success_response(new_project.to_dict(), "Project created successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

# 3. Update Project
@product_management_bp.route('/projects/<int:id>', methods=['PUT'])
def update_project(id):
    try:
        project = Project.query.get(id)
        if not project:
            return error_response("Project not found", 404)
        
        data = request.json
        updated_fields = []

        if 'product_package_name' in data and data['product_package_name'] != project.product_package_name:
            project.product_package_name = data['product_package_name']
            updated_fields.append('产品包名')
        if 'product_id' in data and data['product_id'] != project.product_id:
            project.product_id = data['product_id']
            updated_fields.append('产品ID')
        if 'system_type' in data and data['system_type'] != project.system_type:
            project.system_type = data['system_type']
            updated_fields.append('系统类型')
        if 'product_type' in data and data['product_type'] != project.product_type:
            project.product_type = data['product_type']
            updated_fields.append('产品类型')
        if 'environment' in data and data['environment'] != project.environment:
            project.environment = data['environment']
            updated_fields.append('环境')
        if 'product_address' in data and data['product_address'] != project.product_address:
            project.product_address = data['product_address']
            updated_fields.append('产品地址')
        if 'is_automated' in data and data['is_automated'] != project.is_automated:
            project.is_automated = data['is_automated']
            updated_fields.append('是否自动化')
        if 'version_number' in data and data['version_number'] != project.version_number:
            project.version_number = data['version_number']
            updated_fields.append('版本号')
        if 'product_image' in data and data['product_image'] != project.product_image:
            project.product_image = data['product_image']
            updated_fields.append('产品图片')
        if 'remarks' in data and data['remarks'] != project.remarks:
            project.remarks = data['remarks']
            updated_fields.append('备注')
        
        db.session.commit()

        # Log
        if updated_fields:
            try:
                current_user = get_current_user()
                if current_user:
                    log = ProjectLog(
                        project_id=project.id,
                        user_id=current_user.user_id,
                        username=current_user.nickname or current_user.username,
                        operation_type='编辑',
                        change_content=f"修改字段: {', '.join(updated_fields)}",
                        operation_ip=request.remote_addr
                    )
                    db.session.add(log)
                    db.session.commit()
            except Exception as log_e:
                log_info(f"Failed to create log: {str(log_e)}")

        return success_response(project.to_dict(), "Project updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

# 4. Delete Project
@product_management_bp.route('/projects/<int:id>', methods=['DELETE'])
def delete_project(id):
    try:
        project = Project.query.get(id)
        if not project:
            return error_response("Project not found", 404)
        
        db.session.delete(project)
        db.session.commit()
        return success_response(message="Project deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

# 6. Get Enum Values
@product_management_bp.route('/enums/<field_name>', methods=['GET'])
def get_enums(field_name):
    try:
        enums = EnumValue.query.filter_by(field_name=field_name).all()
        return success_response([e.field_value for e in enums])
    except Exception as e:
        return error_response(str(e))

# 7. Add Enum Value
@product_management_bp.route('/enums', methods=['POST'])
def add_enum():
    try:
        data = request.json
        field_name = data.get('field_name')
        field_value = data.get('field_value')
        
        if not field_name or not field_value:
            return error_response("Field name and value are required", 400)
            
        exists = EnumValue.query.filter_by(field_name=field_name, field_value=field_value).first()
        if exists:
             return success_response(message="Enum value already exists")
             
        new_enum = EnumValue(field_name=field_name, field_value=field_value)
        db.session.add(new_enum)
        db.session.commit()
        return success_response(new_enum.to_dict(), "Enum value added")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

# 5. Upload Image
@product_management_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return error_response("No file part", 400)
    file = request.files['file']
    if file.filename == '':
        return error_response("No selected file", 400)
    
    if file:
        filename = str(uuid.uuid4()) + "_" + file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Return URL relative to static folder
        # Ensure your Flask app has static_folder configured or default to 'static' in app root
        # Here we assume standard setup where /static maps to the static folder
        file_url = f"/static/uploads/{filename}" 
        return success_response({'url': file_url})

# Get Project Logs
@product_management_bp.route('/projects/<int:id>/logs', methods=['GET'])
def get_project_logs(id):
    try:
        logs = ProjectLog.query.filter_by(project_id=id).order_by(ProjectLog.operation_time.desc()).all()
        return success_response([log.to_dict() for log in logs])
    except Exception as e:
        return error_response(str(e))
