from flask import Blueprint, jsonify

development_bp = Blueprint('development_bp', __name__)

@development_bp.route('/', methods=['GET'])
def index():
    return jsonify({'code': 200, 'msg': 'success', 'data': 'Hello from 研发管理'})
