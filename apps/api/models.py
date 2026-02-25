import hashlib
import secrets
import uuid

from django.conf import settings
from django.db import models


class APIKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        'workspaces.Workspace', on_delete=models.CASCADE, related_name='api_keys'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    name = models.CharField(max_length=100)
    key_prefix = models.CharField(max_length=8, unique=True)
    key_hash = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'API Key'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"

    @classmethod
    def generate(cls, workspace, created_by, name):
        raw_key = f"spt_{secrets.token_urlsafe(32)}"
        prefix = raw_key[:8]
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        api_key = cls.objects.create(
            workspace=workspace,
            created_by=created_by,
            name=name,
            key_prefix=prefix,
            key_hash=key_hash,
        )
        return api_key, raw_key

    def verify(self, raw_key: str) -> bool:
        return hashlib.sha256(raw_key.encode()).hexdigest() == self.key_hash
