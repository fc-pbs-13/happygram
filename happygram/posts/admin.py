from django.contrib import admin
from django.utils.safestring import mark_safe
from mptt.admin import MPTTModelAdmin

from posts.models import Comment, Post, Like, Photo


def report(modeladmin, request, queryset):
    ids = [x.id for x in queryset.all()]
    count = queryset.update(caption="하하호")
    # print("here", ids, 'count', count)


@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    list_display = ('id', 'post_id', 'user', 'contents', 'parent_id',)
    list_filter = ['post_id', 'user', 'parent_id']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'caption', 'user', 'created', 'like_count']
    list_filter = ['id', 'user', 'created', 'like_count']
    search_fields = ['caption', 'user__email', ]
    # actions = [report]
    # readonly_fields = ('like_count',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'post_id', 'user_id']
    search_fields = ['post__id', 'user__email']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'image', 'post_id']
    readonly_fields = ['headshot_image']

    def headshot_image(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.image.url,
            width=obj.image.width,
            height=obj.image.height,
        ))


class MyModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return (o.name for o in obj.tags.all())
