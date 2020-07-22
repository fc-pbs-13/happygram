from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from posts.models import Comment


@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    list_display = ('id', 'tree_id', 'parent', 'lft', 'rght', 'is_child_node', 'is_leaf_node', 'is_root_node')

class MyModelAdmin(admin.ModelAdmin):
    list_display = ['tag_list']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())