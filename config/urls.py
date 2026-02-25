from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('auth/', include('allauth.urls')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('workspace/', include('apps.workspaces.urls', namespace='workspaces')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('testing/', include('apps.testing.urls', namespace='testing')),
    path('api/', include('apps.api.urls', namespace='api')),
]

handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
