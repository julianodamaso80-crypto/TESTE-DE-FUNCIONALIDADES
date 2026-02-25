import logging
import os
import time

from django.utils import timezone

logger = logging.getLogger('spritetest.playwright')


def _run_browser_tests(cases_data: list, base_url: str) -> list:
    """
    Executa os testes no Playwright (sync API).
    Recebe e retorna dados puros (dicts) — sem tocar no Django ORM.
    """
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

    results = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='SpriteTest/1.0 Playwright',
        )
        page = context.new_page()

        for case_data in cases_data:
            result = {'status': 'passed', 'error': '', 'duration_ms': 0, 'fix_suggestion': ''}
            start = time.monotonic()
            category = (case_data.get('category') or '').lower()

            try:
                page.goto(base_url, wait_until='networkidle', timeout=30000)

                if 'navigation' in category:
                    _test_navigation(page, base_url)
                elif 'auth' in category or 'authentication' in category:
                    _test_auth_elements(page)
                elif 'performance' in category:
                    _test_performance(page)
                elif 'form' in category:
                    _test_forms(page)
                else:
                    _test_ui_elements(page)

                result['status'] = 'passed'

            except PlaywrightTimeout as e:
                result['status'] = 'failed'
                result['error'] = f"Timeout: {str(e)[:200]}"
                result['fix_suggestion'] = (
                    "Elemento não respondeu no tempo esperado. "
                    "Verifique se o seletor está correto e adicione wait explícito."
                )
            except Exception as e:
                result['status'] = 'failed'
                result['error'] = str(e)[:300]
                result['fix_suggestion'] = (
                    f"Erro inesperado. Verifique se a URL {base_url} está acessível "
                    f"e o elemento existe."
                )
            finally:
                elapsed = time.monotonic() - start
                result['duration_ms'] = int(elapsed * 1000)

            result['case_id'] = case_data['id']
            results.append(result)

        browser.close()

    return results


def _test_navigation(page, base_url):
    links = page.query_selector_all('a[href]')
    if not links:
        raise Exception("Nenhum link encontrado na página")
    page.wait_for_load_state('networkidle')


def _test_auth_elements(page):
    selectors = [
        'input[type=email]',
        'input[type=password]',
        'input[name=email]',
        'input[name=username]',
    ]
    found = False
    for sel in selectors:
        el = page.query_selector(sel)
        if el:
            found = True
            break
    if not found:
        raise Exception("Campos de autenticação não encontrados na página")


def _test_forms(page):
    forms = page.query_selector_all('form')
    if not forms:
        raise Exception("Nenhum formulário encontrado na página")
    inputs = page.query_selector_all('input:not([type=hidden])')
    if not inputs:
        raise Exception("Nenhum campo de input encontrado nos formulários")


def _test_performance(page):
    start = time.time()
    page.wait_for_load_state('networkidle')
    elapsed = time.time() - start
    if elapsed > 10:
        raise Exception(f"Página demorou {elapsed:.1f}s para carregar (limite: 10s)")


def _test_ui_elements(page):
    body = page.query_selector('body')
    if not body:
        raise Exception("Página sem body — possível erro de renderização")
    page.wait_for_load_state('domcontentloaded')


def run_playwright_sync(test_run) -> None:
    """Executa todos os TestCases de um TestRun com Playwright real (API síncrona)."""
    base_url = test_run.project.base_url
    logger.info(f"Playwright iniciando: run={test_run.id} url={base_url}")

    # 1) Prefetch case data BEFORE entering Playwright context
    #    (Django ORM calls are not allowed inside greenlet/async context)
    cases = list(test_run.cases.all().order_by('order'))
    cases_data = [{'id': str(c.id), 'category': c.category, 'title': c.title} for c in cases]
    cases_map = {str(c.id): c for c in cases}

    # 2) Run browser tests (pure Playwright, no ORM)
    results = _run_browser_tests(cases_data, base_url)

    # 3) Save results back to DB (outside Playwright context)
    for result in results:
        case = cases_map[result['case_id']]
        case.status = 'passed' if result['status'] == 'passed' else 'failed'
        case.error_message = result.get('error', '')
        case.ai_fix_suggestion = result.get('fix_suggestion', '')
        case.duration_ms = result.get('duration_ms', 0)
        case.save(update_fields=['status', 'error_message', 'ai_fix_suggestion', 'duration_ms'])

    # 4) Recalculate summary
    test_run.recalculate_summary()
    test_run.refresh_from_db()

    test_run.status = 'passed' if test_run.failed_cases == 0 else 'failed'
    test_run.completed_at = timezone.now()

    if test_run.started_at:
        test_run.duration_secs = int((test_run.completed_at - test_run.started_at).total_seconds())
    else:
        test_run.duration_secs = 0

    test_run.ai_summary = (
        f"Playwright executou {test_run.total_cases} testes reais em {test_run.duration_secs}s. "
        f"{test_run.passed_cases} passaram, {test_run.failed_cases} falharam."
    )
    test_run.save(update_fields=['status', 'completed_at', 'duration_secs', 'ai_summary'])
    logger.info(f"Playwright concluído: run={test_run.id} pass_rate={test_run.pass_rate}%")
