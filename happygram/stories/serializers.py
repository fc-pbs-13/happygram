from rest_framework import serializers

from profiles.serializers import ProfileSerializer
from stories.models import Story


class StoryListSerializer(serializers.ModelSerializer):
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


class StoryDetailSerializer(serializers.ModelSerializer):
    """스토리 디테일"""
    read_users = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ('id', 'user', 'image', 'created', 'caption', 'read_users',)

    def get_read_users(self, obj):
        """스토리를 읽은 유저의 프로필 리스트"""
        if self.context['view'].action == 'retrieve':
            read_user = self.context['view'].read_users
            serializer = ProfileSerializer(read_user, many=True)
            return serializer.data
        return None
