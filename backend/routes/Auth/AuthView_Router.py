from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import db, SysUser, AppUserLog
import jwt
import datetime
from backend.config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'code': 400, 'msg': '邮箱和密码不能为空'}), 400

    # 对于本系统，我们可以通过邮箱或用户名登录。
    # 前端表单要求输入邮箱，所以我们假设是邮箱登录，但用户表的用户名是唯一的。
    # 让我们检查邮箱是否匹配或用户名是否匹配（如果我们想支持这两种方式）
    # 当前create.sql数据中，'admin'用户名和'admin@example.com'邮箱是对应的。
    
    user = SysUser.query.filter_by(email=email).first()
    
    # 如果邮箱未匹配，尝试用户名（可选）
    if not user:
        user = SysUser.query.filter_by(username=email).first()

    if not user:
        return jsonify({'code': 401, 'msg': '用户不存在'}), 401
    
    # 验证密码
    # 注意：create.sql初始数据有bcrypt哈希值。
    # '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2' 对应 '123456'
    if not check_password_hash(user.password, password):
        return jsonify({'code': 401, 'msg': '密码错误'}), 401

    if user.status == 0:
        return jsonify({'code': 403, 'msg': '账号已禁用'}), 403

    # 生成Token
    token = jwt.encode({
        'user_id': user.user_id,
        'username': user.username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, Config.SECRET_KEY, algorithm='HS256')

    # 更新登录信息
    user.login_ip = request.remote_addr
    user.login_date = datetime.datetime.now()
    
    # 记录登录日志
    user_agent = request.user_agent
    login_log = AppUserLog(
        user_id=user.user_id,
        username=user.username,
        login_ip=request.remote_addr,
        login_location=None, # 占位符，用于位置服务
        browser=user_agent.browser,
        os=user_agent.platform,
        device=user_agent.string[:50] if user_agent.string else None, # Store partial UA string as device info
        login_type=1, # Password login
        login_status=1, # Success
        login_time=datetime.datetime.now()
    )
    db.session.add(login_log)
    
    db.session.commit()

    response = jsonify({
        'code': 200, 
        'msg': 'Login successful', 
        # 'token': token, # Removed token from body
        'data': user.to_dict()
    })
    
    # Set Authorization header
    response.headers['Authorization'] = f'Bearer {token}'
    # Also expose the header so frontend can read it
    response.headers['Access-Control-Expose-Headers'] = 'Authorization'
    
    return response

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('name') # Frontend sends 'name' which we'll use as username/nickname
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'code': 400, 'msg': '所有字段都是必填项'}), 400

    if SysUser.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'msg': '用户名已存在'}), 400
    
    if SysUser.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'msg': '邮箱已注册'}), 400

    hashed_password = generate_password_hash(password)

    new_user = SysUser(
        username=username, # Using name as username
        nickname=username,
        email=email,
        password=hashed_password,
        status=1,
        create_time=datetime.datetime.now()
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '注册成功'})

@auth_bp.route('/user/info', methods=['GET'])
def get_user_info():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'code': 401, 'msg': '缺少认证头'}), 401
    
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        
        user = SysUser.query.get(user_id)
        if not user:
            return jsonify({'code': 401, 'msg': '用户不存在'}), 401
            
        # In a real app, fetch roles and permissions here
        # For now, return basic info and mock roles
        roles = ['admin'] if user.username == 'admin' else ['common']
        
        return jsonify({
            'code': 200,
            'data': {
                'name': user.nickname,
                'avatar': user.avatar,
                'roles': roles,
                'permissions': ['*:*:*'] if 'admin' in roles else []
            }
        })
    except Exception as e:
        return jsonify({'code': 401, 'msg': '无效的令牌'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'code': 401, 'msg': '缺少认证头'}), 401
    
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        
        user = SysUser.query.get(user_id)
        if not user:
            return jsonify({'code': 401, 'msg': '用户不存在'}), 401
        
        # Update login info 记录用户登出信息
        # user.login_ip = request.remote_addr
        # user.login_date = datetime.datetime.now()
        
        # 查找该用户最近一次未登出的登录日志
        last_login_log = AppUserLog.query.filter_by(
            user_id=user_id, 
            login_status=1
        ).filter(
            AppUserLog.logout_time == None
        ).order_by(
            AppUserLog.login_time.desc()
        ).first()

        if last_login_log:
            # 更新登出时间和在线时长
            now = datetime.datetime.now()
            last_login_log.logout_time = now
            # 计算在线时长（秒）
            if last_login_log.login_time:
                duration = (now - last_login_log.login_time).total_seconds()
                last_login_log.online_duration = int(duration)
        
        db.session.commit()
        
        return jsonify({'code': 200, 'msg': '登出成功'})
    except Exception as e:
        return jsonify({'code': 401, 'msg': '无效的令牌'}), 401
    