from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Inicialização pós-deploy Railway'

    def handle(self, *args, **kwargs):
        from django.contrib.sites.models import Site
        site = Site.objects.get_or_create(id=1)[0]
        domain = __import__('os').environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')
        site.domain = domain
        site.name = 'SpriteTest'
        site.save()
        self.stdout.write(self.style.SUCCESS(f'Site configurado: {domain}'))
