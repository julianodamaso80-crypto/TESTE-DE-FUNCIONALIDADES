import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger('spritetest.tasks')


@shared_task(bind=True, max_retries=3, name='testing.run_test_execution')
def run_test_execution(self, run_id: str):
    """Executa testes de forma assíncrona via Celery."""
    from .executor import simulate_test_execution
    from .models import TestRun

    try:
        run = TestRun.objects.get(id=run_id)
    except TestRun.DoesNotExist:
        logger.error("TestRun %s não encontrado", run_id)
        return

    try:
        logger.info("Iniciando execução async: %s", run_id)
        simulate_test_execution(run)
        logger.info("Execução concluída: %s status=%s", run_id, run.status)
    except Exception as exc:
        run.status = 'error'
        run.error_message = str(exc)
        run.completed_at = timezone.now()
        run.save(update_fields=['status', 'error_message', 'completed_at'])
        logger.error("Erro na execução %s: %s", run_id, exc)
        raise self.retry(exc=exc, countdown=10)
