from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    """Модель пользователя."""

    bonus_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Бонусный баланс',
    )

    phone_number = PhoneNumberField(
        unique=True,
        blank=True,
        null=True,
        verbose_name='Номер телефона',
    )

    class Meta(AbstractUser.Meta):
        constraints = [
            models.CheckConstraint(
                condition=Q(bonus_balance__gte=0),
                name='user_bonus_balance_non_negative',
            ),
        ]

    def __str__(self):
        return self.username
