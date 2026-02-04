from flask import Blueprint, jsonify

my_space_bp = Blueprint('my_space_bp', __name__)

@my_space_bp.route('/', methods=['GET'])
def index():
    return jsonify({'code': 200, 'msg': 'success', 'data': 'Hello from 我的空间'})
