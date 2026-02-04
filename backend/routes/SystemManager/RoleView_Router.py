from flask import Blueprint, jsonify

sys_role_bp = Blueprint('sys_role', __name__)

@sys_role_bp.route('/list', methods=['GET'])
def list_roles():
    return jsonify({'code': 200, 'msg': 'Success', 'data': []})
