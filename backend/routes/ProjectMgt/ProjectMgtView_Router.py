from flask import Blueprint, jsonify

project_bp = Blueprint('project_bp', __name__)

@project_bp.route('/', methods=['GET'])
def index():
    return jsonify({'code': 200, 'msg': 'success', 'data': 'Hello from 项目管理'})
