from django.conf import settings
from django.db import models

from event.models.choices import RegistrationStatus
from event.models.event import Event


class Registration(models.Model):
    """Модель регистрации пользователя на мероприятие."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='Пользователь',
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='Мероприятие',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации',
    )
    status = models.CharField(
        max_length=9,
        choices=RegistrationStatus,
        default=RegistrationStatus.PENDING,
        verbose_name='Статус регистрации',
    )
    bonus_used = models.BooleanField(
        default=False,
        verbose_name='Использованы бонусы',
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Регистрация'
        verbose_name_plural = 'Регистрации'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'event'),
                name='unique_user_event_registration',
            ),
        ]

    def __str__(self):
        return f'{self.user} — {self.event}'
