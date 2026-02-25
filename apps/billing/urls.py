from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('pricing/', views.pricing, name='pricing'),
    path('checkout/<str:plan>/', views.checkout, name='checkout'),
    path('success/', views.success, name='success'),
    path('manage/', views.manage_billing, name='manage'),
    path('webhook/', views.webhook, name='webhook'),
]
