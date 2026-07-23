from django.urls import path
from rest_framework import routers

from event.api.views import CancelRegistrationAPIView, EventViewSet

router = routers.SimpleRouter()

router.register('', EventViewSet, basename='events')

urlpatterns = [
    path(
        'cancel-registration/<int:pk>/',
        CancelRegistrationAPIView.as_view(),
        name='cancel-registration',
    ),
]
urlpatterns += router.urls
