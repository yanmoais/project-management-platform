from flask import Blueprint, jsonify

sys_post_bp = Blueprint('sys_post', __name__)

@sys_post_bp.route('/list', methods=['GET'])
def list_posts():
    return jsonify({'code': 200, 'msg': 'Success', 'data': []})
