from pydantic_settings import BaseSettings
from typing import Dict

class Settings(BaseSettings):
    """
    系统配置类
    使用 Pydantic BaseSettings 管理环境变量
    """
    # 项目名称
    PROJECT_NAME: str = "Project Management Platform"
    
    # 密钥配置
    SECRET_KEY: str = "dev_secret_key_change_in_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # token过期时间：24小时
    
    # 数据库配置
    # 注意：FastAPI 使用异步驱动 aiomysql
    SQLALCHEMY_DATABASE_URI: str = 'mysql+aiomysql://root:123456@localhost/project_management_platform'
    
    # 多数据库绑定
    SQLALCHEMY_BINDS: Dict[str, str] = {
        'automation': 'mysql+aiomysql://root:123456@localhost/automation'
    }

    # Redis 配置
    REDIS_URL: str = 'redis://localhost:6379/0'
    
    # Celery 配置
    CELERY_BROKER_URL: str = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND: str = 'redis://localhost:6379/2'
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
