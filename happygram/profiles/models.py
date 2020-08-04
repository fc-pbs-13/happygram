from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from relations.models import Relation


def profile_img_path(instance, filename):
    return f'profile_img/{instance.user_id}/{filename}'


class Profile(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    introduce = models.CharField(max_length=200, null=True)
    image = models.ImageField(upload_to=profile_img_path, null=True, blank=True)
    following = models.PositiveIntegerField(default=0)
    follower = models.PositiveIntegerField(default=0)


@receiver(post_save, sender=Relation)
def relation_create(sender, **kwargs):
    obj = kwargs['instance']
    # from_user +1
    from_user_profile = Profile.objects.get(user=obj.from_user_id)
    from_user_profile.following += 1
    from_user_profile.save()
    # to_user +1
    to_user_profile = Profile.objects.get(user=obj.to_user_id)
    to_user_profile.follower += 1
    to_user_profile.save()


@receiver(post_delete, sender=Relation)
def relation_delete(sender, **kwargs):
    obj = kwargs['instance']
    # from_user -1
    from_user_profile = Profile.objects.get(user=obj.from_user_id)
    from_user_profile.following -= 1
    from_user_profile.save()
    # to_user -1
    to_user_profile = Profile.objects.get(user=obj.to_user_id)
    to_user_profile.follower -= 1
    to_user_profile.save()
