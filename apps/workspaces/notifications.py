import httpx
import logging

logger = logging.getLogger('spritetest.notifications')


def send_slack_notification(webhook_url: str, run) -> bool:
    if not webhook_url:
        return False
    color = '#a3e635' if run.status == 'passed' else '#f87171'
    status_emoji = '\u2705' if run.status == 'passed' else '\u274c'
    payload = {
        'attachments': [{
            'color': color,
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f"{status_emoji} *{run.project.name}* \u2014 {run.pass_rate}% pass rate",
                    },
                },
                {
                    'type': 'section',
                    'fields': [
                        {'type': 'mrkdwn', 'text': f"*Status:* {run.status.upper()}"},
                        {'type': 'mrkdwn', 'text': f"*URL:* {run.project.base_url}"},
                        {'type': 'mrkdwn', 'text': f"*Testes:* {run.passed_cases}\u2713 {run.failed_cases}\u2717 de {run.total_cases}"},
                        {'type': 'mrkdwn', 'text': f"*Dura\u00e7\u00e3o:* {run.duration_secs}s"},
                    ],
                },
            ],
        }],
    }
    try:
        r = httpx.post(webhook_url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        logger.error(f"Slack failed: {e}")
        return False


def send_discord_notification(webhook_url: str, run) -> bool:
    if not webhook_url:
        return False
    color = 0xa3e635 if run.status == 'passed' else 0xf87171
    status_emoji = '\u2705' if run.status == 'passed' else '\u274c'
    payload = {
        'embeds': [{
            'title': f"{status_emoji} {run.project.name}",
            'color': color,
            'fields': [
                {'name': 'Status', 'value': run.status.upper(), 'inline': True},
                {'name': 'Pass Rate', 'value': f"{run.pass_rate}%", 'inline': True},
                {'name': 'Testes', 'value': f"{run.passed_cases}\u2713 {run.failed_cases}\u2717 / {run.total_cases}", 'inline': True},
                {'name': 'URL', 'value': run.project.base_url, 'inline': False},
            ],
            'footer': {'text': 'SpriteTest'},
        }],
    }
    try:
        r = httpx.post(webhook_url, json=payload, timeout=10)
        return r.status_code in [200, 204]
    except Exception as e:
        logger.error(f"Discord failed: {e}")
        return False


def send_run_notifications(run) -> dict:
    workspace = run.project.workspace
    results = {}
    if workspace.slack_webhook_url:
        results['slack'] = send_slack_notification(workspace.slack_webhook_url, run)
    if workspace.discord_webhook_url:
        results['discord'] = send_discord_notification(workspace.discord_webhook_url, run)
    return results
