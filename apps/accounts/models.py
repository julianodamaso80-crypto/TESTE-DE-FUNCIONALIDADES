import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Usuário customizado do SpriteTest.
    Usa email como identificador principal na UI.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    avatar_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, default='')

    # Onboarding
    onboarding_completed = models.BooleanField(default=False)

    # UI Preferences
    ui_theme = models.CharField(max_length=20, default='dark', choices=[('dark', 'Dark'), ('darker', 'Darker'), ('midnight', 'Midnight')])
    ui_density = models.CharField(max_length=20, default='comfortable', choices=[('compact', 'Compact'), ('comfortable', 'Comfortable'), ('spacious', 'Spacious')])

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # AllAuth usa email como campo de login
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    @property
    def display_name(self):
        """Nome de exibição: first_name ou parte do email."""
        if self.first_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email.split('@')[0]

    @property
    def initials(self):
        """Iniciais para avatar fallback."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.email[0].upper()
