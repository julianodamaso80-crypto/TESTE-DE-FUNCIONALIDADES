import time
from django.utils import timezone


def check_database():
    start = time.time()
    try:
        from django.db import connection
        connection.ensure_connection()
        return {'status': 'operational', 'latency_ms': round((time.time() - start) * 1000)}
    except Exception as e:
        return {'status': 'outage', 'error': str(e)[:100]}


def check_redis():
    start = time.time()
    try:
        from django.conf import settings
        import redis
        r = redis.from_url(getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0'))
        r.ping()
        return {'status': 'operational', 'latency_ms': round((time.time() - start) * 1000)}
    except Exception:
        return {'status': 'degraded', 'note': 'Redis offline — usando fallback síncrono'}


def check_ai():
    from django.conf import settings
    if getattr(settings, 'ANTHROPIC_API_KEY', ''):
        return {'status': 'operational', 'note': 'Claude API configurado'}
    return {'status': 'degraded', 'note': 'Usando mock (sem ANTHROPIC_API_KEY)'}


def get_system_status():
    components = {
        'API & Dashboard':    check_database(),
        'Background Workers': check_redis(),
        'AI Engine':          check_ai(),
        'Test Execution':     {'status': 'operational'},
    }
    statuses = [c['status'] for c in components.values()]
    if all(s == 'operational' for s in statuses):
        overall, text = 'operational', 'All Systems Operational'
    elif any(s == 'outage' for s in statuses):
        overall, text = 'outage', 'Partial Outage Detected'
    else:
        overall, text = 'degraded', 'Degraded Performance'
    return {
        'overall': overall,
        'overall_text': text,
        'components': components,
        'checked_at': timezone.now(),
    }
