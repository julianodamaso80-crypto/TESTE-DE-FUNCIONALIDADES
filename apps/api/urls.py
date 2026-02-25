from django.urls import path

from . import views, views_dashboard

app_name = 'api'

urlpatterns = [
    # REST API endpoints
    path('v1/projects/', views.ProjectListView.as_view(), name='projects'),
    path('v1/tests/', views.CreateTestView.as_view(), name='create_test'),
    path('v1/runs/<uuid:run_id>/', views.RunDetailView.as_view(), name='run_detail'),
    path('v1/runs/<uuid:run_id>/status/', views.RunStatusView.as_view(), name='run_status'),
    # Dashboard key management
    path('keys/', views_dashboard.api_keys_list, name='keys_list'),
    path('keys/create/', views_dashboard.api_key_create, name='key_create'),
    path('keys/<uuid:key_id>/revoke/', views_dashboard.api_key_revoke, name='key_revoke'),
]
