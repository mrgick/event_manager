from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user.api.views import ProfileAPIView

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    path('profile/me/', ProfileAPIView.as_view(), name='profile-me'),
]
