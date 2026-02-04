from flask import Blueprint, jsonify

deployment_bp = Blueprint('deployment_bp', __name__)

@deployment_bp.route('/', methods=['GET'])
def index():
    return jsonify({'code': 200, 'msg': 'success', 'data': 'Hello from 移交部署'})
