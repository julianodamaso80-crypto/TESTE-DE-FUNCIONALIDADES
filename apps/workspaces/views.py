from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def members(request):
    memberships = request.workspace.memberships.select_related('user').all() if request.workspace else []
    return render(request, 'workspaces/members.html', {
        'members': memberships,
    })


@login_required
def settings(request):
    return render(request, 'workspaces/settings.html', {})


@login_required
def integrations(request):
    workspace = request.workspace
    if request.method == 'POST':
        workspace.slack_webhook_url = request.POST.get('slack_webhook_url', '').strip()
        workspace.discord_webhook_url = request.POST.get('discord_webhook_url', '').strip()
        workspace.save(update_fields=['slack_webhook_url', 'discord_webhook_url'])
        messages.success(request, 'Integrações salvas!')
        if request.POST.get('test_slack') and workspace.slack_webhook_url:
            from apps.workspaces.notifications import send_slack_notification

            class FakeRun:
                project = type('P', (), {'name': 'SpriteTest', 'base_url': 'https://spritetest.io'})()
                status = 'passed'
                pass_rate = 100
                passed_cases = 8
                failed_cases = 0
                total_cases = 8
                duration_secs = 12

            ok = send_slack_notification(workspace.slack_webhook_url, FakeRun())
            if ok:
                messages.success(request, 'Slack OK!')
            else:
                messages.error(request, 'Slack falhou — verifique a URL do webhook.')
        return redirect('workspaces:integrations')
    return render(request, 'workspaces/integrations.html', {'workspace': workspace})
