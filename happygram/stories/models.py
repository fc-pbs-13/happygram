from django.db import models


def story_img_path(instance, filename):
    return f'story_img/{instance.user_id}/{filename}'


class Story(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=story_img_path)
    caption = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}'


class StoryRead(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    story = models.ForeignKey('stories.Story', on_delete=models.CASCADE, related_name='story_read')
