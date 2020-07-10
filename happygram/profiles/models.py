from django.db import models


class Profile(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_image', null=True, blank=True)
    introduce = models.CharField(max_length=200, null=True)
    # followings = models.ManyToManyField()
    # followers = models.ManyToManyField()
    # collections = models.ManyToManyField()
