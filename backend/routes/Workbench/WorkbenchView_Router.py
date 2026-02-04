from flask import Blueprint, jsonify

workbench_bp = Blueprint('workbench_bp', __name__)

@workbench_bp.route('/', methods=['GET'])
def index():
    return jsonify({'code': 200, 'msg': 'success', 'data': 'Hello from 工作台'})
