from celery import Celery, Task
from app.core.config import settings

class ContextTask(Task):
    """Celery Task que proporciona contexto de aplicación"""
    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

celery = Celery(
    __name__,
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Lima",
    enable_utc=True,
)

celery.Task = ContextTask

__all__ = ["celery"]