from django.contrib import admin

from event.models import Event, Registration, Review


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'owner',
    ]


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'event',
    ]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'event',
        'rating',
    ]
