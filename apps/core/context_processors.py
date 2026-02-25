def analytics(request):
    from django.conf import settings
    return {
        'POSTHOG_KEY': settings.POSTHOG_API_KEY,
        'POSTHOG_HOST': settings.POSTHOG_HOST,
    }
