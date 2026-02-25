import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger('spritetest.tasks')


@shared_task(bind=True, max_retries=3, name='testing.run_test_execution')
def run_test_execution(self, run_id: str):
    """Executa testes de forma assíncrona via Celery."""
    from .executor import run_test_execution_smart
    from .models import TestRun

    try:
        run = TestRun.objects.get(id=run_id)
    except TestRun.DoesNotExist:
        logger.error("TestRun %s não encontrado", run_id)
        return

    try:
        logger.info("Iniciando execução async: %s", run_id)
        run_test_execution_smart(run)
        logger.info("Execução concluída: %s status=%s", run_id, run.status)
    except Exception as exc:
        run.status = 'error'
        run.error_message = str(exc)
        run.completed_at = timezone.now()
        run.save(update_fields=['status', 'error_message', 'completed_at'])
        logger.error("Erro na execução %s: %s", run_id, exc)
        raise self.retry(exc=exc, countdown=10)


@shared_task(name='testing.run_scheduled_tests')
def run_scheduled_tests():
    """Executa todos os testes agendados com next_run_at <= agora."""
    from apps.testing.ai_service import generate_test_cases
    from apps.testing.executor import run_test_execution_smart
    from apps.testing.models import ScheduledTest, TestCase, TestRun

    now = timezone.now()
    schedules = ScheduledTest.objects.filter(is_active=True, next_run_at__lte=now)
    logger.info(f"Scheduled: {schedules.count()} testes para executar")

    for schedule in schedules:
        try:
            project = schedule.project
            ai_result = generate_test_cases(
                project.base_url, project.test_type, project.special_instructions
            )

            if 'error' not in ai_result:
                run = TestRun.objects.create(
                    project=project,
                    triggered_by=schedule.created_by or project.created_by,
                    status='pending',
                    ai_model_used='claude-opus-4-6',
                )

                for i, tc in enumerate(ai_result.get('test_cases', [])):
                    TestCase.objects.create(
                        run=run,
                        title=tc.get('title', ''),
                        description=tc.get('description', ''),
                        category=tc.get('category', ''),
                        steps=tc.get('steps', []),
                        order=i,
                    )

                run.total_cases = run.cases.count()
                run.save(update_fields=['total_cases'])

                run_test_execution_smart(run)

                schedule.last_run_at = now
                schedule.calculate_next_run()

                if schedule.notify_email:
                    send_run_notification.delay(str(run.id))
        except Exception as e:
            logger.error(f"Erro no scheduled test {schedule.id}: {e}")

    return f"Processados {schedules.count()} agendamentos"


@shared_task(name='testing.send_run_notification')
def send_run_notification(run_id: str):
    """Envia email com resultado do run."""
    from django.conf import settings
    from django.core.mail import send_mail

    from apps.testing.models import TestRun

    try:
        run = TestRun.objects.select_related('project__workspace').get(id=run_id)
        schedule = run.project.schedules.filter(is_active=True).first()

        if not schedule or not schedule.notify_email:
            return
        if schedule.notify_on_failure_only and run.status == 'passed':
            return

        members = list(
            run.project.workspace.members.filter(is_active=True).values_list('email', flat=True)
        )

        duration = ''
        if run.duration_secs:
            mins, secs = divmod(int(run.duration_secs), 60)
            duration = f"{mins}m {secs}s" if mins else f"{secs}s"

        status_icon = '\u2713' if run.status == 'passed' else '\u2717'
        subject = (
            f"[SpriteTest] {status_icon} {run.project.name} — {run.pass_rate}% pass rate"
        )
        body = f"""Resultado do teste agendado:

Projeto: {run.project.name}
URL: {run.project.base_url}
Status: {run.status.upper()}
Pass Rate: {run.pass_rate}%
Total: {run.total_cases} casos ({run.passed_cases} passou, {run.failed_cases} falhou)
Duração: {duration or 'N/A'}

Ver relatório completo: /testing/runs/{run.id}/report/

— SpriteTest"""

        send_mail(
            subject, body, settings.DEFAULT_FROM_EMAIL, members, fail_silently=True
        )
        logger.info(f"Email enviado para {len(members)} membros: run={run_id}")
    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {e}")
