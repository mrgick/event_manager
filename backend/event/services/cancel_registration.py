from collections import defaultdict
from datetime import timedelta

from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from event.models import Registration
from event.models.choices import RegistrationStatus
from user.models import User


class CancelRegistrationService:
    """Сервис отмены регистрации на мероприятие."""

    def __init__(self, registration_id: int, user_id: int):
        self._registration_id = registration_id
        self._user_id = user_id

    @transaction.atomic
    def execute(self) -> Registration:
        registration = get_object_or_404(
            Registration.objects.select_for_update().select_related('event'),
            pk=self._registration_id,
            user_id=self._user_id,
        )
        self._validate(registration)
        self._update_user_balance(registration)
        self._cancel_registration(registration)
        return registration

    def _validate(self, registration: Registration) -> None:
        errors = defaultdict(list)

        self._validate_registration_status(registration, errors)
        self._validate_registration_start_time(registration, errors)

        if errors:
            raise ValidationError(errors)

    def _validate_registration_status(
        self,
        registration: Registration,
        errors: dict[str, list[str]],
    ) -> None:
        if registration.status == RegistrationStatus.CANCELED:
            errors['non_field_errors'].append('Регистрация уже отменена.')

    def _validate_registration_start_time(
        self,
        registration: Registration,
        errors: dict[str, list[str]],
    ) -> None:
        deadline = registration.event.start_time - timedelta(days=2)
        if timezone.now() > deadline:
            errors['non_field_errors'].append(
                'Отмена регистрации разрешена только за 2 дня до начала мероприятия.'
            )

    def _update_user_balance(self, registration: Registration) -> None:
        if registration.bonus_used:
            User.objects.filter(pk=self._user_id).update(
                bonus_balance=(F('bonus_balance') + registration.event.price),
            )

    def _cancel_registration(self, registration: Registration) -> None:
        registration.status = RegistrationStatus.CANCELED
        registration.save(update_fields=('status',))
