from django.db import models


class EventStatus(models.TextChoices):
    """Статусы мероприятий."""

    DRAFT = 'draft', 'Черновик'
    PUBLISHED = 'published', 'Опубликовано'
    CANCELED = 'canceled', 'Отменено'
    COMPLETED = 'completed', 'Завершено'


class RegistrationStatus(models.TextChoices):
    """Статусы регистрации на мероприятие."""

    PENDING = 'pending', 'Ожидает оплаты'
    CONFIRMED = 'confirmed', 'Подтверждена'
    CANCELED = 'canceled', 'Отменена'
    ATTENDED = 'attended', 'Посетил'
