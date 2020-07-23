from django.db import models


class Story(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='story_image', null=True, blank=True)
    caption = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)


class StoryRead(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    story = models.ForeignKey('stories.Story', on_delete=models.CASCADE, related_name='story_read')
