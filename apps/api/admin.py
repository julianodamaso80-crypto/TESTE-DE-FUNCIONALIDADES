from django.contrib import admin

from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_prefix', 'workspace', 'is_active', 'last_used_at', 'created_at')
    list_filter = ('is_active',)
    readonly_fields = ('key_prefix', 'key_hash', 'created_at')
