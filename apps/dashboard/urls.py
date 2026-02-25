from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('new/', views.new_test, name='new_test'),
    path('tests/', views.tests, name='tests'),
    path('runs/', views.test_runs, name='runs'),
    path('monitoring/', views.monitoring, name='monitoring'),
]
