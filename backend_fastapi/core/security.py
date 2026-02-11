from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
from werkzeug.security import generate_password_hash, check_password_hash
# from passlib.context import CryptContext # 暂时弃用 passlib，改用 werkzeug 保持兼容
from backend_fastapi.core.config import settings

# 密码哈希上下文 (passlib 配置暂时保留注释)
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    使用 werkzeug.security.check_password_hash 以兼容原 Flask 系统生成的哈希
    """
    # 兼容处理：如果是 bcrypt ($2a$ 或 $2b$)，werkzeug 也能处理（只要底层有 bcrypt 库）
    # 但原系统如果是 Flask 默认生成的，可能是 pbkdf2 或 scrypt
    # 根据数据库检查结果，哈希是 $2a$ 开头的 bcrypt 格式。
    # werkzeug.security.check_password_hash 支持 bcrypt (如果安装了 bcrypt 库，当前已安装)
    try:
        return check_password_hash(hashed_password, plain_password)
    except Exception as e:
        # 如果 werkzeug 失败，可能是因为它不支持 $2a$ 前缀（旧版 bcrypt），尝试用 passlib 作为后备
        # 但既然是迁移，最好统一。
        # 这里打印错误日志方便调试
        print(f"Werkzeug verification failed: {e}")
        # Fallback to passlib if werkzeug fails (optional, but robust)
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False

def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    使用 werkzeug.security.generate_password_hash 保持一致性
    """
    return generate_password_hash(password)

def create_access_token(subject: Union[str, Any], user_id: int) -> str:
    """
    创建 JWT Access Token
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire, 
        "sub": str(subject),
        "user_id": user_id,
        "username": str(subject)
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
