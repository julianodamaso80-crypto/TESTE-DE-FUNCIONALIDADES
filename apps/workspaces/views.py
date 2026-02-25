from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def members(request):
    memberships = request.workspace.memberships.select_related('user').all() if request.workspace else []
    return render(request, 'workspaces/members.html', {
        'members': memberships,
    })


@login_required
def settings(request):
    return render(request, 'workspaces/settings.html', {})
