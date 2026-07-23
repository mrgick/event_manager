from datetime import timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from event.models.choices import RegistrationStatus
from event.tests.factories import EventFactory, RegistrationFactory


@pytest.mark.django_db
class TestCancelRegistration:
    def get_url(self, registration):
        return reverse(
            'cancel-registration',
            kwargs={'pk': registration.pk},
        )

    def _serialize_registration(self, registration):
        return {
            'id': registration.id,
            'event_id': registration.event.id,
            'status': registration.status,
            'bonus_used': registration.bonus_used,
            'created_at': registration.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        }

    @pytest.fixture
    def registered_user(self, user):
        user.bonus_balance = Decimal('100.00')
        user.save(update_fields=('bonus_balance',))
        user.refresh_from_db()
        return user

    @pytest.fixture
    def event(self):
        return EventFactory.create(price=Decimal('50.00'))

    @pytest.fixture
    def registration(self, registered_user, event):
        return RegistrationFactory.create(user=registered_user, event=event, bonus_used=True)

    def test_cancel_registration_with_used_bonuses(
        self, registered_user, event, registration, authorized_client
    ):
        """Тест возврата списанных бонусов при отмене регистрации."""

        response = authorized_client.post(self.get_url(registration))

        registration.refresh_from_db()
        registered_user.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.data == self._serialize_registration(registration)
        assert registered_user.bonus_balance == Decimal('150.00')  # 100.00 + 50.00
        assert registration.status == RegistrationStatus.CANCELED

    def test_cancel_registration_without_used_bonuses(
        self, registered_user, event, registration, authorized_client
    ):
        """Тест отмены регистрации без использования бонусов."""

        registration.bonus_used = False
        registration.save(update_fields=('bonus_used',))

        response = authorized_client.post(self.get_url(registration))

        registration.refresh_from_db()
        registered_user.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.data == self._serialize_registration(registration)
        assert registered_user.bonus_balance == Decimal('100.00')
        assert registration.status == RegistrationStatus.CANCELED

    def test_errors(self, registered_user, event, registration, authorized_client):
        """Тест получения ошибок при отмене регистрации."""

        # 1. регистрация уже отменена
        registration.status = RegistrationStatus.CANCELED
        registration.save(update_fields=('status',))

        response = authorized_client.post(self.get_url(registration))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['non_field_errors'][0] == 'Регистрация уже отменена.'
        registration.refresh_from_db()
        assert registration.status == RegistrationStatus.CANCELED

        # 2. мероприятие начнется менее чем через 2 дня
        registration.status = RegistrationStatus.CONFIRMED
        registration.save(update_fields=('status',))
        event.start_time = timezone.now() + timedelta(days=1)
        event.save(update_fields=('start_time',))

        response = authorized_client.post(self.get_url(registration))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['non_field_errors'][0] == (
            'Отмена регистрации разрешена только за 2 дня до начала мероприятия.'
        )
        registration.refresh_from_db()
        assert registration.status == RegistrationStatus.CONFIRMED

        # 3. регистрация не принадлежит пользователю
        another_user_registration = RegistrationFactory.create()
        response = authorized_client.post(self.get_url(another_user_registration))
        assert response.status_code == status.HTTP_404_NOT_FOUND
