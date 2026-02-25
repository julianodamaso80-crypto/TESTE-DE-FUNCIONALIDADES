import logging

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

logger = logging.getLogger('spritetest.auth')


class CustomAccountAdapter(DefaultAccountAdapter):

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """Em desenvolvimento, não enviar email (apenas logar)."""
        if settings.DEBUG:
            logger.info(
                f"[DEV] Email confirmation for {emailconfirmation.email_address.email}: "
                f"key={emailconfirmation.key}"
            )
        else:
            super().send_confirmation_mail(request, emailconfirmation, signup)

    def save_user(self, request, user, form, commit=True):
        """Salvar campos extras do signup."""
        user = super().save_user(request, user, form, commit=False)
        user.first_name = form.cleaned_data.get('first_name', '')
        user.last_name = form.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user
