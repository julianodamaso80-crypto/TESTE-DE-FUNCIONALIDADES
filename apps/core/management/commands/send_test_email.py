from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Envia email de teste para verificar configuração SMTP'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)

    def handle(self, *args, **options):
        from django.conf import settings
        from django.core.mail import send_mail

        try:
            send_mail(
                'SpriteTest — Email de Teste',
                'Se você recebeu este email, o SMTP está configurado corretamente.',
                settings.DEFAULT_FROM_EMAIL,
                [options['email']],
            )
            self.stdout.write(self.style.SUCCESS(f'Email enviado para {options["email"]}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Falhou: {e}'))
