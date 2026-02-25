from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.analytics import track
from .models import APIKey


@login_required
def api_keys_list(request):
    keys = APIKey.objects.filter(workspace=request.workspace)
    return render(request, 'api/keys_list.html', {'keys': keys})


@login_required
def api_key_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Nome obrigatório')
            return redirect('api:keys_list')
        api_key, raw_key = APIKey.generate(request.workspace, request.user, name)
        track(str(request.user.id), 'api_key_created', {})
        return render(request, 'api/key_created.html', {
            'api_key': api_key, 'raw_key': raw_key,
        })
    return render(request, 'api/key_create.html')


@login_required
@require_POST
def api_key_revoke(request, key_id):
    key = get_object_or_404(APIKey, id=key_id, workspace=request.workspace)
    key.is_active = False
    key.save(update_fields=['is_active'])
    messages.success(request, f'API Key "{key.name}" revogada')
    return redirect('api:keys_list')
