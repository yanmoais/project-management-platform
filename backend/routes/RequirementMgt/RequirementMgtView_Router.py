from flask import Blueprint, jsonify

requirement_bp = Blueprint('requirement_bp', __name__)

@requirement_bp.route('/', methods=['GET'])
def index():
    return jsonify({'code': 200, 'msg': 'success', 'data': 'Hello from 需求管理'})
