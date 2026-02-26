from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Verifica se o projeto está pronto para produção'

    def handle(self, *args, **kwargs):
        from django.conf import settings

        checks = {
            'SECRET_KEY segura (>50 chars)': len(settings.SECRET_KEY) > 50,
            'DEBUG=False': not settings.DEBUG,
            'SENTRY configurado': bool(settings.SENTRY_DSN),
            'STRIPE configurado': bool(getattr(settings, 'STRIPE_SECRET_KEY', '')),
            'ANTHROPIC configurado': bool(getattr(settings, 'ANTHROPIC_API_KEY', '')),
            'EMAIL configurado': 'console' not in settings.EMAIL_BACKEND,
            'ALLOWED_HOSTS configurado': bool(settings.ALLOWED_HOSTS),
            'HTTPS (SECURE_SSL_REDIRECT)': getattr(settings, 'SECURE_SSL_REDIRECT', False),
        }

        all_ok = True
        for check, result in checks.items():
            status = '\u2705' if result else '\u274c'
            self.stdout.write(f'{status} {check}')
            if not result:
                all_ok = False

        if all_ok:
            self.stdout.write(self.style.SUCCESS('\n\U0001f680 Pronto para produção!'))
        else:
            self.stdout.write(self.style.WARNING('\n\u26a0\ufe0f  Configure os itens \u274c antes de lançar.'))
