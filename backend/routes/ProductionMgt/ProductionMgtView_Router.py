from flask import Blueprint, jsonify

production_bp = Blueprint('production_bp', __name__)

@production_bp.route('/', methods=['GET'])
def index():
    return jsonify({'code': 200, 'msg': 'success', 'data': 'Hello from 投产管理'})
