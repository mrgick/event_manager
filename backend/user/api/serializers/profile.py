from rest_framework import serializers

from event.api.serializers import RegistrationSerializer
from user.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля текущего пользователя."""

    registrations = RegistrationSerializer(
        source='recent_registrations',
        many=True,
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'bonus_balance',
            'registrations',
        ]
