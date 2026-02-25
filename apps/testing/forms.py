from django import forms

from .models import TestProject


class TestProjectForm(forms.ModelForm):
    class Meta:
        model = TestProject
        fields = [
            'name', 'base_url', 'test_type',
            'auth_email', 'auth_password',
            'special_instructions',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'My Web App Tests',
            }),
            'base_url': forms.URLInput(attrs={
                'class': 'input-field',
                'placeholder': 'https://example.com',
            }),
            'test_type': forms.Select(attrs={
                'class': 'input-field',
            }),
            'auth_email': forms.EmailInput(attrs={
                'class': 'input-field',
                'placeholder': 'test@example.com (optional)',
            }),
            'auth_password': forms.PasswordInput(attrs={
                'class': 'input-field',
                'placeholder': '••••••••',
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'input-field',
                'rows': 4,
                'placeholder': 'Focus on checkout flow, test with Portuguese locale, etc.',
            }),
        }
