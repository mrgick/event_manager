from datetime import timedelta
from decimal import Decimal

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from event.models import Event, Registration, Review
from event.models.choices import EventStatus, RegistrationStatus
from user.tests.factories import UserFactory


class EventFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'Event {n}')
    description = factory.Faker('paragraph')
    start_time = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    end_time = factory.LazyAttribute(lambda event: event.start_time + timedelta(hours=2))
    address = factory.Faker('address')
    max_attendees = 100
    price = Decimal('0.00')
    owner = factory.SubFactory(UserFactory)
    status = EventStatus.PUBLISHED

    class Meta:
        model = Event


class RegistrationFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    status = RegistrationStatus.CONFIRMED
    bonus_used = False

    class Meta:
        model = Registration


class ReviewFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    rating = factory.Faker('pyint', min_value=1, max_value=5)
    text = factory.Faker('paragraph')

    class Meta:
        model = Review
