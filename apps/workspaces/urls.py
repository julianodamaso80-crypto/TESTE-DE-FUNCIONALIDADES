from django.urls import path

from . import views

app_name = 'workspaces'

urlpatterns = [
    path('members/', views.members, name='members'),
    path('settings/', views.settings, name='settings'),
    path('integrations/', views.integrations, name='integrations'),
]
