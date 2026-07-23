from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from event.models.event import Event


class Review(models.Model):
    """Модель отзыва пользователя."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Пользователь',
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Мероприятие',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Рейтинг',
    )
    text = models.TextField(verbose_name='Текст отзыва')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'event'),
                name='unique_user_event_review',
            ),
            models.CheckConstraint(
                condition=Q(rating__gte=1, rating__lte=5),
                name='review_rating_between_1_and_5',
            ),
        ]

    def __str__(self):
        return f'{self.user} — {self.event}: {self.rating}'
