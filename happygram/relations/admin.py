from django.contrib import admin

from relations.models import Relation


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ['id', 'related_type', 'from_user', 'to_user']
    list_display_links = ['id', ]
    list_filter = ['related_type', 'from_user']

