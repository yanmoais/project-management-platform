from flask import Blueprint, jsonify

sys_notice_bp = Blueprint('sys_notice', __name__)

@sys_notice_bp.route('/list', methods=['GET'])
def list_notices():
    return jsonify({'code': 200, 'msg': 'Success', 'data': []})
