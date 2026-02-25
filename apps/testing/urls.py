from django.urls import path

from . import views

app_name = 'testing'

urlpatterns = [
    path('new/', views.new_test, name='new_test'),
    path('projects/', views.project_list, name='project_list'),
    path('runs/<uuid:run_id>/', views.run_detail, name='run_detail'),
    path('runs/<uuid:run_id>/execute/', views.execute_run, name='execute_run'),
    path('runs/<uuid:run_id>/report/', views.run_report, name='run_report'),
    path('runs/<uuid:run_id>/share/', views.toggle_share, name='toggle_share'),
    path('public/<uuid:share_token>/', views.run_public, name='run_public'),
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/project/<uuid:project_id>/', views.schedule_create, name='schedule_create'),
    path('schedules/<uuid:schedule_id>/toggle/', views.schedule_toggle, name='schedule_toggle'),
]
