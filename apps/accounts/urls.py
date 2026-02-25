from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('onboarding/', views.onboarding, name='onboarding'),
    path('profile/', views.profile, name='profile'),
    path('preferences/', views.update_preferences, name='update_preferences'),
]
