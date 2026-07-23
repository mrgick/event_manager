from django.db.models import (
    BooleanField,
    Case,
    Count,
    F,
    Prefetch,
    Q,
    QuerySet,
    Value,
    When,
)
from django.utils import timezone

from event.models import Event, Review
from event.models.choices import EventStatus, RegistrationStatus


class EventListService:
    """Сервис получения списка мероприятий."""

    def execute(self) -> list[Event]:
        events = list(self._get_queryset())
        self._set_average_rating(events)
        return events

    def _get_queryset(self) -> QuerySet[Event]:
        reviews = Review.objects.order_by().only('event_id', 'rating')

        return (
            Event.objects.filter(
                status=EventStatus.PUBLISHED,
                end_time__gt=timezone.now(),
            )
            .annotate(
                current_attendees=Count(
                    'registrations',
                    filter=Q(registrations__status=RegistrationStatus.CONFIRMED),
                ),
            )
            .annotate(
                is_full=Case(
                    When(max_attendees__isnull=True, then=Value(False)),
                    When(
                        max_attendees__lte=F('current_attendees'),
                        then=Value(True),
                    ),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
            .order_by('-created_at')
            .prefetch_related(
                Prefetch(
                    'reviews',
                    queryset=reviews,
                    to_attr='prefetched_reviews',
                )
            )
        )

    def _set_average_rating(self, events: list[Event]) -> None:
        for event in events:
            ratings = [review.rating for review in event.prefetched_reviews]
            event.average_rating = sum(ratings) / len(ratings) if ratings else 0.0
