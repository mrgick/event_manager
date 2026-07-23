from rest_framework import serializers

from event.models import Registration


class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации на мероприятие."""

    class Meta:
        model = Registration
        fields = [
            'id',
            'event_id',
            'status',
            'bonus_used',
            'created_at',
        ]
