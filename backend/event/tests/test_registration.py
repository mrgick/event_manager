from datetime import timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from event.models import Registration
from event.models.choices import EventStatus, RegistrationStatus
from event.tests.factories import EventFactory, RegistrationFactory


@pytest.mark.django_db
class TestRegisterService:
    def get_url(self, event):
        return reverse('events-register', kwargs={'pk': event.id})

    def test_without_enough_bonuses_registration(self, user, authorized_client):
        """Тест платной регистрации при нулевом балансе."""

        event = EventFactory.create(price=Decimal('10.00'))

        response = authorized_client.post(self.get_url(event))
        assert response.status_code == status.HTTP_201_CREATED

        registration = Registration.objects.get(pk=response.data['id'])
        user.refresh_from_db()
        assert registration.status == RegistrationStatus.PENDING
        assert registration.bonus_used is False
        assert user.bonus_balance == Decimal('0.00')

    def test_free_event_registration(self, user, authorized_client):
        """Тест бесплатной регистрации."""

        initial_balance = Decimal('10.00')
        user.bonus_balance = initial_balance
        user.save(update_fields=('bonus_balance',))
        event = EventFactory.create(price=Decimal('0.00'))
        owner_initial_balance = event.owner.bonus_balance

        response = authorized_client.post(self.get_url(event))
        assert response.status_code == status.HTTP_201_CREATED

        registration = Registration.objects.get(pk=response.data['id'])
        user.refresh_from_db()
        event.owner.refresh_from_db()
        assert registration.status == RegistrationStatus.CONFIRMED
        assert registration.bonus_used is False
        assert user.bonus_balance == initial_balance
        assert event.owner.bonus_balance == owner_initial_balance + Decimal('5.00')

    def test_errors(self, user, authorized_client):
        """Тест получения ошибок при регистрации."""

        # 1. Отсутствие свободных мест
        event = EventFactory.create(max_attendees=2)
        RegistrationFactory.create_batch(
            2,
            event=event,
            status=RegistrationStatus.CONFIRMED,
        )

        response = authorized_client.post(self.get_url(event))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert response.data['non_field_errors'][0] == 'На мероприятие больше нет свободных мест.'
        assert not Registration.objects.filter(
            event=event,
            user=user,
        ).exists()

        # 2. Неопубликованное мероприятие

        event = EventFactory.create(status=EventStatus.DRAFT)

        response = authorized_client.post(self.get_url(event))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert response.data['non_field_errors'][0] == (
            'Регистрация доступна только на опубликованные мероприятия.'
        )
        assert not Registration.objects.filter(
            event=event,
            user=user,
        ).exists()

        # 3. Завершившееся мероприятие

        event = EventFactory.create(
            start_time=timezone.now() - timedelta(days=2),
            end_time=timezone.now() - timedelta(days=1),
        )

        response = authorized_client.post(self.get_url(event))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert response.data['non_field_errors'][0] == 'Мероприятие уже завершено.'
        assert not Registration.objects.filter(
            event=event,
            user=user,
        ).exists()

        # 4. Повторная регистрация

        event = EventFactory.create()
        RegistrationFactory.create(event=event, user=user)

        response = authorized_client.post(self.get_url(event))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert response.data['non_field_errors'][0] == 'Вы уже зарегистрированы на это мероприятие.'
        assert (
            Registration.objects.filter(
                event=event,
                user=user,
            ).count()
            == 1
        )

        # 5. Регистрация организатора на свое мероприятие

        event = EventFactory.create(owner=user)

        response = authorized_client.post(self.get_url(event))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['non_field_errors'][0] == 'Вы являетесь организатором мероприятия.'
        assert not Registration.objects.filter(
            event=event,
            user=user,
        ).exists()
