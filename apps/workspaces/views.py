import uuid
from datetime import timedelta

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.workspaces.models import WorkspaceInvitation, WorkspaceMembership


@login_required
def members(request):
    memberships = (
        request.workspace.memberships.select_related('user').all()
        if request.workspace
        else []
    )
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
                project = type(
                    'P', (), {'name': 'SpriteTest', 'base_url': 'https://spritetest.io'}
                )()
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


@login_required
def invite_member(request):
    workspace = request.workspace
    membership = workspace.memberships.filter(user=request.user).first()
    if not membership or membership.role not in ['owner', 'admin']:
        messages.error(request, 'Sem permissão para convidar membros.')
        return redirect('workspaces:settings')

    limits = workspace.get_plan_limits()
    current_count = workspace.memberships.count()
    if current_count >= limits['members']:
        messages.error(
            request, f'Limite de {limits["members"]} membros atingido. Faça upgrade.'
        )
        return redirect('billing:pricing')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        role = request.POST.get('role', 'member')
        if not email:
            messages.error(request, 'Email obrigatório.')
            return redirect('workspaces:invite')

        if workspace.memberships.filter(user__email=email).exists():
            messages.error(request, 'Este usuário já é membro.')
            return redirect('workspaces:invite')

        inv, created = WorkspaceInvitation.objects.get_or_create(
            workspace=workspace,
            email=email,
            defaults={'invited_by': request.user, 'role': role},
        )
        if not created:
            inv.token = uuid.uuid4()
            inv.accepted = False
            inv.expires_at = timezone.now() + timedelta(days=7)
            inv.save()

        invite_url = request.build_absolute_uri(
            f'/workspace/invite/accept/{inv.token}/'
        )
        try:
            from django.core.mail import EmailMultiAlternatives
            from django.template.loader import render_to_string

            context = {
                'invited_by': request.user.display_name or request.user.email,
                'workspace_name': workspace.name,
                'invite_url': invite_url,
            }
            text_body = f"Você foi convidado para {workspace.name}.\nAcesse: {invite_url}"
            html_body = render_to_string('emails/invite.html', context)
            msg = EmailMultiAlternatives(
                subject=f'Convite para {workspace.name} no SpriteTest',
                body=text_body,
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=True)
        except Exception:
            pass

        messages.success(request, f'Convite enviado para {email}! URL: {invite_url}')
        return redirect('workspaces:settings')

    pending = WorkspaceInvitation.objects.filter(workspace=workspace, accepted=False)
    return render(request, 'workspaces/invite.html', {
        'workspace': workspace,
        'pending_invites': pending,
        'slots_remaining': limits['members'] - current_count,
    })


def accept_invite(request, token):
    inv = get_object_or_404(WorkspaceInvitation, token=token, accepted=False)

    if inv.is_expired:
        messages.error(request, 'Convite expirado.')
        return redirect('core:home')

    if not request.user.is_authenticated:
        request.session['pending_invite_token'] = str(token)
        return redirect(f'/auth/signup/?next=/workspace/invite/accept/{token}/')

    if request.user.email.lower() != inv.email.lower():
        messages.error(request, f'Este convite é para {inv.email}.')
        return redirect('dashboard:home')

    WorkspaceMembership.objects.get_or_create(
        workspace=inv.workspace,
        user=request.user,
        defaults={'role': inv.role},
    )
    inv.accepted = True
    inv.save(update_fields=['accepted'])
    messages.success(request, f'Bem-vindo ao workspace {inv.workspace.name}!')
    return redirect('dashboard:home')


@login_required
@require_POST
def cancel_invite(request, invite_id):
    inv = get_object_or_404(
        WorkspaceInvitation, id=invite_id, workspace=request.workspace
    )
    inv.delete()
    messages.success(request, 'Convite cancelado.')
    return redirect('workspaces:invite')
