from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Verifica PostHog'

    def handle(self, *args, **kwargs):
        from django.conf import settings
        if not settings.POSTHOG_API_KEY:
            self.stdout.write(self.style.WARNING('PostHog: chave vazia — analytics desabilitado (OK para dev)'))
            return
        self.stdout.write(self.style.SUCCESS(f'PostHog OK — {settings.POSTHOG_HOST}'))
