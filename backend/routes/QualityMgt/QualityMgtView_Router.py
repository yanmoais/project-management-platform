from flask import Blueprint, jsonify

quality_bp = Blueprint('quality_bp', __name__)

@quality_bp.route('/', methods=['GET'])
def index():
    return jsonify({'code': 200, 'msg': 'success', 'data': 'Hello from 质量管理'})
