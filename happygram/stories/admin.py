from django.contrib import admin
from django.utils.safestring import mark_safe

from stories.models import Story, StoryRead


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'created', 'user']
    list_filter = ['id', 'user', 'created']
    search_fields = ['id', 'user__email', ]
    readonly_fields = ['headshot_image']

    def headshot_image(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="{obj.image.width}" height={obj.image.height} />')


@admin.register(StoryRead)
class StoryReadAdmin(admin.ModelAdmin):
    list_display = ['id', 'story', 'user']
    list_filter = ['id', 'user', 'story']
    search_fields = ['id', 'user__email', ]
