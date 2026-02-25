import shutil
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Remove vídeos de runs com mais de 30 dias'

    def handle(self, *args, **kwargs):
        from apps.testing.models import TestRun

        cutoff = timezone.now() - timedelta(days=30)
        old_runs = TestRun.objects.filter(created_at__lt=cutoff, video_path__gt='')
        count = 0
        for run in old_runs:
            video_dir = Path(settings.MEDIA_ROOT) / 'videos' / str(run.id)
            if video_dir.exists():
                shutil.rmtree(video_dir)
                run.video_path = ''
                run.save(update_fields=['video_path'])
                count += 1
        self.stdout.write(self.style.SUCCESS(f'{count} vídeos removidos'))
