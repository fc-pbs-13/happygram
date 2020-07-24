from django.db import models


def profile_img_path(instance, filename):
    return f'profile_img/{instance.user_id}/{filename}'


class Profile(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=profile_img_path, null=True, blank=True)
    introduce = models.CharField(max_length=200, null=True)
