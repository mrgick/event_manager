from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

api_urlpatterns = [
    path('events/', include('event.urls'), name='events'),
    path('', include('user.urls'), name='users'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'schema/swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger',
    ),
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('admin/', admin.site.urls),
]
