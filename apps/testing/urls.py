from django.urls import path

from . import views

app_name = 'testing'

urlpatterns = [
    path('new/', views.new_test, name='new_test'),
    path('projects/', views.project_list, name='project_list'),
    path('runs/<uuid:run_id>/', views.run_detail, name='run_detail'),
    path('runs/<uuid:run_id>/execute/', views.execute_run, name='execute_run'),
]
