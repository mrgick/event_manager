from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'phone_number',
        'bonus_balance',
        'is_staff',
        'is_active',
    )
