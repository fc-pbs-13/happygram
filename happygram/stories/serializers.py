from rest_framework import serializers

from stories.models import Story


class StorySerializer(serializers.ModelSerializer):
    story_read_id = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ('id', 'user', 'image', 'created', 'caption', 'story_read_id',)
        read_only_fields = ('user',)

    def get_story_read_id(self, obj):
        """ request user가 read한 스토리는 story_read_id가 보인다   """
        if self.context['view'].action == 'list':
            story_read_id = self.context['view'].story_read.get(obj.id)
            return story_read_id
        return None
