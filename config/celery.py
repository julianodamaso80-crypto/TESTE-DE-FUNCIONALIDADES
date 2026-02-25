import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('spritetest')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# Defaults para todas as tasks
app.conf.task_default_queue = 'default'
app.conf.task_annotations = {
    '*': {
        'max_retries': 3,
        'soft_time_limit': 300,
    },
}
