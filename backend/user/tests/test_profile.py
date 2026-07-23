from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from event.models import Registration
from event.tests.factories import RegistrationFactory


@pytest.mark.django_db
class TestProfile:
    def get_url(self):
        return reverse('profile-me')

    def _serialize_profile(self, user, registrations):
        return {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': str(user.phone_number),
            'bonus_balance': str(user.bonus_balance),
            'registrations': [
                {
                    'id': registration.id,
                    'event_id': registration.event.id,
                    'status': registration.status,
                    'bonus_used': registration.bonus_used,
                    'created_at': registration.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                }
                for registration in registrations
            ],
        }

    def test_get_profile(self, user, authorized_client):
        """Тест получения профиля без регистраций."""

        response = authorized_client.get(self.get_url())

        assert response.status_code == status.HTTP_200_OK
        assert response.data == self._serialize_profile(user, [])

    def test_get_profile_with_registrations(
        self,
        user,
        authorized_client,
        django_assert_num_queries,
    ):
        """Тест получения профиля с регистрациями."""

        registrations = RegistrationFactory.create_batch(12, user=user)
        another_user_registration = RegistrationFactory.create()
        created_at = timezone.now()

        for index, registration in enumerate(registrations):
            registration.created_at = created_at + timedelta(minutes=index)
            Registration.objects.filter(pk=registration.pk).update(
                created_at=registration.created_at
            )

        Registration.objects.filter(pk=another_user_registration.pk).update(
            created_at=created_at + timedelta(days=1)
        )

        # 2 запроса:
        # - user
        # - prefetch registrations
        with django_assert_num_queries(2):
            response = authorized_client.get(self.get_url())

        assert response.status_code == status.HTTP_200_OK
        assert response.data == self._serialize_profile(user, list(reversed(registrations[2:])))

    def test_get_profile_without_authentication(self, unauthorized_client):
        """Тест попытки получения профиля без авторизации."""

        response = unauthorized_client.get(self.get_url())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
