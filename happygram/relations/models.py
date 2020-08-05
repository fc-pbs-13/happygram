from django.db import models
from django.db.models import F
from django_lifecycle import LifecycleModel, hook, AFTER_SAVE, AFTER_CREATE, AFTER_UPDATE, AFTER_DELETE

from profiles.models import Profile


class Relation(LifecycleModel):
    class RelationChoice(models.TextChoices):
        FOLLOW = 'FOLLOW'
        BLOCK = 'BLOCK'

    from_user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='from_user_relations',
        related_query_name='from_users_relation',
    )
    to_user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='to_user_relations',
        related_query_name='to_users_relation',
    )
    related_type = models.CharField(
        choices=RelationChoice.choices,
        max_length=10,
    )

    class Meta:
        unique_together = (
            ('from_user', 'to_user'),
        )

    @hook(AFTER_CREATE)
    def create_follow(self):
        Profile.objects.filter(user_id=self.from_user_id).update(following=F('following') + 1)
        Profile.objects.filter(user_id=self.to_user).update(follower=F('follower') + 1)

    @hook(AFTER_UPDATE)
    def update_follow(self):
        if self.related_type == 'FOLLOW':
            Profile.objects.filter(user_id=self.from_user_id).update(following=F('following') + 1)
            Profile.objects.filter(user_id=self.to_user).update(follower=F('follower') + 1)

        elif self.related_type == 'BLOCK':
            Profile.objects.filter(user_id=self.from_user_id).update(following=F('following') - 1)
            Profile.objects.filter(user_id=self.to_user).update(follower=F('follower') - 1)

    @hook(AFTER_DELETE)
    def delete_follow(self):
        Profile.objects.filter(user_id=self.from_user_id).update(following=F('following') - 1)
        Profile.objects.filter(user_id=self.to_user).update(follower=F('follower') - 1)
