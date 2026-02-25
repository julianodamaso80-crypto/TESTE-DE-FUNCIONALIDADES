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
def workspace_settings(request):
    workspace = request.workspace
    membership = workspace.memberships.filter(user=request.user).first()
    is_owner = membership and membership.role == 'owner'

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_name' and is_owner:
            name = request.POST.get('name', '').strip()
            if name:
                workspace.name = name
                workspace.save(update_fields=['name'])
                messages.success(request, 'Nome atualizado!')
        elif action == 'remove_member' and is_owner:
            member_id = request.POST.get('member_id')
            from apps.workspaces.models import WorkspaceMembership
            m = WorkspaceMembership.objects.filter(
                id=member_id, workspace=workspace
            ).exclude(user=request.user).first()
            if m:
                m.delete()
                messages.success(request, 'Membro removido.')
        elif action == 'leave_workspace' and not is_owner:
            workspace.memberships.filter(user=request.user).delete()
            messages.success(request, 'Você saiu do workspace.')
            return redirect('dashboard:home')
        return redirect('workspaces:settings')

    members_list = workspace.memberships.select_related('user').all()
    return render(request, 'workspaces/settings.html', {
        'workspace': workspace,
        'members': members_list,
        'is_owner': is_owner,
        'plan_limits': workspace.get_plan_limits(),
    })


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
