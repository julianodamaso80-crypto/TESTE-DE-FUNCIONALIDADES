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
    return render(request, 'accounts/profile.html', {
        'user': request.user,
    })
