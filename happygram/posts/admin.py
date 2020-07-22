from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from posts.models import Comment


@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    list_display = ('id', 'tree_id', 'parent', 'lft', 'rght', 'is_child_node', 'is_leaf_node', 'is_root_node')

