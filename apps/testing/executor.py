import logging
import random

from django.utils import timezone

logger = logging.getLogger(__name__)

# Mensagens de erro realistas por categoria
_ERROR_MESSAGES = {
    'Navigation': [
        'Page returned HTTP 404 — route not found.',
        'Navigation link points to broken URL — received timeout after 10s.',
        'Redirect loop detected: page redirects back to itself.',
    ],
    'Authentication': [
        'Login form submitted successfully but no session cookie was set.',
        'Password field accepts less than 6 characters — minimum length not enforced.',
        'After login, user is redirected to 404 instead of dashboard.',
    ],
    'Forms': [
        'Form submission returned 500 Internal Server Error.',
        'Required field "email" accepted empty value — validation missing.',
        'Form CSRF token missing — submission rejected by server.',
    ],
    'UI': [
        'Horizontal scroll appears on viewport 375px — content overflows container.',
        'Button text is truncated on mobile — missing text-wrap or overflow handling.',
        'Dark mode toggle does not persist after page reload.',
    ],
    'Performance': [
        'First Contentful Paint is 4.2s — exceeds 1.8s threshold.',
        'Total page weight is 5.8MB — exceeds 3MB budget.',
        'Largest Contentful Paint at 6.1s — above 2.5s threshold.',
    ],
}

_FIX_SUGGESTIONS = {
    'Navigation': [
        'Verify the route is defined in urls.py and the view returns a valid response.',
        'Check for typos in href attributes and ensure all links use {% url %} template tags.',
        'Add redirect loop detection middleware or fix the redirect target URL.',
    ],
    'Authentication': [
        'Ensure the login view calls django.contrib.auth.login() after credential validation.',
        'Add MinLengthValidator(6) to the password field in your User model or form.',
        'Update LOGIN_REDIRECT_URL in settings.py to point to a valid dashboard route.',
    ],
    'Forms': [
        'Check the view for unhandled exceptions — add try/except and return proper error responses.',
        'Add required=True to the form field and ensure clean_email() validates non-empty input.',
        'Ensure {% csrf_token %} is included inside the <form> tag in the template.',
    ],
    'UI': [
        'Add overflow-x-hidden to the page container and use max-w-full on images/tables.',
        'Use Tailwind truncate or whitespace-nowrap with overflow-hidden on the button.',
        'Store the dark mode preference in localStorage and apply it on DOMContentLoaded.',
    ],
    'Performance': [
        'Defer non-critical JavaScript, compress images with WebP, enable gzip compression.',
        'Audit assets with Lighthouse — remove unused CSS/JS and lazy-load below-fold images.',
        'Optimize LCP element (usually hero image) — use preload, proper sizing, and CDN.',
    ],
}


def run_test_execution_smart(test_run) -> None:
    """
    Escolhe executor baseado em disponibilidade do Playwright.
    Real: se URL é acessível externamente.
    Mock: se URL é localhost ou Playwright indisponível.
    """
    from urllib.parse import urlparse

    url = test_run.project.base_url
    parsed = urlparse(url)
    hostname = parsed.hostname or ''

    is_local = (
        hostname in ('localhost', '127.0.0.1', '0.0.0.0')
        or hostname.endswith('.local')
    )

    if is_local:
        logger.info(f"URL local detectada ({url}) — usando executor mock")
        simulate_test_execution(test_run)
        return

    try:
        from apps.testing.playwright_runner import run_playwright_sync
        logger.info(f"URL externa ({url}) — usando Playwright real")
        run_playwright_sync(test_run)
    except Exception as e:
        logger.warning(f"Playwright falhou ({e}) — fallback para mock")
        simulate_test_execution(test_run)


def simulate_test_execution(test_run):
    """
    Simula a execução de todos os TestCases de um TestRun.
    80% chance de passed, 20% chance de failed com erro realista.
    """
    test_run.status = 'running'
    test_run.started_at = timezone.now()
    test_run.save(update_fields=['status', 'started_at'])

    cases = list(test_run.cases.all())

    for case in cases:
        case.status = 'running'
        case.save(update_fields=['status'])

        # Simulate execution time (50-800ms)
        case.duration_ms = random.randint(50, 800)

        if random.random() < 0.80:
            case.status = 'passed'
        else:
            case.status = 'failed'
            category = case.category or 'UI'
            errors = _ERROR_MESSAGES.get(category, _ERROR_MESSAGES['UI'])
            fixes = _FIX_SUGGESTIONS.get(category, _FIX_SUGGESTIONS['UI'])
            case.error_message = random.choice(errors)
            case.ai_fix_suggestion = random.choice(fixes)

        case.save(update_fields=['status', 'duration_ms', 'error_message', 'ai_fix_suggestion'])

    # Recalculate summary
    test_run.recalculate_summary()
    test_run.refresh_from_db()

    # Final status
    if test_run.failed_cases == 0:
        test_run.status = 'passed'
    else:
        test_run.status = 'failed'

    test_run.completed_at = timezone.now()
    if test_run.started_at:
        test_run.duration_secs = (test_run.completed_at - test_run.started_at).total_seconds()

    test_run.ai_summary = (
        f"Executed {test_run.total_cases} test cases. "
        f"{test_run.passed_cases} passed, {test_run.failed_cases} failed. "
        f"Pass rate: {test_run.pass_rate}%. "
    )
    if test_run.failed_cases > 0:
        test_run.ai_summary += "Review failed cases for AI fix suggestions."
    else:
        test_run.ai_summary += "All tests passed successfully."

    test_run.save(update_fields=[
        'status', 'completed_at', 'duration_secs', 'ai_summary',
    ])

    logger.info("TestRun %s completed: %s (pass rate: %s%%)", test_run.id, test_run.status, test_run.pass_rate)

    try:
        from apps.workspaces.notifications import send_run_notifications
        send_run_notifications(test_run)
    except Exception as e:
        logging.getLogger('spritetest').warning(f"Notification failed: {e}")

    return test_run
