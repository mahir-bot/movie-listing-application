from django.contrib import admin
from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('', include('core_apps.movies.urls')),
    path('account/', include('core_apps.account.urls')),
    path('dashboard/', include('core_apps.dashboard.urls')),
    # path('', include('django.contrib.auth.urls')),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
