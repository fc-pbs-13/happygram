from django.contrib.postgres.fields import ArrayField
from django.db import models
from model_utils.models import TimeStampedModel
from django.db.models import F
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Post(TimeStampedModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    # images = ArrayField(models.ImageField(upload_to='post_images'), null=True,
    #                     blank=True)  # null False 인데 테스트코드 작성으로 일단 true다->>>> 일단 photo모델로 만들었
    caption = models.CharField(max_length=200, blank=True)
    like_count = models.PositiveIntegerField(default=0)
    # colletions = momdels.ForeignKey


class Photo(models.Model):
    post = models.ForeignKey('posts.Post', related_name='img', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_image', null=True, blank=True)


class Comment(MPTTModel):
    # todo reply create할 때 post - null true -> safe? (Admin) / false -> 시리얼라이저에 reply까지 다 불러온다
    post = models.ForeignKey('posts.Post', related_name='comments', on_delete=models.CASCADE, null=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    contents = models.CharField(max_length=200)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="children")


class Like(models.Model):
    post = models.ForeignKey('posts.Post', related_name='post_like', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', related_name='user_like', on_delete=models.CASCADE)


    class Meta:
        unique_together = ['post', 'user']
