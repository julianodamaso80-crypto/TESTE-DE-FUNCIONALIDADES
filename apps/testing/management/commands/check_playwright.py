from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Verifica instalação do Playwright'

    def handle(self, *args, **kwargs):
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                browser.close()
            self.stdout.write(self.style.SUCCESS(
                'Playwright OK — Chromium disponível'
            ))
        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f'Playwright INDISPONÍVEL: {e}'
            ))
