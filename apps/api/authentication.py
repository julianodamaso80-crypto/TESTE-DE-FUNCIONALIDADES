import hashlib

from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer spt_'):
            return None

        raw_key = auth_header.split(' ', 1)[1]
        prefix = raw_key[:8]

        from apps.api.models import APIKey

        try:
            api_key = APIKey.objects.select_related('workspace').get(
                key_prefix=prefix, is_active=True
            )
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('API Key inválida')

        if api_key.expires_at and api_key.expires_at < timezone.now():
            raise AuthenticationFailed('API Key expirada')

        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        if key_hash != api_key.key_hash:
            raise AuthenticationFailed('API Key inválida')

        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=['last_used_at'])

        request.workspace = api_key.workspace
        return (api_key.created_by, api_key)
