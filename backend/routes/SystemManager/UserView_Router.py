from flask import Blueprint, jsonify

sys_user_bp = Blueprint('sys_user', __name__)

@sys_user_bp.route('/list', methods=['GET'])
def list_users():
    return jsonify({'code': 200, 'msg': 'Success', 'data': []})
