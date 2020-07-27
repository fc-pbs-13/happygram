from django.contrib import admin
from django.utils.safestring import mark_safe

from profiles.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'introduce']
    list_filter = ['id', 'user']
    search_fields = ['id', 'user__email', ]
    readonly_fields = ['headshot_image']

    def headshot_image(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="{obj.image.width}" height={obj.image.height} />')
