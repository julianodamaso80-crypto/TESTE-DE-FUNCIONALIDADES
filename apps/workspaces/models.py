import uuid

from django.conf import settings
from django.db import models


class Plan(models.TextChoices):
    FREE = 'free', 'Free'
    PRO = 'pro', 'Pro'
    ENTERPRISE = 'enterprise', 'Enterprise'


class WorkspaceRole(models.TextChoices):
    OWNER = 'owner', 'Owner'
    ADMIN = 'admin', 'Admin'
    MEMBER = 'member', 'Member'
    VIEWER = 'viewer', 'Viewer'


# Limites por plano (fonte da verdade)
PLAN_LIMITS = {
    Plan.FREE: {
        'test_runs': 50,
        'members': 3,
        'projects': 2,
        'video_retention_days': 7,
        'api_access': False,
        'scheduling': False,
    },
    Plan.PRO: {
        'test_runs': 1000,
        'members': 20,
        'projects': -1,  # unlimited
        'video_retention_days': 30,
        'api_access': True,
        'scheduling': True,
    },
    Plan.ENTERPRISE: {
        'test_runs': -1,  # unlimited
        'members': -1,    # unlimited
        'projects': -1,   # unlimited
        'video_retention_days': 90,
        'api_access': True,
        'scheduling': True,
    },
}


class Workspace(models.Model):
    """
    Workspace = unidade de isolamento de dados no SpriteTest.
    Equivale a uma organização/time.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True, default='')
    logo_url = models.URLField(blank=True, null=True)

    # Plano
    plan = models.CharField(max_length=20, choices=Plan.choices, default=Plan.FREE)

    # Limites por plano (desnormalizados para performance)
    max_test_runs_per_month = models.IntegerField(default=50)
    max_members = models.IntegerField(default=3)
    max_projects = models.IntegerField(default=2)

    # Billing (preparado mas não implementado ainda)
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    plan_expires_at = models.DateTimeField(null=True, blank=True)

    # Membros (M2M com tabela intermediária)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='WorkspaceMembership',
        through_fields=('workspace', 'user'),
        related_name='workspaces',
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Workspace'
        verbose_name_plural = 'Workspaces'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.plan})"

    def get_member_role(self, user):
        """Retorna o role do usuário neste workspace."""
        try:
            return self.memberships.get(user=user).role
        except WorkspaceMembership.DoesNotExist:
            return None

    def is_owner(self, user):
        return self.get_member_role(user) == WorkspaceRole.OWNER

    def is_admin_or_owner(self, user):
        return self.get_member_role(user) in [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]

    @property
    def plan_limits(self):
        """Retorna limites do plano atual."""
        return PLAN_LIMITS.get(self.plan, PLAN_LIMITS[Plan.FREE])

    def save(self, *args, **kwargs):
        """Auto-gerar slug a partir do name e aplicar limites do plano."""
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Workspace.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Aplicar limites do plano
        limits = PLAN_LIMITS.get(self.plan, PLAN_LIMITS[Plan.FREE])
        self.max_test_runs_per_month = limits['test_runs']
        self.max_members = limits['members']
        self.max_projects = limits['projects']

        super().save(*args, **kwargs)


class WorkspaceMembership(models.Model):
    """
    Tabela intermediária: User <-> Workspace com role e status.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    role = models.CharField(
        max_length=20,
        choices=WorkspaceRole.choices,
        default=WorkspaceRole.MEMBER,
    )

    # Convite
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invitations_sent',
    )
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Membro do Workspace'
        verbose_name_plural = 'Membros do Workspace'
        unique_together = [('user', 'workspace')]

    def __str__(self):
        return f"{self.user.email} @ {self.workspace.name} ({self.role})"


class WorkspaceInvitation(models.Model):
    """
    Convite pendente para um workspace (por email).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='invitations',
    )
    email = models.EmailField()
    role = models.CharField(
        max_length=20,
        choices=WorkspaceRole.choices,
        default=WorkspaceRole.MEMBER,
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    accepted = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Convite'
        verbose_name_plural = 'Convites'

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Convite: {self.email} → {self.workspace.name}"
