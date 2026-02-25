import json
import logging
import os

logger = logging.getLogger(__name__)


def _get_mock_test_cases(base_url, test_type):
    """Retorna casos de teste mock realistas quando não há API key."""
    cases = [
        {
            'title': 'Homepage loads correctly',
            'description': f'Verify that {base_url} loads within acceptable time and renders key elements.',
            'category': 'Navigation',
            'steps': [
                f'Navigate to {base_url}',
                'Verify page returns HTTP 200',
                'Check page loads in under 3 seconds',
                'Verify main heading is present',
            ],
        },
        {
            'title': 'Navigation links work',
            'description': 'Verify all primary navigation links lead to valid pages.',
            'category': 'Navigation',
            'steps': [
                'Find all links in the main navigation',
                'Click each link',
                'Verify each page returns HTTP 200',
                'Verify no broken links (404)',
            ],
        },
        {
            'title': 'Login form validation',
            'description': 'Verify the login form validates inputs correctly.',
            'category': 'Authentication',
            'steps': [
                'Navigate to login page',
                'Submit empty form and check for validation errors',
                'Enter invalid email format and verify error message',
                'Enter valid credentials and verify successful login',
            ],
        },
        {
            'title': 'User registration flow',
            'description': 'Test complete user registration with valid data.',
            'category': 'Authentication',
            'steps': [
                'Navigate to registration page',
                'Fill in all required fields with valid data',
                'Submit the form',
                'Verify success message or redirect to dashboard',
            ],
        },
        {
            'title': 'Form submission with valid data',
            'description': 'Verify the main form submits and processes data correctly.',
            'category': 'Forms',
            'steps': [
                'Navigate to the primary form page',
                'Fill all required fields with valid data',
                'Click submit button',
                'Verify success feedback is displayed',
                'Verify data is persisted (reload and check)',
            ],
        },
        {
            'title': 'Responsive layout on mobile',
            'description': 'Verify the layout adapts properly to mobile viewport.',
            'category': 'UI',
            'steps': [
                f'Open {base_url} with 375x812 viewport',
                'Verify navigation collapses to hamburger menu',
                'Verify no horizontal scrollbar appears',
                'Verify text is readable without zooming',
            ],
        },
        {
            'title': 'Page performance audit',
            'description': 'Verify page performance meets acceptable thresholds.',
            'category': 'Performance',
            'steps': [
                f'Load {base_url} and measure First Contentful Paint',
                'Verify FCP is under 1.8 seconds',
                'Verify Largest Contentful Paint is under 2.5 seconds',
                'Check total page weight is under 3MB',
            ],
        },
        {
            'title': 'Error handling for invalid URLs',
            'description': 'Verify the app handles 404 and error states gracefully.',
            'category': 'UI',
            'steps': [
                f'Navigate to {base_url}/nonexistent-page-12345',
                'Verify a friendly 404 page is shown',
                'Verify the 404 page has a link back to home',
                'Verify no unhandled exceptions are exposed',
            ],
        },
    ]

    # Filter by test type
    if test_type == 'api':
        cases = [c for c in cases if c['category'] not in ('UI', 'Performance')]
    elif test_type == 'ui':
        pass  # keep all

    return cases


def generate_test_cases(base_url, test_type, special_instructions=''):
    """
    Gera casos de teste usando IA (Claude) ou retorna mock.

    Returns:
        dict com keys: test_cases (list), app_summary (str), test_strategy (str)
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY', '').strip()

    if not api_key:
        logger.info("ANTHROPIC_API_KEY not set — using mock test cases.")
        mock_cases = _get_mock_test_cases(base_url, test_type)
        return {
            'test_cases': mock_cases,
            'app_summary': f'Mock analysis of {base_url} — running in demo mode without AI.',
            'test_strategy': f'Generated {len(mock_cases)} test cases covering navigation, auth, forms, UI, and performance.',
            'model_used': 'mock',
        }

    # Real AI call
    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        type_label = {'ui': 'UI/E2E', 'api': 'API', 'both': 'UI and API'}
        test_type_desc = type_label.get(test_type, 'UI')

        extra = ''
        if special_instructions:
            extra = f'\n\nAdditional instructions from the user:\n{special_instructions}'

        message = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=4096,
            system=(
                'You are a senior QA engineer. Generate test cases in pure JSON format. '
                'Do NOT include any markdown, code fences, or explanation — only valid JSON. '
                'The JSON must have this structure: '
                '{"app_summary": "...", "test_strategy": "...", "test_cases": ['
                '{"title": "...", "description": "...", "category": "...", "steps": ["...", "..."]}]}'
            ),
            messages=[
                {
                    'role': 'user',
                    'content': (
                        f'Generate 8-12 comprehensive {test_type_desc} test cases for the web '
                        f'application at: {base_url}\n\n'
                        f'Cover these categories: Navigation, Authentication, Forms, UI, Performance.\n'
                        f'Each test case must have: title, description, category, '
                        f'and detailed steps (list of strings).{extra}'
                    ),
                }
            ],
        )

        raw = message.content[0].text
        data = json.loads(raw)

        return {
            'test_cases': data.get('test_cases', []),
            'app_summary': data.get('app_summary', ''),
            'test_strategy': data.get('test_strategy', ''),
            'model_used': 'claude-sonnet-4-20250514',
        }

    except json.JSONDecodeError as e:
        logger.error("Failed to parse AI response as JSON: %s", e)
        mock_cases = _get_mock_test_cases(base_url, test_type)
        return {
            'test_cases': mock_cases,
            'app_summary': f'AI returned invalid JSON — falling back to mock cases for {base_url}.',
            'test_strategy': 'Fallback mock strategy.',
            'model_used': 'mock (json error fallback)',
        }

    except Exception as e:
        error_type = type(e).__name__
        logger.error("AI service error (%s): %s", error_type, e)
        mock_cases = _get_mock_test_cases(base_url, test_type)
        return {
            'test_cases': mock_cases,
            'app_summary': f'AI error ({error_type}) — falling back to mock cases for {base_url}.',
            'test_strategy': 'Fallback mock strategy.',
            'model_used': f'mock ({error_type} fallback)',
        }
