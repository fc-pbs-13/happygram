from django.db import models


class Relation(models.Model):
    CHOICE_RELATIONS_TYPE = (
        ('f', 'follow'),
        ('b', 'block'),
    )
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
        choices=CHOICE_RELATIONS_TYPE,
        max_length=10,
    )

    class Meta:
        unique_together = (
            ('from_user', 'to_user'),
        )
