from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from config import celery_app
from event.models import Event
from event.models.choices import RegistrationStatus


@celery_app.task
def send_event_reminders() -> int:
    window_start = timezone.now() + timedelta(days=1)
    window_end = window_start + timedelta(hours=1)
    event_ids = (
        Event.objects.filter(
            start_time__gte=window_start,
            start_time__lt=window_end,
            reminder_sent=False,
        )
        .order_by('pk')
        .values_list('pk', flat=True)
    )

    notifications_sent = 0
    for event_id in event_ids.iterator():
        with transaction.atomic():
            event = (
                Event.objects.select_for_update()
                .filter(
                    pk=event_id,
                    start_time__gte=window_start,
                    start_time__lt=window_end,
                    reminder_sent=False,
                )
                .first()
            )
            if event is None:
                continue

            registrations = event.registrations.filter(
                status=RegistrationStatus.CONFIRMED,
            ).select_related('user')
            for registration in registrations.iterator():
                print(f'Notify {registration.user.email} about {event.title}')  # noqa: T201
                notifications_sent += 1

            event.reminder_sent = True
            event.save(update_fields=('reminder_sent',))

    return notifications_sent
