from django.contrib import admin

from stories.models import Story, StoryRead


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'created', 'user']
    list_filter = ['id', 'user', 'created']
    search_fields = ['id', 'user__email', ]


@admin.register(StoryRead)
class StoryReadAdmin(admin.ModelAdmin):
    list_display = ['id', 'story', 'user']
    list_filter = ['id', 'user', 'story']
    search_fields = ['id', 'user__email', ]
