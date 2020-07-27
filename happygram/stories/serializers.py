from rest_framework import serializers

from profiles.serializers import ProfileSerializer
from stories.models import Story, StoryRead


class StoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ('id', 'user', 'image', 'created', 'caption')
        read_only_fields = ('user',)


class StoryDetailSerializer(serializers.ModelSerializer):
    """스토리 디테일"""
    # read_users = serializers.SerializerMethodField()
    read_users = ProfileSerializer(source='user.profile')

    class Meta:
        model = StoryRead
        fields = ('id', 'user', 'story_id', 'read_users',)

    # def get_read_users(self, obj):
    #     """스토리를 읽은 유저의 프로필 리스트"""
    #     read_user = self.context['view'].read_users
    #     serializer = ProfileSerializer(read_user, many=True)
    #     return serializer.data
