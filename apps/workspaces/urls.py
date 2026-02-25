from django.urls import path

from . import views

app_name = 'workspaces'

urlpatterns = [
    path('members/', views.members, name='members'),
    path('settings/', views.workspace_settings, name='settings'),
    path('integrations/', views.integrations, name='integrations'),
    path('invite/', views.invite_member, name='invite'),
    path('invite/accept/<uuid:token>/', views.accept_invite, name='accept_invite'),
    path('invite/<uuid:invite_id>/cancel/', views.cancel_invite, name='cancel_invite'),
]
