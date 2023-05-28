from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class UserAdmin(UserAdmin):
    list_display = (
        'pk', 'username', 'confirmation_code', 'email', 'role',
        'is_superuser', 'bio', 'first_name', 'last_name',
    )
    list_editable = ('role',)
    search_fields = ('username', 'role',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
