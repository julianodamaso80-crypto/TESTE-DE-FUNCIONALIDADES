from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def onboarding(request):
    """
    Fluxo de onboarding pós-registro.
    Fase 2: apenas marcar como concluído e redirecionar ao dashboard.
    """
    if request.user.onboarding_completed:
        return redirect('dashboard:home')

    if request.method == 'POST':
        request.user.onboarding_completed = True
        request.user.save()
        return redirect('dashboard:home')

    return render(request, 'accounts/onboarding.html', {})


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {
        'user': request.user,
    })
