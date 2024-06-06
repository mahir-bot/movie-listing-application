from django.contrib import admin
from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from dj_rest_auth.views import PasswordResetConfirmView
from core_apps.users.views import CustomUserDetailsView


schema_view = get_schema_view(
    openapi.Info(
        title="Movie API",
        default_version='v1',
        description="API for Movie App",
        contact=openapi.Contact(email="mahirhasan333@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path(settings.ADMIN_URL, admin.site.urls),
    path('', include('core_apps.movies.urls')),
    # path('users/', include('core_apps.users.urls')),
    
    # path('api/v1/auth/', include('dj_rest_auth.urls')),
    # path('api/v1/auth/user/', CustomUserDetailsView.as_view(), name='user_details'),
    # path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    # path('api/v1/auth/password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "Movie App Admin"
admin.site.site_title = "Movie App Admin Portal"
admin.site.index_title = "Welcome to Movie App Portal"