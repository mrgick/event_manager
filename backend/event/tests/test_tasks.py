from datetime import timedelta

import pytest
from django.utils import timezone

from event.models.choices import RegistrationStatus
from event.tasks import send_event_reminders
from event.tests.factories import EventFactory, RegistrationFactory


@pytest.mark.django_db
def test_send_event_reminders(monkeypatch, capsys):
    now = timezone.now()
    monkeypatch.setattr('event.tasks.timezone.now', lambda: now)

    event = EventFactory.create(
        start_time=now + timedelta(days=1, minutes=30),
        end_time=now + timedelta(days=1, hours=2),
    )
    confirmed_registration = RegistrationFactory.create(event=event)
    canceled_registration = RegistrationFactory.create(
        event=event,
        status=RegistrationStatus.CANCELED,
    )
    event_outside_reminder_window = EventFactory.create(
        start_time=now + timedelta(days=2),
        end_time=now + timedelta(days=2, hours=2),
    )

    notifications_sent = send_event_reminders.run()

    event.refresh_from_db()
    event_outside_reminder_window.refresh_from_db()
    output = capsys.readouterr().out

    assert notifications_sent == 1
    assert event.reminder_sent is True
    assert event_outside_reminder_window.reminder_sent is False
    assert confirmed_registration.user.email in output
    assert canceled_registration.user.email not in output
