from django.http import JsonResponse
from django.shortcuts import render


def home(request):
    """Landing page principal."""
    context = {
        'page_title': 'SpriteTest - AI Testing Platform',
    }
    return render(request, 'core/home.html', context)


def health_check(request):
    """Health check endpoint para load balancers e monitoramento."""
    from django.db import connection
    checks = {'status': 'ok', 'version': '1.0.0', 'checks': {}}
    try:
        connection.ensure_connection()
        checks['checks']['database'] = 'ok'
    except Exception as e:
        checks['checks']['database'] = f'error: {str(e)}'
        checks['status'] = 'degraded'
    try:
        import redis
        from django.conf import settings
        r = redis.from_url(getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0'))
        r.ping()
        checks['checks']['redis'] = 'ok'
    except Exception:
        checks['checks']['redis'] = 'offline'
    return JsonResponse(checks)


def error_404(request, exception):
    """Custom 404 error handler."""
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    """Custom 500 error handler."""
    return render(request, 'errors/500.html', status=500)
