from django.http import JsonResponse
from django.shortcuts import redirect, render


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


def status_page(request):
    from apps.core.status import get_system_status
    return render(request, 'core/status.html', {'status': get_system_status()})


def status_api(request):
    from apps.core.status import get_system_status
    s = get_system_status()
    return JsonResponse({
        'status': s['overall'],
        'message': s['overall_text'],
        'components': {k: v['status'] for k, v in s['components'].items()},
        'timestamp': s['checked_at'].isoformat(),
    })


def privacy(request):
    return render(request, 'core/legal/privacy.html')


def terms(request):
    return render(request, 'core/legal/terms.html')


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


def handler429(request, exception=None):
    if request.path.startswith('/api/'):
        return JsonResponse({'detail': 'Rate limit excedido. Tente novamente em breve.'}, status=429)
    from django.contrib import messages
    messages.error(request, 'Muitas tentativas. Aguarde um momento.')
    return redirect(request.META.get('HTTP_REFERER', '/'))
