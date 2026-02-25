from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('health/', views.health_check, name='health_check'),
    path('status/', views.status_page, name='status_page'),
    path('status.json', views.status_api, name='status_api'),
]
