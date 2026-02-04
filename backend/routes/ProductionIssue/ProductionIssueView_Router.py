from flask import Blueprint, jsonify

issue_bp = Blueprint('issue_bp', __name__)

@issue_bp.route('/', methods=['GET'])
def index():
    return jsonify({'code': 200, 'msg': 'success', 'data': 'Hello from 生产问题'})
