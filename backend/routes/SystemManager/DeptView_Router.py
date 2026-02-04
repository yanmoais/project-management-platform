from flask import Blueprint, jsonify

sys_dept_bp = Blueprint('sys_dept', __name__)

@sys_dept_bp.route('/list', methods=['GET'])
def list_depts():
    return jsonify({'code': 200, 'msg': 'Success', 'data': []})
