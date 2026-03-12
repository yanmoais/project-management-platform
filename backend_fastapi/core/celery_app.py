from celery import Celery
from backend_fastapi.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["backend_fastapi.tasks.automation_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    broker_connection_retry_on_startup=settings.CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP,
    beat_schedule={
        'scan-automation-rules-every-minute': {
            'task': 'backend_fastapi.tasks.automation_tasks.scan_automation_rules',
            'schedule': 60.0, # 每 60 秒执行一次
            'args': ()
        },
    }
)
