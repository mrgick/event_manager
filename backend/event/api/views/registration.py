from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from event.api.serializers import RegistrationSerializer
from event.services import CancelRegistrationService


class CancelRegistrationAPIView(GenericAPIView):
    """АПИ для отмены регистрации."""

    permission_classes = [IsAuthenticated]
    serializer_class = RegistrationSerializer

    @extend_schema(
        request=None,
        responses={
            status.HTTP_200_OK: RegistrationSerializer,
        },
    )
    def post(self, request, pk, *args, **kwargs):
        registration = CancelRegistrationService(
            registration_id=pk, user_id=request.user.pk
        ).execute()
        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_200_OK)
