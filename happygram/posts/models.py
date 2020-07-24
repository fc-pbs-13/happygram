from django.db import models
from model_utils.models import TimeStampedModel
from django.db.models import F
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from taggit.managers import TaggableManager


class Post(TimeStampedModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    caption = models.CharField(max_length=200)
    like_count = models.PositiveIntegerField(default=0)
    tags = TaggableManager()

    def __str__(self):
        return f'{self.id}'


def post_img_path(instance, filename):
    return f'post_img/{instance.post.user_id}/{filename}'


class Photo(models.Model):
    post = models.ForeignKey('posts.Post', related_name='img', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=post_img_path, null=True, blank=True)


class Comment(MPTTModel):
    post = models.ForeignKey('posts.Post', related_name='comments', on_delete=models.CASCADE, null=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    contents = models.CharField(max_length=200)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class MPTTMeta:
        order_insertion_by = ['-id']


class Like(models.Model):
    post = models.ForeignKey('posts.Post', related_name='post_like', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', related_name='user_like', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['post', 'user']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # like create count +1
        super().save(force_insert, force_update, using, update_fields)
        # save 이후에 update (save에서 에러 날수도 있음)
        Post.objects.filter(id=self.post.id).update(like_count=F('like_count') + 1)

    def delete(self, using=None, keep_parents=False):
        # like delete count -1
        delete = super().delete(using, keep_parents)
        Post.objects.filter(id=self.post_id).update(like_count=F('like_count') - 1)
        return delete
