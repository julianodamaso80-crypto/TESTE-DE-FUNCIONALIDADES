from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect

from .models import Workspace, WorkspaceRole


class WorkspaceRequiredMixin(LoginRequiredMixin):
    """
    Mixin base para todas as views dentro de um workspace.
    Garante: usuário autenticado + pertence ao workspace.
    """
    workspace_slug_url_kwarg = 'workspace_slug'
    required_role = None  # None = qualquer membro

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return response

        workspace_slug = kwargs.get(self.workspace_slug_url_kwarg)
        if workspace_slug:
            self.workspace = get_object_or_404(
                Workspace,
                slug=workspace_slug,
                members=request.user,
            )
            request.workspace = self.workspace
            request.session['current_workspace_id'] = str(self.workspace.id)

            if self.required_role:
                role = self.workspace.get_member_role(request.user)
                allowed = {
                    WorkspaceRole.VIEWER: [WorkspaceRole.VIEWER, WorkspaceRole.MEMBER, WorkspaceRole.ADMIN, WorkspaceRole.OWNER],
                    WorkspaceRole.MEMBER: [WorkspaceRole.MEMBER, WorkspaceRole.ADMIN, WorkspaceRole.OWNER],
                    WorkspaceRole.ADMIN: [WorkspaceRole.ADMIN, WorkspaceRole.OWNER],
                    WorkspaceRole.OWNER: [WorkspaceRole.OWNER],
                }
                if role not in allowed.get(self.required_role, []):
                    messages.error(request, 'Você não tem permissão para realizar esta ação.')
                    return redirect('workspaces:detail', workspace_slug=workspace_slug)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'workspace'):
            context['workspace'] = self.workspace
            context['user_role'] = self.workspace.get_member_role(self.request.user)
        return context
