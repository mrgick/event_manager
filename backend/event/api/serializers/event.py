from rest_framework import serializers

from event.models import Event


class EventCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания мероприятия."""

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'start_time',
            'end_time',
            'address',
            'max_attendees',
            'price',
            'owner',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'owner',
            'status',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError(
                {'end_time': 'Дата и время окончания должны быть позже даты и времени начала.'}
            )
        return attrs


class EventListSerializer(serializers.ModelSerializer):
    """Сериализатор списка мероприятий."""

    current_attendees = serializers.IntegerField(
        read_only=True,
        label='Количество подтвержденных регистраций',
    )
    average_rating = serializers.FloatField(
        read_only=True,
        label='Средний рейтинг',
    )
    is_full = serializers.BooleanField(
        read_only=True,
        label='Заполненность мероприятия',
    )

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'start_time',
            'end_time',
            'address',
            'max_attendees',
            'price',
            'owner_id',
            'status',
            'created_at',
            'updated_at',
            'current_attendees',
            'average_rating',
            'is_full',
        ]
