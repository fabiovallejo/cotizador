from app.tasks import celery_app

@celery_app.task(name="test_task")
def test_task():
    """Task de prueba para verificar que Celery funciona"""
    return {"status": "ok", "message": "Task ejecutado correctamente"}