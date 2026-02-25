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
    return JsonResponse({'status': 'ok', 'version': '0.1.0'})


def error_404(request, exception):
    """Custom 404 error handler."""
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    """Custom 500 error handler."""
    return render(request, 'errors/500.html', status=500)
