from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'onboarding_completed', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'onboarding_completed')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('SpriteTest', {
            'fields': ('avatar_url', 'bio', 'onboarding_completed'),
        }),
    )
