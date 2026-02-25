web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
worker: celery -A config worker -l info -c 2 -Q default
beat: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
