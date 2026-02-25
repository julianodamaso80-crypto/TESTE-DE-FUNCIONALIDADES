from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Executa manualmente os testes agendados pendentes'

    def handle(self, *args, **kwargs):
        from apps.testing.tasks import run_scheduled_tests

        result = run_scheduled_tests()
        self.stdout.write(self.style.SUCCESS(result))
