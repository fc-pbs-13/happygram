from django.contrib import admin

from profiles.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'introduce']
    list_filter = ['id', 'user']
    search_fields = ['id', 'user__email', ]
