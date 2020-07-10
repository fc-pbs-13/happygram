from django.contrib.postgres.fields import ArrayField
from django.db import models


class Post(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    images = ArrayField(models.ImageField(upload_to='post_images'), null=True, blank=True)# null False 인데 테스트코드 작성으로 일단 true
    caption = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    # like = models.ForeignKey()
    # colletions = momdels.ForeignKey()
