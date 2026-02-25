import logging

from celery import shared_task

logger = logging.getLogger('spritetest.tasks')


@shared_task(bind=True, max_retries=3, name='testing.run_test_execution')
def run_test_execution(self, run_id: str):
    """Executa testes de forma assíncrona via Celery."""
    from .executor import simulate_test_execution
    from .models import TestRun

    logger.info("Starting test execution for run_id=%s", run_id)

    try:
        run = TestRun.objects.get(id=run_id)
    except TestRun.DoesNotExist:
        raise ValueError(f"TestRun not found: {run_id}")

    try:
        simulate_test_execution(run)
        logger.info(
            "Test execution completed for run_id=%s — status=%s, pass_rate=%s%%",
            run_id, run.status, run.pass_rate,
        )
    except Exception as exc:
        logger.error("Test execution failed for run_id=%s: %s", run_id, exc)
        run.status = 'error'
        run.error_message = str(exc)
        run.save(update_fields=['status', 'error_message'])
        raise

    return {
        'run_id': run_id,
        'status': run.status,
        'pass_rate': run.pass_rate,
    }
