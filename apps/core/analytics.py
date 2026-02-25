import logging

logger = logging.getLogger('spritetest.analytics')


def get_posthog():
    from django.conf import settings
    if not settings.POSTHOG_API_KEY:
        return None
    try:
        import posthog as ph
        ph.api_key = settings.POSTHOG_API_KEY
        ph.host = settings.POSTHOG_HOST
        return ph
    except Exception:
        return None


def track(user_id: str, event: str, properties: dict = None):
    ph = get_posthog()
    if not ph:
        return
    try:
        ph.capture(str(user_id), event, properties or {})
    except Exception as e:
        logger.debug(f"track failed: {e}")


def identify(user_id: str, properties: dict = None):
    ph = get_posthog()
    if not ph:
        return
    try:
        ph.identify(str(user_id), properties or {})
    except Exception as e:
        logger.debug(f"identify failed: {e}")
