import uuid

from django.conf import settings
from django.db import models


class TestProject(models.Model):
    """Projeto de teste — contém configuração para gerar e executar testes."""

    TEST_TYPE_CHOICES = [
        ('ui', 'UI'),
        ('api', 'API'),
        ('both', 'Both'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='test_projects',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='test_projects',
    )
    name = models.CharField(max_length=200)
    base_url = models.URLField()
    test_type = models.CharField(max_length=10, choices=TEST_TYPE_CHOICES, default='ui')
    auth_email = models.EmailField(blank=True, default='')
    auth_password = models.CharField(max_length=200, blank=True, default='')
    special_instructions = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Test Project'
        verbose_name_plural = 'Test Projects'

    def __str__(self):
        return f"{self.name} ({self.base_url})"


class TestRun(models.Model):
    """Execução de um conjunto de testes."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        TestProject,
        on_delete=models.CASCADE,
        related_name='runs',
    )
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='test_runs',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_cases = models.IntegerField(default=0)
    passed_cases = models.IntegerField(default=0)
    failed_cases = models.IntegerField(default=0)
    ai_summary = models.TextField(blank=True, default='')
    ai_model_used = models.CharField(max_length=100, blank=True, default='')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_secs = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True, default='')
    celery_task_id = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Test Run'
        verbose_name_plural = 'Test Runs'

    def __str__(self):
        return f"Run {self.id} — {self.status}"

    @property
    def pass_rate(self):
        if self.total_cases == 0:
            return 0
        return round((self.passed_cases / self.total_cases) * 100, 1)

    def recalculate_summary(self):
        cases = self.cases.all()
        self.total_cases = cases.count()
        self.passed_cases = cases.filter(status='passed').count()
        self.failed_cases = cases.filter(status='failed').count()
        self.save(update_fields=['total_cases', 'passed_cases', 'failed_cases'])


class TestCase(models.Model):
    """Caso de teste individual dentro de um TestRun."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        TestRun,
        on_delete=models.CASCADE,
        related_name='cases',
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, default='')
    category = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    steps = models.JSONField(default=list, blank=True)
    error_message = models.TextField(blank=True, default='')
    ai_fix_suggestion = models.TextField(blank=True, default='')
    duration_ms = models.IntegerField(null=True, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Test Case'
        verbose_name_plural = 'Test Cases'

    def __str__(self):
        return f"{self.title} [{self.status}]"
