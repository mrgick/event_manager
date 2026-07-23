from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from event.models import Event, Registration
from event.models.choices import EventStatus, RegistrationStatus
from user.models import User


class RegisterService:
    """Сервис регистрации на мероприятие."""

    def __init__(self, event_id: int, user_id: int):
        self._event_id = event_id
        self._user_id = user_id

    @transaction.atomic
    def execute(self) -> Registration:
        event = get_object_or_404(
            Event.objects.select_for_update(),
            id=self._event_id,
        )
        user = User.objects.select_for_update().get(pk=self._user_id)
        self._validate(event, user)
        return self._create_registration(event, user)

    def _validate(self, event: Event, user: User) -> None:
        errors = defaultdict(list)
        self._validate_event_is_published(event, errors)
        self._validate_event_not_finished(event, errors)
        self._validate_user_not_registered(event, user, errors)
        self._validate_user_is_not_owner(event, user, errors)
        self._validate_event_has_available_places(event, errors)
        if errors:
            raise ValidationError(errors)

    def _validate_event_is_published(
        self,
        event: Event,
        errors: dict[str, list[str]],
    ) -> None:
        if event.status != EventStatus.PUBLISHED:
            errors['non_field_errors'].append(
                'Регистрация доступна только на опубликованные мероприятия.'
            )

    def _validate_event_not_finished(
        self,
        event: Event,
        errors: dict[str, list[str]],
    ) -> None:
        if event.end_time <= timezone.now():
            errors['non_field_errors'].append('Мероприятие уже завершено.')

    def _validate_user_not_registered(
        self,
        event: Event,
        user: User,
        errors: dict[str, list[str]],
    ) -> None:
        if Registration.objects.filter(user=user, event=event).exists():
            errors['non_field_errors'].append('Вы уже зарегистрированы на это мероприятие.')

    def _validate_user_is_not_owner(
        self,
        event: Event,
        user: User,
        errors: dict[str, list[str]],
    ) -> None:
        if event.owner_id == user.pk:
            errors['non_field_errors'].append('Вы являетесь организатором мероприятия.')

    def _validate_event_has_available_places(
        self,
        event: Event,
        errors: dict[str, list[str]],
    ) -> None:
        if event.max_attendees is not None:
            confirmed_count = Registration.objects.filter(
                event=event,
                status=RegistrationStatus.CONFIRMED,
            ).count()
            if confirmed_count >= event.max_attendees:
                errors['non_field_errors'].append('На мероприятие больше нет свободных мест.')

    def _create_registration(
        self,
        event: Event,
        user: User,
    ) -> Registration:
        if event.price > Decimal('0.00'):
            if user.bonus_balance >= event.price:
                user.bonus_balance -= event.price
                user.save(update_fields=['bonus_balance'])
                return Registration.objects.create(
                    user=user,
                    event=event,
                    status=RegistrationStatus.CONFIRMED,
                    bonus_used=True,
                )

            return Registration.objects.create(
                user=user,
                event=event,
                status=RegistrationStatus.PENDING,
            )

        User.objects.filter(pk=event.owner_id).update(
            bonus_balance=F('bonus_balance') + Decimal('5.00')
        )
        return Registration.objects.create(
            user=user,
            event=event,
            status=RegistrationStatus.CONFIRMED,
        )
