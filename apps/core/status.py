import os
import time
from django.utils import timezone


def check_database():
    start = time.time()
    try:
        from django.db import connection
        connection.ensure_connection()
        latency = round((time.time() - start) * 1000)
        return {'status': 'operational', 'latency_ms': latency}
    except Exception as e:
        return {'status': 'outage', 'error': str(e)}


def check_redis():
    start = time.time()
    try:
        from django.conf import settings
        import redis
        r = redis.from_url(getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0'))
        r.ping()
        latency = round((time.time() - start) * 1000)
        return {'status': 'operational', 'latency_ms': latency}
    except Exception:
        return {'status': 'degraded', 'error': 'Redis offline'}


def check_ai_service():
    from django.conf import settings
    if not getattr(settings, 'ANTHROPIC_API_KEY', '') and not os.environ.get('ANTHROPIC_API_KEY', ''):
        return {'status': 'degraded', 'note': 'Using mock (no API key)'}
    return {'status': 'operational', 'note': 'Claude API configured'}


def get_system_status():
    db = check_database()
    redis_status = check_redis()
    ai = check_ai_service()
    components = {
        'API & Dashboard': db,
        'Background Workers': redis_status,
        'AI Engine': ai,
        'Test Execution': {'status': 'operational'},
    }
    all_operational = all(c['status'] == 'operational' for c in components.values())
    any_outage = any(c['status'] == 'outage' for c in components.values())
    if all_operational:
        overall = 'operational'
        overall_text = 'All Systems Operational'
    elif any_outage:
        overall = 'outage'
        overall_text = 'Partial Outage Detected'
    else:
        overall = 'degraded'
        overall_text = 'Degraded Performance'
    return {
        'overall': overall,
        'overall_text': overall_text,
        'components': components,
        'checked_at': timezone.now(),
    }
