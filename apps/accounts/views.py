from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def onboarding(request):
    """Fluxo de onboarding pós-registro com stepper de 3 passos."""
    user = request.user
    if user.onboarding_completed:
        return redirect('dashboard:home')

    steps = {
        'profile': bool(user.first_name),
        'first_test': user.triggered_runs.exists() if hasattr(user, 'triggered_runs') else False,
        'invite': request.workspace.memberships.count() > 1 if request.workspace else False,
    }

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'complete_profile':
            name = request.POST.get('display_name', '').strip()
            if name:
                parts = name.split(' ', 1)
                user.first_name = parts[0]
                user.last_name = parts[1] if len(parts) > 1 else ''
                user.save(update_fields=['first_name', 'last_name'])
                messages.success(request, 'Perfil atualizado!')
        elif action == 'skip_onboarding':
            user.onboarding_completed = True
            user.save(update_fields=['onboarding_completed'])
            return redirect('dashboard:home')
        return redirect('accounts:onboarding')

    return render(request, 'accounts/onboarding.html', {
        'steps': steps,
        'workspace': request.workspace,
    })


@login_required
def profile(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            user = request.user
            display_name = request.POST.get('display_name', '').strip()
            if display_name:
                parts = display_name.split(None, 1)
                user.first_name = parts[0]
                user.last_name = parts[1] if len(parts) > 1 else ''
            else:
                user.first_name = ''
                user.last_name = ''
            new_email = request.POST.get('email', '').strip()
            if new_email and new_email != user.email:
                from .models import User as UserModel
                if not UserModel.objects.filter(email=new_email).exclude(id=user.id).exists():
                    user.email = new_email
                    user.username = new_email
                else:
                    messages.error(request, 'Este email já está em uso.')
                    return redirect('accounts:profile')
            user.save()
            messages.success(request, 'Perfil atualizado!')
        elif action == 'change_password':
            from django.contrib.auth import update_session_auth_hash
            old_pw = request.POST.get('old_password')
            new_pw = request.POST.get('new_password')
            confirm_pw = request.POST.get('confirm_password')
            if not request.user.check_password(old_pw):
                messages.error(request, 'Senha atual incorreta.')
            elif new_pw != confirm_pw:
                messages.error(request, 'Senhas não coincidem.')
            elif len(new_pw) < 8:
                messages.error(request, 'Senha deve ter pelo menos 8 caracteres.')
            else:
                request.user.set_password(new_pw)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Senha alterada com sucesso!')
        return redirect('accounts:profile')

    workspaces = request.user.workspaces.all()
    api_keys_count = 0
    try:
        from apps.api.models import APIKey
        api_keys_count = APIKey.objects.filter(
            created_by=request.user, is_active=True
        ).count()
    except Exception:
        pass

    return render(request, 'accounts/profile.html', {
        'workspaces': workspaces,
        'api_keys_count': api_keys_count,
    })
