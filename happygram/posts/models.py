from django.contrib.postgres.fields import ArrayField
from django.db import models
from model_utils.models import TimeStampedModel
from model_utils import Choices


class Post(TimeStampedModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    # images = ArrayField(models.ImageField(upload_to='post_images'), null=True,
    #                     blank=True)  # null False 인데 테스트코드 작성으로 일단 true
    caption = models.CharField(max_length=200, blank=True)
    # like = models.ForeignKey()
    # colletions = momdels.ForeignKey()


class Photo(models.Model):
    post = models.ForeignKey('posts.Post', related_name='img', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_image', null=True, blank=True)
