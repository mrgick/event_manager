from django.db.models import Prefetch, prefetch_related_objects
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from event.models import Registration
from user.api.serializers import UserProfileSerializer


class ProfileAPIView(RetrieveAPIView):
    """АПИ профиля текущего пользователя."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        user = self.request.user
        prefetch_related_objects(
            [user],
            Prefetch(
                'registrations',
                queryset=Registration.objects.order_by('-created_at')[:10],
                to_attr='recent_registrations',
            ),
        )
        return user
