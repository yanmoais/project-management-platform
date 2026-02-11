import os

class Config:
    # Use the credentials from settings.js (root:123456)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/project_management_platform'
    SQLALCHEMY_BINDS = {
        'automation': 'mysql+pymysql://root:123456@localhost/automation'
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_change_in_prod'

    # Celery Configuration
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_ENABLE_UTC = False
