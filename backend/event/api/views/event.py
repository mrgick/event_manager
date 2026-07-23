from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from event.api.serializers import (
    EventCreateSerializer,
    EventListSerializer,
    RegistrationSerializer,
)
from event.models import Event
from event.services import (
    EventListService,
    RegisterService,
)


class EventViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """АПИ для работы с мероприятиями."""

    queryset = Event.objects.all()
    serializer_map = {
        'list': EventListSerializer,
        'create': EventCreateSerializer,
        'register': RegistrationSerializer,
    }

    def get_serializer_class(self):
        if self.action in self.serializer_map:
            return self.serializer_map[self.action]
        return super().get_serializer_class()

    def get_permissions(self):
        permission_classes = [AllowAny] if self.action == 'list' else [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = EventListService().execute()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=None,
        responses={
            status.HTTP_201_CREATED: RegistrationSerializer(),
        },
    )
    @action(detail=True, methods=('post',), url_path='register')
    def register(self, request, pk=None, *args, **kwargs):
        """АПИ для регистрации на мероприятие."""
        registration = RegisterService(event_id=pk, user_id=request.user.pk).execute()
        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
