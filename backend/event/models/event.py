from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q

from event.models.choices import EventStatus


class Event(models.Model):
    """Модель мероприятия."""

    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(max_length=5000, verbose_name='Описание')

    start_time = models.DateTimeField(verbose_name='Дата и время начала')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания')

    address = models.CharField(max_length=500, verbose_name='Местоположение')

    max_attendees = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        verbose_name='Максимальное количество участников',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Стоимость участия',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Организатор',
    )

    status = models.CharField(
        max_length=9,
        choices=EventStatus.choices,
        default=EventStatus.DRAFT,
        verbose_name='Статус',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    reminder_sent = models.BooleanField(
        default=False,
        verbose_name='Уведомления разосланы',
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        constraints = [
            models.CheckConstraint(
                condition=Q(end_time__gt=F('start_time')),
                name='event_end_after_start',
            ),
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name='event_price_non_negative',
            ),
            models.CheckConstraint(
                condition=Q(max_attendees__isnull=True) | Q(max_attendees__gt=0),
                name='event_max_attendees_positive_or_null',
            ),
        ]

    def __str__(self):
        return self.title
