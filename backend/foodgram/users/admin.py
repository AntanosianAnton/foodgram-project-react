from django.contrib import admin

from users.models import User


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    list_display = ('username', 'email', 'id')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'
    list_filter = ('username', 'email')
