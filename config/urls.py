from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from apps.core.sitemaps import StaticViewSitemap, PricingSitemap

sitemaps = {'static': StaticViewSitemap, 'pricing': PricingSitemap}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('auth/', include('allauth.urls')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('workspace/', include('apps.workspaces.urls', namespace='workspaces')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('testing/', include('apps.testing.urls', namespace='testing')),
    path('api/', include('apps.api.urls', namespace='api')),
    path('billing/', include('apps.billing.urls', namespace='billing')),
]

handler404 = 'apps.core.views.handler404'
handler500 = 'apps.core.views.handler500'

urlpatterns += [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='core/robots.txt', content_type='text/plain')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
