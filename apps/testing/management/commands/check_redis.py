import redis
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Verifica conexão com Redis'

    def handle(self, *args, **kwargs):
        try:
            r = redis.from_url(settings.CELERY_BROKER_URL)
            r.ping()
            self.stdout.write(self.style.SUCCESS(
                'Redis OK — Celery async disponível'
            ))
        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f'Redis OFFLINE — usando fallback síncrono. Erro: {e}'
            ))
