from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from event.models import Event
from event.models.choices import EventStatus
from event.tests.factories import (
    EventFactory,
    RegistrationFactory,
    ReviewFactory,
)


@pytest.mark.django_db
class TestEvents:
    def get_list_url(self):
        return reverse('events-list')

    def _serialize_event(self, event, current_attendees, average_rating, is_full):
        return {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start_time': event.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'end_time': event.end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'address': event.address,
            'max_attendees': event.max_attendees,
            'price': str(event.price),
            'owner_id': event.owner_id,
            'status': event.status,
            'created_at': event.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'updated_at': event.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'current_attendees': current_attendees,
            'average_rating': average_rating,
            'is_full': is_full,
        }

    def _serialize_create_event(self, event):
        return {
            'title': event.title,
            'description': event.description,
            'start_time': event.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'end_time': event.end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'address': event.address,
            'max_attendees': event.max_attendees,
            'price': str(event.price),
        }

    def test_event_list(self, unauthorized_client, django_assert_num_queries):
        """Тест получения списка мероприятий."""

        event1 = EventFactory.create(max_attendees=None)

        event2 = EventFactory.create(max_attendees=10)
        for rating in (2, 4, 5):  # 3.66
            ReviewFactory.create(event=event1, rating=rating)
        RegistrationFactory.create_batch(9, event=event2)  # not full

        event3 = EventFactory.create(max_attendees=3)
        ReviewFactory.create(event=event3, rating=5)  # 5
        RegistrationFactory.create_batch(3, event=event3)  # full

        # не попадет в ответ
        EventFactory.create(status=EventStatus.DRAFT)
        EventFactory.create(
            start_time=timezone.now() - timedelta(days=1), status=EventStatus.PUBLISHED
        )

        # 2 запроса
        # - events с аннотацией среднего рейтинга
        # - prefetch подтвержденных регистраций
        with django_assert_num_queries(2):
            response = unauthorized_client.get(self.get_list_url())

        assert response.status_code == status.HTTP_200_OK
        assert response.data == [
            self._serialize_event(event3, 3, 5.0, True),
            self._serialize_event(event2, 9, 0.0, False),
            self._serialize_event(event1, 0, 11 / 3, False),
        ]

    def test_event_create(self, authorized_client):
        """Тест создания мероприятия."""

        event = EventFactory.build()
        request_data = self._serialize_create_event(event)

        response = authorized_client.post(self.get_list_url(), data=request_data)

        assert response.status_code == status.HTTP_201_CREATED
        event = Event.objects.get(id=response.data['id'])
        assert request_data == self._serialize_create_event(event)
