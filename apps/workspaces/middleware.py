class CurrentWorkspaceMiddleware:
    """
    Resolve o workspace atual da requisição.
    Prioridade: session > primeiro workspace do user.
    Injeta request.workspace para uso em views e templates.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.workspace = None

        if request.user.is_authenticated:
            # Tentar recuperar da sessão
            workspace_id = request.session.get('current_workspace_id')

            if workspace_id:
                from apps.workspaces.models import Workspace
                try:
                    request.workspace = Workspace.objects.get(
                        id=workspace_id,
                        members=request.user,
                    )
                except Workspace.DoesNotExist:
                    request.session.pop('current_workspace_id', None)

            if not request.workspace:
                # Pegar primeiro workspace (pessoal)
                membership = request.user.memberships.select_related('workspace').first()
                if membership:
                    request.workspace = membership.workspace
                    request.session['current_workspace_id'] = str(request.workspace.id)

        response = self.get_response(request)
        return response
