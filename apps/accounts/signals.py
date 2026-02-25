from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_personal_workspace(sender, instance, created, **kwargs):
    """
    Ao criar novo usuário, automaticamente criar workspace pessoal.
    """
    if created:
        from apps.workspaces.models import Workspace, WorkspaceMembership, WorkspaceRole
        from django.utils.text import slugify

        workspace_name = f"{instance.display_name}'s Workspace"
        base_slug = slugify(f"{instance.email.split('@')[0]}-workspace")

        # Garantir slug único
        slug = base_slug
        counter = 1
        while Workspace.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        workspace = Workspace.objects.create(
            name=workspace_name,
            slug=slug,
            plan='free',
        )

        WorkspaceMembership.objects.create(
            user=instance,
            workspace=workspace,
            role=WorkspaceRole.OWNER,
        )

        from apps.core.analytics import identify, track
        try:
            identify(str(instance.id), {'email': instance.email, 'plan': 'free'})
            track(str(instance.id), 'user_signed_up', {})
        except Exception:
            pass
