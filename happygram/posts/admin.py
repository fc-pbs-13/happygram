import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from mptt.admin import MPTTModelAdmin
from taggit.models import Tag

from posts.models import Comment, Post, Like, Photo


def report(modeladmin, request, queryset):
    ids = [x.id for x in queryset.all()]
    count = queryset.update(caption="하하호")
    print("here", ids, 'count', count)


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
    readonly_fields = ('like_count',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'post_id', 'user_id']
    search_fields = ['post__id', 'user__email']

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ['id', 'image', 'post_id']
    readonly_fields = ['headshot_image']

    def headshot_image(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.image.url,
            width=obj.image.width,
            height=obj.image.height,
        )
        )


class MyModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
