from flask import Blueprint, jsonify

sys_menu_bp = Blueprint('sys_menu', __name__)

@sys_menu_bp.route('/list', methods=['GET'])
def list_menus():
    return jsonify({'code': 200, 'msg': 'Success', 'data': []})
