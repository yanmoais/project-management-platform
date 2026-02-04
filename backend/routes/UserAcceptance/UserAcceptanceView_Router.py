from flask import Blueprint, jsonify

uat_bp = Blueprint('uat_bp', __name__)

@uat_bp.route('/', methods=['GET'])
def index():
    return jsonify({'code': 200, 'msg': 'success', 'data': 'Hello from 用户验收'})
