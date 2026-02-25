from allauth.account.forms import SignupForm
from django import forms


class CustomSignupForm(SignupForm):
    """
    Formulário de registro com campos extras.
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Seu nome',
            'autocomplete': 'given-name',
        }),
        label='Nome',
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Sobrenome',
            'autocomplete': 'family-name',
        }),
        label='Sobrenome',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customizar campos do AllAuth
        self.fields['email'].widget.attrs.update({
            'class': 'input-field',
            'placeholder': 'seu@email.com',
            'autocomplete': 'email',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'input-field',
            'placeholder': '\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'input-field',
            'placeholder': '\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022',
        })
        # Remover campo username da UI (será gerado automaticamente)
        if 'username' in self.fields:
            del self.fields['username']

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.save()
        return user
